#!/usr/bin/env ruby
# Minimal version of Duino-Coin PC Miner, useful for developing own apps
# revox 2020-2022
require 'socket'
require 'digest'
require 'net/http'
require 'json' # Only default ruby libraries
require 'time'
require 'colorize' # gem install colorize

username = "revox" # Replace this with your username
minerId = "None" # Custom miner identifier

# Disable debug output
$VERBOSE = nil

puts("\n ‖ Minimal DUCO-S1 Ruby Miner")
puts(" ‖ Duino-Coin community 2020-2022")
puts(" ‖ https://github.com/revoxhere/duino-coin\n\n")

# Server IP file url
url = 'https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt'
uri = URI(url)
# Receive server IP and port
response = Net::HTTP.get(uri) 
response = response.split("\n")
serverip = response[0]
serverport = response[1]
sharecount = 0

# Connect to the server
s = TCPSocket.open(serverip, serverport)
# Read server version
SERVER_VER = s.gets(3) 
puts(" net ".colorize(:color => :white, :background => :blue) + " Connected".colorize(:color => :yellow)  + " to the master Duino-Coin server ("+ SERVER_VER+ ")")

# Mining loop
puts(" cpu ".colorize(:color => :white, :background => :yellow) + " Mining thread is starting".colorize(:color => :yellow) + " using DUCO-S1 algorithm")
loop do 
    # Send job request
    s.puts("JOB,"+String(username)+",MEDIUM,") 
    # Read job
    job = s.read(87) 
    # Split into previous block hash, result hash and difficulty
    job = job.split(',') 
    difficulty = job[2]
    # Measure starting time
    timeStart = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    for result in 0..100 * Integer(difficulty) + 1 do 
        # DUCO-S1 loop - find the numeric result
        # By checking if last block hash + n is result hash
        sha1 = Digest::SHA1.hexdigest String(String(job[0])+String(result))
        # If result is found
        if sha1 == String(job[1])
            # Measure ending time
            timeStop = Process.clock_gettime(Process::CLOCK_MONOTONIC)
            timeDiff = timeStop - timeStart
            # Calculate hashrate
            hashrate = result / timeDiff
            # Send numeric result to the server
            s.write(String(result) + "," + String(hashrate) + ",Minimal Ruby Miner (DUCO-S1)," + String(minerId)) 
            # Receive result feedback
            SHAREFEED = s.read(4)
            sharecount += 1
            # Check wheter it was accepted or not
            if SHAREFEED == "GOOD" or SHAREFEED == "BLOCK"
                puts(" cpu ".colorize(:color => :white, :background => :yellow) + " Accepted".colorize(:color => :green) + " share #" + String(sharecount) + ", speed: " + String(Integer(hashrate / 1000)) + "kH/s @ diff " + String(difficulty))
                break
            if SHAREFEED == "INVU"
                puts "Invalid username!"
                exit
            if SHAREFEED == "BAD"
                puts(" cpu ".colorize(:color => :white, :background => :yellow) + " Rejected".colorize(:color => :red) + " share #" + String(sharecount) + ", speed: " + String(Integer(hashrate / 1000)) + "kH/s @ diff " + String(difficulty))
                break
                end
            end
            end
        end
    end
end
