// backend/src/main.rs - DYNAMIC BRIDGE MODE (FULL FEATURES)
use actix_web::{web, App, HttpServer};
use actix_cors::Cors;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use std::io::{BufRead, BufReader, Write};
use std::thread;
use std::time::Duration;
use std::net::TcpListener;
use std::sync::mpsc::{channel, Sender};
use serialport::SerialPort;
use influxdb2::Client;

// ===== KONFIGURASI =====
const ARDUINO_WIFI_ADDR: &str = "0.0.0.0:8081"; // Input Data (WiFi)
const GUI_CMD_ADDR: &str = "0.0.0.0:8082";      // Input Command (Python)
const GUI_DATA_ADDR: &str = "0.0.0.0:8083";     // Output Data (Python)
const HTTP_PORT: u16 = 8080;                    // Web Server Status
const BAUD_RATE: u32 = 9600;

// InfluxDB Config
const INFLUXDB_URL: &str = "http://localhost:8086";
const INFLUXDB_ORG: &str = "its_instrumentasi";
const INFLUXDB_BUCKET: &str = "electronic_nose";
const INFLUXDB_TOKEN: &str = "electronic_nose_token";

// ===== STRUKTUR DATA =====
#[derive(Serialize, Deserialize, Clone, Debug)]
struct SensorData {
    timestamp: u64,
    no2: f64, eth: f64, voc: f64, co: f64,
    co_mics: f64, eth_mics: f64, voc_mics: f64,
    state: i32, level: i32,
    state_name: String,
}

struct AppState {
    gui_broadcast: Arc<Mutex<Vec<Sender<String>>>>,
    serial_port: Arc<Mutex<Option<Box<dyn SerialPort>>>>, // Serial Dinamis
    influxdb_client: Arc<Client>,
}

fn parse_sensor_line(line: &str) -> Option<SensorData> {
    if !line.starts_with("SENSOR:") { return None; }
    let content = line.trim_start_matches("SENSOR:");
    let parts: Vec<&str> = content.split(',').collect();
    
    if parts.len() < 9 { return None; }
    
    let p = |s: &str| s.trim().parse::<f64>().unwrap_or(0.0);
    let pi = |s: &str| s.trim().parse::<i32>().unwrap_or(0);
    
    let state_idx = pi(parts[7]);
    let state_names = vec!["IDLE", "PRE-COND", "RAMP_UP", "HOLD", "PURGE", "RECOVERY", "DONE"];
    let state_str = if state_idx >= 0 && (state_idx as usize) < state_names.len() {
        state_names[state_idx as usize].to_string()
    } else { "UNKNOWN".to_string() };

    Some(SensorData {
        timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis() as u64,
        no2: p(parts[0]), eth: p(parts[1]), voc: p(parts[2]), co: p(parts[3]),
        co_mics: p(parts[4]), eth_mics: p(parts[5]), voc_mics: p(parts[6]),
        state: state_idx, level: pi(parts[8]), state_name: state_str,
    })
}

// 1. RECEIVER ARDUINO (WIFI 8081)
fn start_arduino_receiver(state: web::Data<AppState>) {
    thread::spawn(move || {
        let listener = TcpListener::bind(ARDUINO_WIFI_ADDR).expect("Failed to bind Arduino port");
        println!("📡 Listening for Arduino Data on {}", ARDUINO_WIFI_ADDR);
        
        for stream in listener.incoming() {
            if let Ok(stream) = stream {
                let state = state.clone();
                thread::spawn(move || {
                    let reader = BufReader::new(stream);
                    for line in reader.lines() {
                        if let Ok(l) = line {
                            if let Some(data) = parse_sensor_line(&l) {
                                // A. Broadcast ke GUI (JSON)
                                if let Ok(json_str) = serde_json::to_string(&data) {
                                    if let Ok(mut clients) = state.gui_broadcast.lock() {
                                        clients.retain(|tx| tx.send(json_str).is_ok());
                                    }
                                }
                                
                                // B. Simpan ke InfluxDB
                                let client = state.influxdb_client.clone();
                                let d = data.clone();
                                thread::spawn(move || {
                                    let rt = tokio::runtime::Runtime::new().unwrap();
                                    rt.block_on(async {
                                        let point = influxdb2::models::DataPoint::builder("sensor_reading")
                                            .tag("device", "arduino_uno_r4").tag("state", &d.state_name)
                                            .field("no2", d.no2).field("eth", d.eth).field("voc", d.voc).field("co", d.co)
                                            .field("co_mics", d.co_mics).field("eth_mics", d.eth_mics).field("voc_mics", d.voc_mics)
                                            .field("level", d.level as i64)
                                            .build();
                                        if let Ok(p) = point { let _ = client.write(INFLUXDB_BUCKET, futures::stream::iter(vec![p])).await; }
                                    });
                                });
                            }
                        }
                    }
                });
            }
        }
    });
}

