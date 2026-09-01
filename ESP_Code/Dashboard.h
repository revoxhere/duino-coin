#ifndef DASHBOARD_H
#define DASHBOARD_H

const char WEBSITE[] PROGMEM = R"=====(
<!DOCTYPE html>
<html lang="en">
<!--
    Duino-Coin self-hosted dashboard
    MIT licensed
    The Duino-Coin Team, 2019-present
    https://github.com/revoxhere/duino-coin
    https://duinocoin.com
-->
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@@DEVICE@@ // @@ID@@</title>
    <link rel="shortcut icon" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
    <link rel="icon" type="image/png" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0a0a;
            --phosphor: #ffb000;
            --phosphor-dim: #6b4c00;
            --phosphor-glow: rgba(255, 176, 0, 0.15);
            --font-mono: 'Share Tech Mono', 'Courier New', monospace;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: var(--bg);
            color: var(--phosphor);
            font-family: var(--font-mono);
            min-height: 100vh;
            padding: 2rem;
            /* Subtle CRT scanline effect for texture without killing performance */
            background-image: linear-gradient(rgba(0, 0, 0, 0.3) 50%, transparent 50%);
            background-size: 100% 4px;
        }

        .terminal {
            max-width: 800px;
            margin: 0 auto;
            font-size: 0.9rem;
            line-height: 1.6;
            text-shadow: 0 0 5px var(--phosphor-glow);
        }

        /* Log lines */
        .log-line {
            opacity: 0.9;
            margin-bottom: 0.2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .log-prefix {
            color: var(--phosphor-dim);
            margin-right: 0.5rem;
        }

        .log-success {
            color: var(--phosphor);
        }

        /* The Hero / Readout */
        .payload-separator {
            margin: 3rem 0;
            border: none;
            border-top: 1px dashed var(--phosphor-dim);
            opacity: 0.5;
        }

        .readout-container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            position: relative;
            padding-left: 1rem;
        }

        .readout-label {
            font-size: 0.75rem;
            color: var(--phosphor-dim);
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin-bottom: 0.5rem;
        }

        .readout-value {
            font-size: clamp(4rem, 12vw, 8rem);
            font-weight: 400;
            line-height: 0.85;
            color: var(--phosphor);
            text-shadow: 
                0 0 10px var(--phosphor),
                0 0 20px var(--phosphor-glow),
                0 0 40px var(--phosphor-glow);
            position: relative;
            display: inline-block;
        }

        .readout-unit {
            font-size: 1.5rem;
            color: var(--phosphor-dim);
            margin-left: 0.5rem;
            text-shadow: none;
        }

        /* Blinking block cursor */
        .cursor {
            display: inline-block;
            width: 0.6em;
            height: 1.1em;
            background-color: var(--phosphor);
            margin-left: 0.5rem;
            vertical-align: text-bottom;
            animation: blink 1s step-end infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        /* Footer / Meta */
        .meta-container {
            margin-top: 3rem;
            font-size: 0.75rem;
            color: var(--phosphor-dim);
            border-top: 1px solid var(--phosphor-dim);
            padding-top: 1rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 1rem;
            opacity: 0.7;
        }

        a {
            color: var(--phosphor);
            text-decoration: none;
            border-bottom: 1px dashed var(--phosphor-dim);
            transition: all 0.2s ease;
        }

        a:hover, a:focus-visible {
            color: #fff;
            border-bottom-color: #fff;
            text-shadow: 0 0 8px #fff;
        }

        /* Accessibility & Motion */
        @media (prefers-reduced-motion: reduce) {
            .cursor {
                animation: none;
                opacity: 0.6;
            }
            body {
                background-image: none;
            }
        }

        *:focus-visible {
            outline: 1px solid var(--phosphor);
            outline-offset: 2px;
        }

        @media (max-width: 600px) {
            body { padding: 1rem; }
            .log-line { font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <main class="terminal" role="img" aria-label="Device terminal output showing mining status">
        
        <!-- Simulated Boot/Init Log -->
        <div class="log-line"><span class="log-prefix">[SYS]</span> INIT @@DEVICE@@ // ID: @@ID@@</div>
        <div class="log-line"><span class="log-prefix">[SYS]</span> FW VER: @@VERSION@@</div>
        <div class="log-line"><span class="log-prefix">[SYS]</span> HEAP ALLOC: @@MEMORY@@ FREE</div>
        <div class="log-line"><span class="log-prefix">[ENV]</span> PAYLOAD: @@SENSOR@@</div>
        <div class="log-line"><span class="log-prefix">[NET]</span> RESOLVING @@NODE@@...</div>
        <div class="log-line log-success"><span class="log-prefix">[NET]</span> CONNECTION ESTABLISHED</div>
        <div class="log-line log-success"><span class="log-prefix">[MIN]</span> DIFFICULTY SET: @@DIFF@@</div>
        <div class="log-line log-success"><span class="log-prefix">[MIN]</span> SHARES OK: @@SHARES@@</div>

        <hr class="payload-separator">

        <!-- The Thesis / Hero -->
        <div class="readout-container">
            <div class="readout-label">Current Hashrate</div>
            <div>
                <span class="readout-value" id="hashratex">@@HASHRATE@@</span>
                <span class="readout-unit">kH/s</span>
                <span class="cursor"></span>
            </div>
        </div>

        <!-- Footer Meta -->
        <div class="meta-container">
            <div>
                HOST: <a href="http://@@IP_ADDR@@">@@IP_ADDR@@</a> &middot; 
                <a href="https://duinocoin.com">DUINOCOIN.COM</a> &middot; 
                <a href="https://github.com/revoxhere/duino-coin">GITHUB</a>
            </div>
            <div>
                @@RESET_SETTINGS@@
            </div>
        </div>

    </main>
</body>
</html>
)=====";

#endif