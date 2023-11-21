# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

COPY . /

ENV DUCO_USERNAME="simeononsecurity" \
    DUCO_MINING_KEY="" \
    DUCO_INTENSITY=50 \
    DUCO_THREADS=2 \
    DUCO_START_DIFF="MEDIUM" \
    DUCO_DONATE=0 \
    DUCO_IDENTIFIER="Auto" \
    DUCO_ALGORITHM="DUCO-S1" \
    DUCO_LANGUAGE="english" \
    DUCO_SOC_TIMEOUT=20 \
    DUCO_REPORT_SEC=300 \
    DUCO_RASPI_LEDS="n" \
    DUCO_RASPI_CPU_IOT="n" \
    DUCO_DISCORD_RP="n"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends\
    curl \
    python3-pip \
    python3-dev 

# Install rustup for compilation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Download duino fasthash
RUN wget https://server.duinocoin.com/fasthash/libducohash.tar.gz

# Unpack it
RUN tar -xvf libducohash.tar.gz

# Go to the dir
WORKDIR /app/libducohash

# Compile it
RUN cargo build --release

# Extract the module and move it to /app/duino-coin
RUN mv target/release/libducohasher.so /app/duino-coin

# Set the working directory back to /app
WORKDIR /app

# Clone Duino-Coin repository
RUN git clone https://github.com/revoxhere/duino-coin

# Change to the cloned directory
WORKDIR /app/duino-coin

# Install pip dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Set the working directory back to /app
WORKDIR /app

# Make script executable
RUN chmod +x generate_settings.sh

# Specify the command to run on container start
CMD ["./docker-start.sh"]
