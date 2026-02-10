// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use std::time::Instant;
use sysinfo::System;

pub struct App {
    pub server_connections: u32,
    pub server_rps: f64,
    pub server_errors: u32,
    pub server_data_up: u64,
    pub server_data_down: u64,

    pub pool_workers: u32,
    pub pool_hashrate: f64,
    pub pool_blocks: u32,
    pub pool_shares_good: u32,
    pub pool_shares_bad: u32,

    pub users_active: u32,
    pub users_total: u32,
    pub users_new_today: u32,
    pub users_verified: u32,

    pub logs: Vec<String>,
    pub input: String,

    pub sys: System,
    pub cpu_usage: Vec<f64>,
    pub mem_usage: Vec<f64>,

    pub connections: Vec<ConnectionInfo>,

    pub last_tick: Instant,
    pub should_quit: bool,
}

pub struct ConnectionInfo {
    pub name: String,
    pub ip: String,
    pub port: u16,
    pub status: String,
    pub sent: String,
    pub received: String,
    pub uptime: String,
}

impl Default for App {
    fn default() -> Self {
        let sys = System::new();

        Self {
            sys,
            server_connections: 0,
            server_rps: 0.0,
            server_errors: 0,
            server_data_up: 0,
            server_data_down: 0,

            pool_workers: 0,
            pool_hashrate: 0.0,
            pool_blocks: 0,
            pool_shares_good: 0,
            pool_shares_bad: 0,

            users_active: 0,
            users_total: 0,
            users_new_today: 0,
            users_verified: 0,

            logs: vec!["TCP Server Listening on 127.0.0.1:4000".to_string()],
            input: String::new(),

            cpu_usage: vec![0.0; 20],
            mem_usage: vec![0.0; 20],

            connections: Vec::new(),

            last_tick: Instant::now(),
            should_quit: false,
        }
    }
}

impl App {
    pub fn on_tick(&mut self) {
        self.sys.refresh_cpu_usage();
        self.sys.refresh_memory();

        self.cpu_usage.remove(0);
        self.cpu_usage.push(self.sys.global_cpu_usage() as f64);

        self.mem_usage.remove(0);
        self.mem_usage
            .push(self.sys.used_memory() as f64 / self.sys.total_memory() as f64 * 100.0);
    }
}
