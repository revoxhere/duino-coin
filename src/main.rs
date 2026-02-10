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

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut config = Config::default();

    config.load_from_file("config.toml")?;

    // Connect to DB
    master_server::db::connect(
        &config.database_ip,
        config.database_port,
        &config.database_user,
        &config.database_password,
        &config.database_name,
    )
    .await?;

    // Start CLI
    master_server::cli::run().await?;

    Ok(())
}