// 2. GUI COMMAND RECEIVER (TCP 8082 -> SERIAL USB)
fn start_gui_cmd_receiver(state: web::Data<AppState>) {
    thread::spawn(move || {
        let listener = TcpListener::bind(GUI_CMD_ADDR).expect("Failed to bind CMD port");
        println!("🎛️  GUI Command Receiver ready on {}", GUI_CMD_ADDR);
        
        for stream in listener.incoming() {
            if let Ok(stream) = stream {
                let state = state.clone();
                thread::spawn(move || {
                    let reader = BufReader::new(stream);
                    for line in reader.lines() {
                        if let Ok(cmd_raw) = line {
                            let cmd = cmd_raw.trim().to_string();
                            println!("📥 CMD: {}", cmd);

                            // --- LOGIKA KONEKSI DINAMIS ---
                            if cmd.starts_with("CONNECT_SERIAL") {
                                // Format: "CONNECT_SERIAL COM3"
                                let parts: Vec<&str> = cmd.split_whitespace().collect();
                                if parts.len() >= 2 {
                                    let port_name = parts[1];
                                    println!("🔌 Request to open serial: {}", port_name);
                                    
                                    match serialport::new(port_name, BAUD_RATE).timeout(Duration::from_millis(100)).open() {
                                        Ok(p) => {
                                            let mut port_guard = state.serial_port.lock().unwrap();
                                            *port_guard = Some(p);
                                            println!("✅ Serial Connected to {}", port_name);
                                        },
                                        Err(e) => println!("❌ Failed to open {}: {}", port_name, e),
                                    }
                                }
                            }
                            else if cmd == "DISCONNECT_SERIAL" {
                                let mut port_guard = state.serial_port.lock().unwrap();
                                *port_guard = None;
                                println!("🔌 Serial Disconnected");
                            }
                            else {
                                // Perintah biasa (START_SAMPLING / STOP_SAMPLING) diteruskan ke Arduino
                                let mut port_guard = state.serial_port.lock().unwrap();
                                if let Some(port) = port_guard.as_mut() {
                                    let cmd_str = format!("{}\n", cmd);
                                    if let Err(e) = port.write_all(cmd_str.as_bytes()) {
                                        println!("❌ Serial Write Error: {}", e);
                                    } else {
                                        println!("➡️ Forwarded to Arduino: {}", cmd);
                                    }
                                } else {
                                    println!("⚠️ Serial not connected! Cannot send: {}", cmd);
                                }
                            }
                        }
                    }
                });
            }
        }
    });
}

// 3. GUI DATA BROADCASTER (TCP 8083 OUT)
fn start_gui_broadcaster(state: web::Data<AppState>) {
    thread::spawn(move || {
        let listener = TcpListener::bind(GUI_DATA_ADDR).expect("Failed to bind Data port");
        println!("💻 GUI Data Output ready on {}", GUI_DATA_ADDR);
        for stream in listener.incoming() {
            if let Ok(mut stream) = stream {
                let (tx, rx) = channel();
                if let Ok(mut clients) = state.gui_broadcast.lock() {
                     clients.push(tx);
                }
                thread::spawn(move || {
                    while let Ok(msg) = rx.recv() {
                        if stream.write_all(format!("{}\n", msg).as_bytes()).is_err() { break; }
                    }
                });
            }
        }
    });
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("🚀 STARTING E-NOSE BACKEND (DYNAMIC BRIDGE MODE)");
    
    let client = Client::new(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_TOKEN);
    let state = web::Data::new(AppState {
        gui_broadcast: Arc::new(Mutex::new(Vec::new())),
        serial_port: Arc::new(Mutex::new(None)), // Awalnya Kosong, menunggu Python
        influxdb_client: Arc::new(client),
    });

    start_arduino_receiver(state.clone());
    start_gui_cmd_receiver(state.clone());
    start_gui_broadcaster(state.clone());

    HttpServer::new(move || {
        App::new().app_data(state.clone()).route("/", web::get().to(|| async { "E-Nose Ready" }))
    })
    .bind(("0.0.0.0", HTTP_PORT))?
    .run()
    .await
}