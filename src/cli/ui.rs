// ===============================================================
// Duino-Coin Master Server
//
// https://duinocoin.com
//
// Copyright (c) 2019-2026 Duino-Coin Team & Community
//
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// ===============================================================

use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Row, Sparkline, Table, Wrap},
};

use crate::cli::App;

pub fn render(f: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(6),  // Top row info
            Constraint::Min(10),    // Middle row (Input & Logs)
            Constraint::Length(10), // Bottom row (Table & Graphs)
        ])
        .split(f.area());

    // --- TOP ROW ---
    let top_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(33),
            Constraint::Percentage(33),
            Constraint::Percentage(34),
        ])
        .split(chunks[0]);

    // Server Info
    let server_info = vec![
        Line::from(vec![
            Span::raw("Connections: "),
            Span::styled(
                format!("{}", app.server_connections),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("RPS: "),
            Span::styled(
                format!("{:.1}", app.server_rps),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Errors: "),
            Span::styled(
                format!("{}", app.server_errors),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Data ↑↓: "),
            Span::styled(
                format!("{} B / {} B", app.server_data_up, app.server_data_down),
                Style::default().fg(Color::Yellow),
            ),
        ]),
    ];
    let server_block = Block::default().borders(Borders::ALL).title("Server");
    f.render_widget(
        Paragraph::new(server_info).block(server_block),
        top_chunks[0],
    );

    // Pool Info
    let pool_info = vec![
        Line::from(vec![
            Span::raw("Workers(Miners): "),
            Span::styled(
                format!("{}", app.pool_workers),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Hashrate(Total): "),
            Span::styled(
                format!("{:.2} GH/s", app.pool_hashrate),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Blocks: "),
            Span::styled(
                format!("{}", app.pool_blocks),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Shares: "),
            Span::styled(
                format!("{} ✓ / {} ✗", app.pool_shares_good, app.pool_shares_bad),
                Style::default().fg(Color::Yellow),
            ),
        ]),
    ];
    let pool_block = Block::default().borders(Borders::ALL).title("Pool");
    f.render_widget(Paragraph::new(pool_info).block(pool_block), top_chunks[1]);

    // Users Info
    let users_info = vec![
        Line::from(vec![
            Span::raw("Active: "),
            Span::styled(
                format!("{}", app.users_active),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Total: "),
            Span::styled(
                format!("{}", app.users_total),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("New Today: "),
            Span::styled(
                format!("{}", app.users_new_today),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::raw("Verified: "),
            Span::styled(
                format!("{}", app.users_verified),
                Style::default().fg(Color::Yellow),
            ),
        ]),
    ];
    let users_block = Block::default().borders(Borders::ALL).title("Users");
    f.render_widget(Paragraph::new(users_info).block(users_block), top_chunks[2]);

    // --- MIDDLE ROW ---
    let middle_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(60), Constraint::Percentage(40)])
        .split(chunks[1]);

    // CLI Input area
    let input_text = vec![
        Line::from(vec![
            Span::styled("Type      ", Style::default().fg(Color::Yellow)),
            Span::styled("'help'", Style::default().fg(Color::Yellow)),
            Span::raw(" for commands, "),
            Span::styled("'exit'", Style::default().fg(Color::Yellow)),
            Span::raw(" to quit."),
        ]),
        Line::from(format!("> {}", app.input)),
    ];

    let input_block = Block::default()
        .borders(Borders::ALL)
        .title("DUCO Server $");
    f.render_widget(
        Paragraph::new(input_text).block(input_block),
        middle_chunks[0],
    );

    // Logs
    let log_lines: Vec<Line> = app.logs.iter().map(|l| Line::from(l.as_str())).collect();
    let logs_block = Block::default().borders(Borders::ALL).title("Logs");
    f.render_widget(
        Paragraph::new(log_lines)
            .block(logs_block)
            .wrap(Wrap { trim: true }),
        middle_chunks[1],
    );

    // --- BOTTOM ROW ---
    let bottom_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(60),
            Constraint::Percentage(20),
            Constraint::Percentage(20),
        ])
        .split(chunks[2]);

    // Connections Table
    let rows: Vec<Row> = app
        .connections
        .iter()
        .map(|c| {
            Row::new(vec![
                c.name.clone(),
                c.ip.clone(),
                c.port.to_string(),
                c.status.clone(),
                c.sent.clone(),
                c.received.clone(),
                c.uptime.clone(),
            ])
        })
        .collect();

    let table = Table::new(
        rows,
        [
            Constraint::Percentage(15),
            Constraint::Percentage(20),
            Constraint::Percentage(10),
            Constraint::Percentage(15),
            Constraint::Percentage(15),
            Constraint::Percentage(15),
            Constraint::Percentage(10),
        ],
    )
    .header(
        Row::new(vec![
            "Name", "IP", "Port", "Status", "Sent", "Received", "Uptime",
        ])
        .style(Style::default().add_modifier(Modifier::BOLD)),
    )
    .block(Block::default().borders(Borders::ALL).title("Connections"));
    f.render_widget(table, bottom_chunks[0]);

    // CPU Usage
    let cpu_data: Vec<u64> = app.cpu_usage.iter().map(|&v| v as u64).collect();
    let cpu_sparkline = Sparkline::default()
        .block(Block::default().borders(Borders::ALL).title(format!(
            "CPU Usage: {:.1}%",
            app.cpu_usage.last().unwrap_or(&0.0)
        )))
        .data(&cpu_data)
        .style(Style::default().fg(Color::Red));
    f.render_widget(cpu_sparkline, bottom_chunks[1]);

    // Memory Usage
    let mem_data: Vec<u64> = app.mem_usage.iter().map(|&v| v as u64).collect();
    let mem_sparkline = Sparkline::default()
        .block(Block::default().borders(Borders::ALL).title(format!(
            "Memory Usage: {:.1}%",
            app.mem_usage.last().unwrap_or(&0.0)
        )))
        .data(&mem_data)
        .style(Style::default().fg(Color::Yellow));
    f.render_widget(mem_sparkline, bottom_chunks[2]);
}
