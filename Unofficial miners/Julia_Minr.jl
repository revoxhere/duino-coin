using Sockets
using SHA
username = "revox" # Replace this with your username

socket = Sockets.connect("51.15.127.80", 2811)
println("Connected to Duino-Coin server")

server_ver = String(read(socket, 3))
println("Server is on version: ", server_ver)

while true
	write(socket, string("JOB,", String(username), ",MEDIUM"))
	job = String(read(socket, 87))
	#println("Job received: ", job)

	job = split(job, ",")
	lastBlockHash = job[1]
	result = job[2]
	difficulty = parse(Int32, job[3]) * 100

	for i = 0:difficulty
		stringToHash = string(lastBlockHash, string.(i))
		ducos1 = bytes2hex(sha1(stringToHash))

		if ducos1 == result 
			write(socket, string(i, ",,Julia Miner"))
			feedback = String(read(socket, 4))
			if feedback == "GOOD"
				println("Accepted share ", i, "\tDifficulty ", difficulty)
				break
			else
				println("Rejected share ", i, "\tDifficulty ", difficulty)
				break
			end
		end
		i += 1
	end
end
