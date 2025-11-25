use chrono::{DateTime, Utc};
use futures::{SinkExt, StreamExt};
use influxdb2::Client;
use influxdb2::models::DataPoint;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::broadcast;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

// Struktur data Sensor
#[derive(Debug, Serialize, Deserialize, Clone)]
struct SensorData {
    timestamp: DateTime<Utc>,
    no2: f64,
    eth: f64,
    voc: f64,
    co: f64,
    co_mics: f64,
    eth_mics: f64,
    voc_mics: f64,
    state: String,
    level: i32,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 Starting E-Nose Backend System (Bidirectional)...");

    // Ganti Token InfluxDB jika perlu
    let db_client = Arc::new(Client::new("http://localhost:8086", "its_instrumentasi", "electronic_nose_token"));

    // Channel 1: Broadcast Data Sensor (Arduino -> Frontend)
    let (tx_sensor, _rx_sensor) = broadcast::channel::<String>(100);
    
    // Channel 2: Broadcast Command (Frontend -> Arduino)
    let (tx_cmd, _rx_cmd) = broadcast::channel::<String>(100);

    let arduino_listener = TcpListener::bind("0.0.0.0:8081").await?;
    let frontend_listener = TcpListener::bind("0.0.0.0:8082").await?;

    println!("📡 Listening for Arduino on port 8081");
    println!("💻 Listening for Frontend on port 8082");

    // --- FRONTEND HANDLER ---
    let tx_sensor_clone = tx_sensor.clone();
    let tx_cmd_clone = tx_cmd.clone();
    
    tokio::spawn(async move {
        loop {
            if let Ok((socket, addr)) = frontend_listener.accept().await {
                println!("💻 Frontend Connected: {}", addr);
                let mut rx_sensor = tx_sensor_clone.subscribe();
                let tx_cmd = tx_cmd_clone.clone();

                tokio::spawn(async move {
                    let (reader, mut writer) = socket.into_split();
                    let mut line_reader = BufReader::new(reader).lines();

                    loop {
                        tokio::select! {
                            // 1. Kirim Data Sensor ke Frontend
                            Ok(msg) = rx_sensor.recv() => {
                                if writer.write_all(msg.as_bytes()).await.is_err() || writer.write_all(b"\n").await.is_err() {
                                    break;
                                }
                            }
                            // 2. Baca Command dari Frontend
                            Ok(Some(line)) = line_reader.next_line() => {
                                println!("Command from UI: {}", line);
                                let _ = tx_cmd.send(line); // Broadcast ke Arduino Handler
                            }
                            // Jika koneksi putus
                            else => break,
                        }
                    }
                    println!("💻 Frontend Disconnected");
                });
            }
        }
    });

    // --- ARDUINO HANDLER ---
    loop {
        let (socket, addr) = arduino_listener.accept().await?;
        println!("🔌 Arduino Connected: {}", addr);
        
        let db_client = db_client.clone();
        let tx_sensor = tx_sensor.clone();
        let mut rx_cmd = tx_cmd.subscribe();

        tokio::spawn(async move {
            let (reader, mut writer) = socket.into_split();
            let mut line_reader = BufReader::new(reader).lines();

            loop {
                tokio::select! {
                    // 1. Baca Data Sensor dari Arduino
                    Ok(Some(line)) = line_reader.next_line() => {
                         if line.starts_with("SENSOR:") {
                            process_sensor_data(&line, &db_client, &tx_sensor).await;
                         }
                    }
                    // 2. Kirim Command ke Arduino (Jika ada dari UI)
                    Ok(cmd) = rx_cmd.recv() => {
                        println!("Forwarding to Arduino: {}", cmd);
                        if writer.write_all(cmd.as_bytes()).await.is_err() || writer.write_all(b"\n").await.is_err() {
                            break;
                        }
                    }
                    else => break,
                }
            }
            println!("🔌 Arduino Disconnected");
        });
    }
}

async fn process_sensor_data(line: &str, db_client: &Arc<Client>, tx: &broadcast::Sender<String>) {
    let content = line.trim_start_matches("SENSOR:");
    let parts: Vec<&str> = content.split(',').collect();

    if parts.len() >= 9 {
        let data = SensorData {
            timestamp: Utc::now(),
            no2: parts[0].parse().unwrap_or(-1.0),
            eth: parts[1].parse().unwrap_or(-1.0),
            voc: parts[2].parse().unwrap_or(-1.0),
            co: parts[3].parse().unwrap_or(-1.0),
            co_mics: parts[4].parse().unwrap_or(0.0),
            eth_mics: parts[5].parse().unwrap_or(0.0),
            voc_mics: parts[6].parse().unwrap_or(0.0),
            state: parts[7].parse().unwrap_or("UNKNOWN".to_string()),
            level: parts[8].parse().unwrap_or(0),
        };

        // Kirim ke Frontend
        if let Ok(json_str) = serde_json::to_string(&data) {
            let _ = tx.send(json_str);
        }

        // Simpan ke DB
        let point = DataPoint::builder("sensor_reading")
            .tag("source", "arduino_uno_r4")
            .tag("state", &data.state)
            .field("no2", data.no2)
            .field("eth", data.eth)
            .field("voc", data.voc)
            .field("co", data.co)
            .field("co_mics", data.co_mics)
            .field("level", data.level as i64)
            .build();

        if let Ok(p) = point {
            let _ = db_client.write("electronic_nose", futures::stream::iter(vec![p])).await;
        }
    }
}