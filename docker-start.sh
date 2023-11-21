#!/bin/bash

echo '[PC Miner]' > /app/duino-coin/Settings.cfg
echo "username = ${DUCO_USERNAME}" >> /app/duino-coin/Settings.cfg
echo "mining_key = $(echo -n ${DUCO_MINING_KEY} | base64)" >> /app/duino-coin/Settings.cfg
echo "intensity = ${DUCO_INTENSITY}" >> /app/duino-coin/Settings.cfg
echo "threads = ${DUCO_THREADS}" >> /app/duino-coin/Settings.cfg
echo "start_diff = ${DUCO_START_DIFF}" >> /app/duino-coin/Settings.cfg
echo "donate = ${DUCO_DONATE}" >> /app/duino-coin/Settings.cfg
echo "identifier = ${DUCO_IDENTIFIER}" >> /app/duino-coin/Settings.cfg
echo "algorithm = ${DUCO_ALGORITHM}" >> /app/duino-coin/Settings.cfg
echo "language = ${DUCO_LANGUAGE}" >> /app/duino-coin/Settings.cfg
echo "soc_timeout = ${DUCO_SOC_TIMEOUT}" >> /app/duino-coin/Settings.cfg
echo "report_sec = ${DUCO_REPORT_SEC}" >> /app/duino-coin/Settings.cfg
echo "raspi_leds = ${DUCO_RASPI_LEDS}" >> /app/duino-coin/Settings.cfg
echo "raspi_cpu_iot = ${DUCO_RASPI_CPU_IOT}" >> /app/duino-coin/Settings.cfg
echo "discord_rp = ${DUCO_DISCORD_RP}" >> /app/duino-coin/Settings.cfg

python3 /app/duino-coin/PC_Miner.py
