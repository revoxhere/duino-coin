# Stage 1: Build the application
FROM python:3 AS builder

ENV DEBIAN_FRONTEND noninteractive
ENV container docker
ENV TERM=xterm

WORKDIR /app

COPY . /

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

# Clone Duino-Coin repository
RUN git clone https://github.com/revoxhere/duino-coin

# Download duino fasthash
RUN wget https://server.duinocoin.com/fasthash/libducohash.tar.gz

# Unpack it
RUN tar -xvf libducohash.tar.gz

# Go to the dir
WORKDIR /app/libducohash

# Compile it
RUN cargo build --release

# Stage 2: Create the final lightweight image
FROM python:3-slim

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
    git && \
    rm -rf /var/lib/apt/lists/*

# Install pip dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Set the working directory back to /app
WORKDIR /app

RUN ls
RUN pwd

# Make script executable
RUN chmod +x docker-start.sh

# Specify the command to run on container start
CMD ["./docker-start.sh"]
