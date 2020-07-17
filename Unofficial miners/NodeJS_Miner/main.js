const net = require("net");
const {PromiseSocket} = require("promise-socket");
const sha1 = require("js-sha1");
const https = require("https");

let socket = new net.Socket();
const promiseSocket = new PromiseSocket(socket);

https.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt", res => {
    res.on("data", data => {
        const response = data.toString();
        const serverPort = Number(response.split("\n").slice(1, -4));
        const serverIp = response.split("\n").slice(0, -5);
        socket.setEncoding('utf8');
        socket.connect(serverPort, serverIp.toString());
    })
})

const user = "username";    //put your credentials here
const pass = "password";

function findNumber(prev, toFind, diff) {
    return new Promise((resolve, reject) => {
        for (let i = 0; i < 100 * diff; i++) {
            let hash = sha1(prev + i);
            if (hash == toFind) {
                console.log("Hash Found!");
                socket.write(i.toString());
                resolve();
                break;
            }
        }
    })
}

async function startMining() { // start the mining process
    while (true) {
        socket.write("JOB");
        let job = await promiseSocket.read();
        job = job.split(",");

        let prev = job[0];
        let toFind = job[1];
        let diff = job[2];

        console.log("got job! difficulty: " + diff);

        await findNumber(prev, toFind, diff);
        console.log(await promiseSocket.read()); // await the socket answer (GOOD or BAD)
    }
}

socket.once("data", (data) => {	// login process
    if (data == "1.5") {
        socket.write(`LOGI,${user},${pass}`);
        console.log("Sending login infos");
        socket.once("data", (data) => {
            if (data == "OK") {
                console.log("Login OK");
                socket.write("BALA");
                socket.once("data", async (data) => {
                    console.log("User balance: " + data);
                    startMining();
                }) 
            } else {
                console.log(data.slice(3));
                socket.end();
            }
        })
    } else {
        console.log("Miner outdated!");
        socket.end();
    }
})    

socket.on("end", () => {
    console.log("Connection ended");
})

socket.on("error", (err) => {
    console.log(`Socket error: ${err}`);
})
