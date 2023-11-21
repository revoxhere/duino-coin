#!/bin/bash

# Set the base path
base_path="/app/duino-coin"

python_script="${base_path}/PC_Miner.py"

chmod +x "${base_path}/PC_Miner.py" 

# Find the line containing "VER = x.x" in the Python script
ver_value=$(grep "VER =" "$python_script" | awk '{print $3}')

# Set the environment variable
export VER="$ver_value"

# Display the extracted value (optional)
echo "Extracted PC Miner VER value: $VER"

# Run the Python script in the background
python3 "${full_path}/PC_Miner.py" &

# Set a timeout duration
timeout_duration=10
current_time=0

# Check if the Python script is still running
while [ $current_time -lt $timeout_duration ]; do
    sleep 1
    current_time=$((current_time + 1))

    # Check if the process is still running
    if ! ps -p $! > /dev/null; then
        break
    fi
done

# Kill the background process if it's still running after the timeout
if ps -p $! > /dev/null; then
    kill $!
fi

mkdir "${base_path}/Duino-Coin PC Miner ${ver_value}"

# Find the highest version number in the folder
highest_version=$(ls -d "${base_path}/Duino-Coin PC Miner"* | grep -Eo 'Duino-Coin PC Miner [0-9.]+' | sort -Vr | head -n 1)

# Construct the full path with the highest version number
full_path="${base_path}/${highest_version}"

echo '[PC Miner]' > "${full_path}/Miner_config.cfg"
echo "username = ${DUCO_USERNAME}" >> "${full_path}/Miner_config.cfg"
echo "mining_key = $(echo -n ${DUCO_MINING_KEY} | base64)" >> "${full_path}/Miner_config.cfg"
echo "intensity = ${DUCO_INTENSITY}" >> "${full_path}/Miner_config.cfg"
echo "threads = ${DUCO_THREADS}" >> "${full_path}/Miner_config.cfg"
echo "start_diff = ${DUCO_START_DIFF}" >> "${full_path}/Miner_config.cfg"
echo "donate = ${DUCO_DONATE}" >> "${full_path}/Miner_config.cfg"
echo "identifier = ${DUCO_IDENTIFIER}" >> "${full_path}/Miner_config.cfg"
echo "algorithm = ${DUCO_ALGORITHM}" >> "${full_path}/Miner_config.cfg"
echo "language = ${DUCO_LANGUAGE}" >> "${full_path}/Miner_config.cfg"
echo "soc_timeout = ${DUCO_SOC_TIMEOUT}" >> "${full_path}/Miner_config.cfg"
echo "report_sec = ${DUCO_REPORT_SEC}" >> "${full_path}/Miner_config.cfg"
echo "raspi_leds = ${DUCO_RASPI_LEDS}" >> "${full_path}/Miner_config.cfg"
echo "raspi_cpu_iot = ${DUCO_RASPI_CPU_IOT}" >> "${full_path}/Miner_config.cfg"
echo "discord_rp = ${DUCO_DISCORD_RP}" >> "${full_path}/Miner_config.cfg"

python3 "${base_path}/PC_Miner.py"
