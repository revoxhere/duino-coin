#ifndef DASHBOARD_H
#define DASHBOARD_H

const char WEBSITE[] PROGMEM = R"=====(
    <!DOCTYPE html>
    <html>
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
        <title>Duino-Coin @@DEVICE@@ dashboard</title>
        <link rel="stylesheet" href="https://server.duinocoin.com/assets/css/mystyles.css">
        <link rel="shortcut icon" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
        <link rel="icon" type="image/png" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
    </head>
    <body>
        <section class="section">
            <div class="container">
                <h1 class="title">
                    <img class="icon" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
                    @@DEVICE@@ <small>(@@ID@@)</small>
                </h1>
                <p class="subtitle">
                    Self-hosted, lightweight, official dashboard for your <strong>Duino-Coin</strong> miner
                </p>
            </div>
            <br>
            <div class="container">
                <div class="columns">
                    <div class="column">
                        <div class="box">
                            <p class="subtitle">
                                Mining statistics
                            </p>
                            <div class="columns is-multiline">
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        <span id="hashratex">@@HASHRATE@@</span> kH/s
                                    </div>
                                    <div class="heading is-size-5">
                                        Hashrate
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@DIFF@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Difficulty
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@SHARES@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Shares
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@NODE@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Node
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="column">
                        <div class="box">
                            <p class="subtitle">
                                Device information
                            </p>
                            <div class="columns is-multiline">
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@DEVICE@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Device type
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@ID@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Device ID
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@MEMORY@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Free memory
                                    </div>
                                </div>
                                <div class="column" style="min-width:15em">
                                    <div class="title is-size-5 mb-0">
                                        @@VERSION@@
                                    </div>
                                    <div class="heading is-size-5">
                                        Miner version
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <br>
                <div class="has-text-centered">
                    <div class="title is-size-6 mb-0">
                        Hosted on
                        <a href="http://@@IP_ADDR@@">
                            http://<b>@@IP_ADDR@@</b>
                        </a>
                        &bull;
                        <a href="https://duinocoin.com">
                            duinocoin.com
                        </a>
                        &bull;
                        <a href="https://github.com/revoxhere/duino-coin">
                            github.com/revoxhere/duino-coin
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </body>
    </html>
)=====";

#endif
