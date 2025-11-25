use chrono::{DateTime, Utc};
use futures::SinkExt;
use influxdb2::Client;
use influxdb2::models::DataPoint;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::broadcast;
use tokio_util::codec::{Framed, LinesCodec};
use futures::StreamExt;

// Struktur data yang dikirim ke Frontend & InfluxDB
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
    println!("🚀 Starting E-Nose Backend System...");

    // Setup InfluxDB Client
    let db_client = Arc::new(Client::new("http://localhost:8086", "its_instrumentasi", "electronic_nose_token")); // Ganti token sesuai setup InfluxDB UI nanti

    // Channel untuk broadcast data dari Arduino -> Semua Frontend Client
    let (tx, _rx) = broadcast::channel::<String>(100);

    // 1. Listener untuk Arduino (Port 8081 sesuai embedded/main.ino)
    let arduino_listener = TcpListener::bind("0.0.0.0:8081").await?;
    println!("📡 Listening for Arduino on port 8081");

    // 2. Listener untuk Frontend Python (Port 8082)
    let frontend_listener = TcpListener::bind("0.0.0.0:8082").await?;
    println!("💻 Listening for Frontend on port 8082");

    // Spawn Task: Handle Frontend Connections
    let tx_frontend = tx.clone();
    tokio::spawn(async move {
        loop {
            if let Ok((socket, addr)) = frontend_listener.accept().await {
                println!("💻 New Frontend connected: {}", addr);
                let mut rx = tx_frontend.subscribe();
                tokio::spawn(async move {
                    let mut lines = Framed::new(socket, LinesCodec::new());
                    while let Ok(msg) = rx.recv().await {
                        if lines.send(msg).await.is_err() {
                            break; // Client disconnect
                        }
                    }
                });
            }
        }
    });

    // Main Loop: Handle Arduino Connections
    loop {
        let (socket, addr) = arduino_listener.accept().await?;
        println!("🔌 Arduino connected: {}", addr);
        let db_client = db_client.clone();
        let tx = tx.clone();

        tokio::spawn(async move {
            handle_arduino(socket, db_client, tx).await;
        });
    }
}

async fn handle_arduino(socket: TcpStream, db_client: Arc<Client>, tx: broadcast::Sender<String>) {
    let mut lines = Framed::new(socket, LinesCodec::new());

    while let Some(result) = lines.next().await {
        match result {
            Ok(line) => {
                // Parsing logic sesuai format Arduino: "SENSOR:val,val,..."
                // Referensi: embedded/main.ino
                if line.starts_with("SENSOR:") {
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
                            state: parts[7].parse().unwrap_or("UNKNOWN".to_string()), // Enum State string
                            level: parts[8].parse().unwrap_or(0),
                        };

                        // 1. Kirim ke Frontend (JSON)
                        if let Ok(json_str) = serde_json::to_string(&data) {
                            let _ = tx.send(json_str);
                        }

                        // 2. Simpan ke InfluxDB
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
            }
            Err(_) => break,
        }
    }
}