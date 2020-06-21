const net = require("net");
const {PromiseSocket} = require("promise-socket")
const sha1 = require("js-sha1");

let socket = new net.Socket();
const promiseSocket = new PromiseSocket(socket)
socket.setEncoding('utf8');
socket.connect(15177, "0.tcp.ngrok.io")

const user = "";    //put your credentials here
const pass = "";

async function startMining() { // start the mining process
    while (true) {
        console.log("getting job...")
        socket.write("JOB")
        let job = await promiseSocket.read()
        job = job.split(",")

        let prev = job[0]
        let toFind = job[1]
        let diff = job[2];

        console.log("got job! difficulty: " + diff)

        function findNumber(prev, toFind, diff) { // find the number
            return new Promise((resolve, reject) => {
                for (let i = 0; i < 100 * diff; i++) {
                    let hash = sha1(prev + i)
                    if (hash == toFind) {
                        console.log("Hash Found!")
                        socket.write(i.toString())
                        resolve();
                        break;
                    }
                }
            })
        }
        await findNumber(prev, toFind, diff)
        console.log(await promiseSocket.read()) // await the socket answer (GOOD or BAD)
    }
}

socket.once("data", (data) => {	// login process
    if (data == "1.5") {
        socket.write(`LOGI,${user},${pass}`);
        console.log("Sending login infos")
        socket.once("data", (data) => {
            if (data == "OK") {
                console.log("Login OK")
                socket.write("BALA")
                socket.once("data", async (data) => {
                    console.log("User balance: " + data)
                    startMining();
                }) 
            } else {
                console.log(data.slice(3));
                socket.end();
            }
        })
    } else {
        console.log("Miner outdated / wrong port!");
        socket.end();
    }
})


socket.on("end", () => {
    console.log("Connection ended")
})
