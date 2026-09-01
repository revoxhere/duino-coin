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

        .log-success { color: var(--phosphor); }

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

        /* Эффект обновления данных в терминале */
        .data-flash {
            color: #ffffff;
            text-shadow: 0 0 8px #ffffff;
            transition: color 0.1s ease, text-shadow 0.1s ease;
        }

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

        @media (prefers-reduced-motion: reduce) {
            .cursor { animation: none; opacity: 0.6; }
            body { background-image: none; }
            .data-flash { transition: none; }
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
        
        <!-- Добавлены id="..." к динамическим переменным -->
        <div class="log-line"><span class="log-prefix">[SYS]</span> INIT @@DEVICE@@ // ID: @@ID@@</div>
        <div class="log-line"><span class="log-prefix">[SYS]</span> FW VER: @@VERSION@@</div>
        <div class="log-line"><span class="log-prefix">[SYS]</span> HEAP ALLOC: <span id="stat-memory">@@MEMORY@@</span> FREE</div>
        <div class="log-line"><span class="log-prefix">[ENV]</span> PAYLOAD: <span id="stat-sensor">@@SENSOR@@</span></div>
        <div class="log-line"><span class="log-prefix">[NET]</span> RESOLVING <span id="stat-node">@@NODE@@</span>...</div>
        <div class="log-line log-success"><span class="log-prefix">[NET]</span> CONNECTION ESTABLISHED</div>
        <div class="log-line log-success"><span class="log-prefix">[MIN]</span> DIFFICULTY SET: <span id="stat-diff">@@DIFF@@</span></div>
        <div class="log-line log-success"><span class="log-prefix">[MIN]</span> SHARES OK: <span id="stat-shares">@@SHARES@@</span></div>

        <hr class="payload-separator">

        <div class="readout-container">
            <div class="readout-label">Current Hashrate</div>
            <div>
                <span class="readout-value" id="hashratex">@@HASHRATE@@</span>
                <span class="readout-unit">kH/s</span>
                <span class="cursor"></span>
            </div>
        </div>

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

    <script>
        // Список ID элементов, которые нужно обновлять
        const dynamicIds = ['hashratex', 'stat-diff', 'stat-shares', 'stat-memory', 'stat-sensor', 'stat-node'];

        async function fetchLiveStats() {
            try {
                // Запрашиваем ту же самую страницу в фоне
                const response = await fetch(window.location.href);
                if (!response.ok) return;
                
                const htmlText = await response.text();
                
                // Создаем временный скрытый DOM, чтобы вытащить оттуда новые значения
                const parser = new DOMParser();
                const tempDoc = parser.parseFromString(htmlText, 'text/html');

                dynamicIds.forEach(id => {
                    const liveEl = document.getElementById(id);
                    const fetchedEl = tempDoc.getElementById(id);
                    
                    // Если элемент существует и значение изменилось
                    if (liveEl && fetchedEl && liveEl.innerText !== fetchedEl.innerText) {
                        liveEl.innerText = fetchedEl.innerText;
                        
                        // Добавляем эффект вспышки
                        liveEl.classList.add('data-flash');
                        
                        // Убираем вспышку через 150 мс
                        setTimeout(() => {
                            liveEl.classList.remove('data-flash');
                        }, 150);
                    }
                });
            } catch (e) {
                // Тихо игнорируем ошибки сети (например, если ESP перезагружается)
                console.error("Sync failed", e);
            }
        }

        // Запускаем первый запрос сразу, затем каждые 5 секунд
        setTimeout(fetchLiveStats, 1000);
        setInterval(fetchLiveStats, 5000);
    </script>
</body>
</html>
)=====";

#endif 