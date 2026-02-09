// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("failed to read config file: {0}")]
    Io(#[from] std::io::Error),
    #[error("failed to parse config file: {0}")]
    Toml(#[from] toml::de::Error),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub host: String,
    pub ports: Vec<u16>,
    pub database_ip: String,
    pub database_port: u16,
    pub database_name: String,
    pub database_user: String,
    pub database_password: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            host: "0.0.0.0".to_string(),
            ports: vec![
                2806, // Pools
                2807, // Pools
                2808, // Pools
                2809, // Pools
                2810, // Pools
                2811, // General purpose
                2812, // General purpose
                2813, // General purpose
                2814, // General purpose
                2815, // General purpose
            ],
            database_ip: "127.0.0.1".to_string(),
            database_port: 5432,
            database_name: "duco".to_string(),
            database_user: "root".to_string(),
            database_password: "".to_string(),
        }
    }
}
