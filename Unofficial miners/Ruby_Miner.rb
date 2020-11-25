#!/usr/bin/env ruby
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020
require 'socket'
require 'digest'
require 'net/http'
require 'json' # Only default ruby libraries

username = "username" # Replace this with your username

$VERBOSE = nil # Disable debug output
url = 'https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt'
uri = URI(url)
response = Net::HTTP.get(uri) # Receive server IP and port
response = response.split("\n")
serverip = response[0]
serverport = response[1]

s = TCPSocket.open(serverip, serverport) # Connect to the server
SERVER_VER = s.gets(3) # Read server version
puts "Server is on version " + SERVER_VER

loop do # Mining loop
	s.puts("JOB,"+String(username)) # Send job request
	job = s.read(86) # Read job
	job = job.split(',') # Split into previous block hash, result hash and difficulty
	difficulty = job[2]
	for result in 0..100 * Integer(difficulty) + 1 do # Find the numeric result
		sha1 = Digest::SHA1.hexdigest String(String(job[0])+String(result)) # By checking if last block hash + n is result hash
		if sha1 == String(job[1]) # If result is found
			s.write(result) # Send numeric result to the server
			SHAREFEED = s.read(4) # And receive result feedback
			if SHAREFEED == "GOOD" or SHAREFEED == "BLOCK" # Check wheter it was accepted or not
				puts "Accepted share " + String(result) + " (Difficulty " + String(difficulty) + ")"
				break
			if SHAREFEED == "INVU"
				puts "Invalid username!"
				exit
			if SHAREFEED == "BAD"
				puts "Rejected share " + String(result) + " (Difficulty " + String(difficulty) + ")"
				break
				end
			end
			end
		end
	end
end
