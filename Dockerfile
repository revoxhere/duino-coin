# Stage 1: Build the application
FROM python:3 AS builder

ENV DEBIAN_FRONTEND noninteractive
ENV container docker
ENV TERM=xterm

WORKDIR /app/

COPY . ./duino-coin/ 

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends\
    curl \
    python3-pip \
    python3-dev \
    wget \
    git && \
    rm -rf /var/lib/apt/lists/* 

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
RUN echo -e "[source.crates-io]\nindex = \"https://github.com/rust-lang/crates.io-index\"\n\n[http]\nproxy = \"\"" >> ~/.cargo/config.toml
RUN cargo build --release

# Extract the module and move it to /app/duino-coin
RUN mv target/release/libducohasher.so /app/duino-coin/libducohasher.so

# Stage 2: Create the final lightweight image
FROM python:3

LABEL org.opencontainers.image.source="https://github.com/revoxhere/duino-coin"
LABEL org.opencontainers.image.description="Dockerized Duino-Coin Miner"
LABEL org.opencontainers.image.authors="revoxhere,simeononsecurity"

ENV DEBIAN_FRONTEND noninteractive
ENV container docker
ENV TERM=xterm

WORKDIR /app

COPY --from=builder /app /app

# Change to the cloned directory
WORKDIR /app/duino-coin

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
    python3-dev \
    wget \
    git \
    build-essential \
    && \
    rm -rf /var/lib/apt/lists/*

# Install pip dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Set the working directory back to /app
WORKDIR /app

RUN ls
RUN pwd

# Make script executable
RUN chmod +x /app/duino-coin/docker-start.sh

# Specify the command to run on container start
CMD ["/app/duino-coin/docker-start.sh"]