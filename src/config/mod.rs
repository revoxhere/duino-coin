// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use crate::types::{Config, ConfigError};
use std::path::PathBuf;

impl Config {
    pub fn load_from_file(&mut self, path: &str) -> Result<(), ConfigError> {
        let config_path = PathBuf::from(path);
        let config_content = std::fs::read_to_string(config_path)?;
        let config: Config = toml::from_str(&config_content)?;
        *self = config;
        Ok(())
    }
}
