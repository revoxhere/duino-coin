require 'socket'
require 'digest'
puts "Duino-Coin minimal Ruby miner"
# Very early work in progress, for now it can find only one share
# Will finish it some time later

username = "username"
password = "password"

s = TCPSocket.open('0.tcp.ngrok.io', 12596)
puts "Connected to server"

SERVER_VER = s.gets(3) # Read lines from socket
puts "Server is on version " + SERVER_VER

s.puts("LOGI,"+String(username)+","+String(password))
FEEDBACK = s.gets(2)
puts "Login feedback is " + FEEDBACK

s.write("JOB")
job = s.read()
puts job
job = job.split(',')
difficulty = job[2]
for result in 0..100*Integer(difficulty)+1 do
	sha1 = Digest::SHA1.hexdigest String(String(job[0])+String(result))
	if sha1 == String(job[1])
		s.write(result)
		puts "Share feedback: "+String(FEED)
	end
end
