// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use sqlx::{Pool, Postgres, postgres::PgPoolOptions};
use std::sync::OnceLock;

static DB_POOL: OnceLock<Pool<Postgres>> = OnceLock::new();

pub async fn connect(
    host: &str,
    port: u16,
    user: &str,
    password: &str,
    database: &str,
) -> Result<(), sqlx::Error> {
    let url = format!(
        "postgres://{}:{}@{}:{}/{}",
        user, password, host, port, database
    );

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&url)
        .await?;

    DB_POOL.set(pool).expect("DB already initialized");

    Ok(())
}

pub fn pool() -> &'static Pool<Postgres> {
    DB_POOL.get().expect("DB not initialized")
}
