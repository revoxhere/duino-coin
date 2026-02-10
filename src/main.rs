// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use master_server::types::Config;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut config = Config::default();

    config.load_from_file("config.toml")?;

    // Start CLI
    master_server::cli::run()?;

    Ok(())
}
