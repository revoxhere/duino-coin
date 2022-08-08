using System.Net.Sockets;
using System.Net;
using Newtonsoft.Json;
using System.Security.Cryptography;
using System.Text;
using static System.Convert;

class Program
{
    static IPEndPoint ipAddress;
    static readonly HttpClient client = new HttpClient();
    static Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    static string username = "CleoSk";
    static string difficulty = "LOW";
    static async Task Main(string[] args)
    {
        await ConnectToPool();
        Send("MOTD");
        Receive();
        Console.WriteLine(Receive());
        while (true)
        {
            Mine();
        }
        return;
    }

    static void Send(string text)
    {
        socket.Send(Encoding.Default.GetBytes(text));
        return;
    }

    static string Receive()
    {
        byte[] buffer = new byte[128];
        socket.Receive(buffer);
        return Encoding.Default.GetString(buffer);
    }

    static string[] JobRequest()
    {
        Send($"JOB,{username},{difficulty},halk");
        return Receive().Split(",");
    }

    static string Sha1(string text)
    {
        SHA1 sha1 = SHA1.Create();
        byte[] sourceBytes = Encoding.UTF8.GetBytes(text);
        byte[] hashBytes = sha1.ComputeHash(sourceBytes);
        string hash = BitConverter.ToString(hashBytes).Replace("-", String.Empty);
        return hash.ToLower();
    }

    static void Mine()
    {
        string[] job = JobRequest();
        if(job.Length > 0)
        {
            try
            {
                if (job.Length == 3) {
                    for (int i = 0; i < ToUInt32(job[2]) * 100 + 1; i++)
                    {
                        if (Sha1($"{job[0]}{i}").ToLower() == job[1]) {
                            Console.WriteLine("Share found");
                            Send($"{i}");
                            string[] response = Receive().Split(",");
                            if (response.Length == 1)
                            {
                                Console.WriteLine($"[GOOD] Share accepted");
                                return;
                            }
                            else if (response.Length == 2 && response[0] == "BAD")
                            {
                                Console.Write($"[BAD] Share rejected {response[1]}");
                                return;
                            }
                            else if (response[0] == "BLOCK")
                            {
                                Console.WriteLine($"[GOOD] You found block (You are so lucky)");
                                return;
                            }
                            else
                            {
                                Console.WriteLine("Something wrong");
                                return;
                            }
                        }
                    }
                }
            } catch(Exception e)
            {
                Console.WriteLine(e.Message);
                throw;
            }
        }
    }

    static async Task ConnectToPool()
    {
        try
        {
            HttpResponseMessage response = await client.GetAsync("https://server.duinocoin.com/getPool");
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            dynamic json = JsonConvert.DeserializeObject(responseBody);
            ipAddress = IPEndPoint.Parse($"{json.ip}:{json.port}");
            socket.Connect(ipAddress);
            Console.WriteLine("Connected");

        } catch(Exception e)
        {
            Console.WriteLine(e.Message);
            
        }
    }

}