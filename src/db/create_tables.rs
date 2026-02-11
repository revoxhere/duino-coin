// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

pub async fn run() -> Result<(), sqlx::Error> {
    let pool = crate::db::pool();

    // Transactions
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Transactions (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                username TEXT,
                recipient TEXT,
                amount REAL,
                hash TEXT,
                memo TEXT,
                ip_addr TEXT
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Cards
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Cards (
                timestamp REAL,
                username TEXT,
                value REAL,
                key TEXT UNIQUE
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Blocks
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Blocks (
                timestamp TEXT,
                finder TEXT,
                amount REAL,
                hash TEXT
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Limits
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Limits (
                username TEXT,
                exlimit REAL,
                last REAL
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Users
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Users (
                username TEXT,
                password TEXT,
                email TEXT,
                balance REAL,
                created TEXT DEFAULT 'before 23.08.2021',
                rig_verified TEXT DEFAULT 'No',
                last_seen INTEGER DEFAULT 0,
                stake INTEGER DEFAULT 0,
                warnings INTEGER DEFAULT 0,
                ban_reason TEXT DEFAULT 'None',
                ban INTEGER DEFAULT 0,
                max_miners INTEGER DEFAULT 2,
                reg_country TEXT DEFAULT 'None',
                trustscore INTEGER DEFAULT 0,
                miner_password INTEGER,
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Server
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Server (
                blocks REAL,
                lastBlockHash TEXT
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Pools
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS Pools (
                identifier TEXT,
                name TEXT,
                url TEXT,
                cpu REAL,
                ram REAL,
                connections INTEGER,
                lastsync INTEGER,
                hidden BOOLEAN DEFAULT 0,
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Alt Accounts
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS alt_accounts (
                ip_addr TEXT,
                usernames TEXT,
                change INTEGER,
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Chain Alts
    sqlx::query(
        r#"
            CREATE TABLE IF NOT EXISTS chain_accounts(
                address TEXT,
                username TEXT,
            )
        "#,
    )
    .execute(pool)
    .await?;

    // Initial block
    sqlx::query(
        r#"
            INSERT INTO Server (blocks, lastBlockHash)
            SELECT 1, 'ba29a15896fd2d792d5c4b60668bf2b9feebc51d'
            WHERE NOT EXISTS (SELECT 1 FROM Server)
        "#,
    )
    .execute(pool)
    .await?;

    Ok(())
}
