 #!/usr/bin/env python3
##########################################
# Duino-Coin Server (v1.7) 
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © Duino-Coin Community 2019-2020
##########################################
# Warning: this server structure is no longer used as the masterserver
##########################################
import socket, shutil, threading, time, random, glob, hashlib, math, datetime, re, configparser, sys, os, string, json
from pathlib import Path
from github import Github
from natsort import natsorted
from signal import signal, SIGINT

import requests, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("-------------------------------------------")
print("   Duino-Coin Master Server v1.7")
print("             by Duino-Coin Community")
print("                               2019-2020")
print("-------------------------------------------")
current_hour = time.strptime(time.ctime(time.time())).tm_hour
if current_hour < 12 :
  greeting = "Good morning,"
elif current_hour == 12 :
  greeting = "Good noon,"
elif current_hour > 12 and current_hour < 18 :
  greeting = "Good afternoon,"
elif current_hour >= 18 :
  greeting = "Good evening,"
else:
  greeting = "Welcome back,"
print("  "+greeting+" DUCO administrator.")
print("  I wish you quick, nice and pleasant work!\n")

def ServerLog(whattolog): # Info section
  print("[INFORMANT] "+ str(whattolog))

def ServerWarning(whattolog): # Warning section
  print("[WARNING] !!! " + str(whattolog) + " !!!")

def Watchdog(whattolog): # Watchdog section
  print("[WATCHDOG] " + str(whattolog))

def autorestarter(): # Autorestarter
  Watchdog("Autorestarter declares waiting state")
  time.sleep(3600)
  Watchdog("Autorestarter is restarting the server")
  tcpsock.shutdown(socket.SHUT_RDWR)
  tcpsock.close()
  os.execl(sys.executable, sys.executable, *sys.argv)
threading.Thread(target=autorestarter).start()

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
  Watchdog("SIGNINT detected - See you soon!")
  os._exit(0)
signal(SIGINT, handler) # Enable signal handler
Watchdog("Signal handler declares ready state")

def copytree(src, dst, symlinks=False, ignore=None):
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      shutil.copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)

def Backuper():
  time.sleep(5)
  today = datetime.date.today()
  if not os.path.isdir('backups/'+str(today)+'/'):
    Watchdog("Backuper declares it's creating backup for today (" + str(today) + ")")
    try:
      os.makedirs("backups/"+str(today)+"/balances")
      os.makedirs("backups/"+str(today)+"/emails")
      os.makedirs("backups/"+str(today)+"/users")
    except:
      pass
    copytree("balances/", "backups/"+str(today)+"/balances/")
    copytree("emails/", "backups/"+str(today)+"/emails/")
    copytree("users/", "backups/"+str(today)+"/users/")
    Watchdog("Backuper declares it's finished creating backup for today (" + str(today) + ")")
    with open("prices.txt", "a") as pricesfile:
      pricesfile.write("," + str(round(ducoPrice, 4)).rstrip("\n"))
      Watchdog("Backuper declares it wrote todays DUCO price " + str(ducoPrice) + " to prices file")
  threading.Timer(1800, Backuper).start() # Run this def every .5h

def GenerateAPIfile(): ######################## API SECTION ########################
  global server_info, hashrates, threads, diff, update_count, gitrepo, miners, gitusername, rewardap, blocks, userinfo, allmined
  global supplyleft, minedBlocks, ducoPrice, usersNumber, poolHashrate, prefix, workersNumber, workersList
  threading.Timer(2.5, GenerateAPIfile).start()

  now = datetime.datetime.now()
  now = now.strftime("%d/%m/%Y %H:%M")

  allmined = 0
  miners = []
  res = []
  leadersdata = []
  server_info['pool_hashrate'] = 0
  server_info['users'] = len(os.listdir('users'))

  for hashrate in hashrates:
    server_info['pool_hashrate'] += float(hashrates[hashrate]["hashrate"])

  data = {"pool_miners" : server_info["miners"], "pool_hashrate" : server_info["pool_hashrate"], "users" : server_info["users"], "miners" : {}}
  for hashrate in hashrates:
    data["miners"][hashrate] = hashrates[hashrate]

  for x in hashrates:
    miners.append(hashrates[x]["username"]) 
  
  for i in miners:  
    if i not in res:  
      res.append(i)

  xmgusd = .011
  try:
    coingecko = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=magi&vs_currencies=usd", data = None)
    if coingecko.status_code == 200:
      geckocontent = coingecko.content.decode()
      geckocontentjson = json.loads(geckocontent)
      xmgusd = float(geckocontentjson["magi"]["usd"])
  except:
    pass

  workersNumber = str(len(res))
  workersList = str(" (") + str(', '.join(map(str, res))) + str(")")
  usersNumber = str(server_info["users"])

  randommultiplier = random.randint(97,103) / 100
  ducousdLong = float(xmgusd) * 3.5 * randommultiplier
  ducoPrice = round(float(ducousdLong) / 10 * 0.65, 8) 

  poolHashrate = float((server_info['pool_hashrate']))
  if float(poolHashrate) >= 0:
    poolHashrate = round((server_info['pool_hashrate']), 2) # typical
    prefix = "H"
  if float(poolHashrate) > 1000:
    poolHashrate = int((server_info['pool_hashrate']) / 1000) # to kH conversion
    prefix = "kH"
  if float(poolHashrate) > 1000000:
    poolHashrate = int((server_info['pool_hashrate']) / 1000000) # to MH conversion
    prefix = "MH"
  if float(poolHashrate) > 1000000000:
    poolHashrate = int((server_info['pool_hashrate']) / 1000000000) # to GH conversion
    prefix = "GH"

  with locker: # Last block hash
    with open("config/lastblock", "r+") as lastblok:
      lastblokid = lastblok.readline().rstrip("\n\r ")
      lastblockHash = str(lastblokid)[:10]+"..."

  with locker: # Difficulty and mined blocks
    with open("config/blocks", "r") as blok:
      minedBlocks = blok.readline()

    difficulty = math.ceil(int(minedBlocks) / int(diff_incrase_per))
    supplyleft = int(supply) - int(minedBlocks) # Remaining blcks

  with locker:
    with open("config/foundBlocks", "r") as foundb:
      foundBlocks = foundb.read().splitlines()

  if workersList == " ()":
    workersList = " (No active workers)"

  for filename in os.listdir("balances/"): # All-time mined duco
    if filename.endswith(".txt"):
      try:
        with locker:
          with open("balances/"+filename) as f:
            allmined += float(f.read())
        continue
      except:
        continue
    else:
      continue
  
  leaderfiles = glob.glob("balances/*.txt") 
  for leaderfile in leaderfiles:
    with locker:
      with open(leaderfile, 'r') as leadercontent:
        try:
          leaderline = leadercontent.readline().rstrip()
          leaderline = str(round(float(leaderline), 2))
          leadersdata.append(leaderline + " DUCO - " + leaderfile.replace("balances/", "").replace(".txt", ""))
        except:
          Warning(str(leaderfile) + " has problems with the balance!")
  leadersdata = natsorted(leadersdata, reverse=True) # Sort in descending order
  
  ########## PREPARE JSON #########
  with open("config/api.json", "w") as jsonfile:
    jsonapi = json.dumps({
      'Server version': str(VER),
      'Last update': str(now)+str(" (UTC)"),
      'Duco price': str(ducoPrice),
      'GitHub API file update count': str(update_count),
      'Current difficulty': str(difficulty),
      'Diff increases per': str(diff_incrase_per)+str(" blocks"),
      'Registered users': str(usersNumber),
      'Mined blocks': str(minedBlocks),
      'Supply left': str(supplyleft),
      'Total supply': str(supply),
      'Pool hashrate': str(poolHashrate)+" "+prefix+"/s",
      'Active workers': str(workersNumber) + str(workersList),
      'All-time mined DUCO': str(allmined),
      'Top 10 richest miners': str(str(leadersdata[0]) + ", "
                              + str(leadersdata[1]) + ", "
                              + str(leadersdata[2]) + ", "
                              + str(leadersdata[3]) + ", "
                              + str(leadersdata[4]) + ", "
                              + str(leadersdata[5]) + ", "
                              + str(leadersdata[6]) + ", "
                              + str(leadersdata[7]) + ", "
                              + str(leadersdata[8]) + ", "
                              + str(leadersdata[9])),
      'Last block hash': str(lastblockHash),
      'Full last block hash': str(lastblokid)}
      , sort_keys=False, indent=4)
    jsonfile.write(str(jsonapi))

def InputManagement():
  time.sleep(1)
  Watchdog("Input processor declares ready state")

  while True:
    userInput = input("DUCO Server $ ")
    userInput = userInput.split(" ")

    if userInput[0] == "help":
      print("""Available commands:
        - help - shows this help menu
        - helpme - shows a message
        - balance <user> - prints user balance
        - set <user> <number> - sets user balance to number
        - subtract <user> <number> - subtract number from user balance
        - add <user> <number> - add number to user balance
        - clear - clears console
        - exit - exits DUCO server
        - restart - restarts DUCO server
        - summary - shows quick statistics about the server""")

    elif userInput[0] == "helpme":
      messageList = [
      "  It will get better. It always does.", 
      "  Too depressed to live, too afraid to die? Trust me, it's not worth testing your bravery.",
      "  You can get through it.",
      "  Think about all the things you planned to do. You want to make them true, do you?",
      "  Listen to some music. It always helps.",
      "  'It's not my problem' - and you're free."] # I'll add more stuff here when I'll come up with something
      print(random.choice(messageList))

    elif userInput[0] == "summary":
      print("Quick summary:")
      print("  All mined DUCO: "+str(allmined))
      print("  Registered users: "+str(usersNumber))
      print("  Est. DUCO price: "+str(ducoPrice)+" USD")
      print("  Est. network hashrate: "+str(poolHashrate) + " " + prefix + "/s")
      print("  Active workers: " +str(workersNumber) + str(workersList))

    elif userInput[0] == "clear":
      os.system('clear')

    elif userInput[0] == "exit":
      print("  Are you sure you want to exit DUCO server?")
      confirm = input("  Y/n")
      if confirm == "Y" or confirm == "y" or confirm == "":
        tcpsock.shutdown(socket.SHUT_RDWR)
        tcpsock.close()
        os._exit(0)
      else:
        print("Canceled")

    elif userInput[0] == "restart":
      print("  Are you sure you want to restart DUCO server?")
      confirm = input("  Y/n")
      if confirm == "Y" or confirm == "y" or confirm == "":
        os.system('clear')
        tcpsock.shutdown(socket.SHUT_RDWR)
        tcpsock.close()
        os.execl(sys.executable, sys.executable, *sys.argv)
      else:
        print("Canceled")

    elif userInput[0] == "balance":
      try:
        with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
          balance = balancefile.readline()
          print(userInput[1] + "'s balance: " + str(balance))
      except:
        print("User '" + userInput[1] + "' doesn't exist")

    elif userInput[0] == "set":
      try:
        with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
          balance = balancefile.readline()
          print("  " + userInput[1] + "'s balance is " + str(balance) + ", set it to " + str(float(userInput[2])) + "?")
          confirm = input("  Y/n")
          if confirm == "Y" or confirm == "y" or confirm == "":
            with open("balances/" + str(userInput[1]) + ".txt", "w") as balancefile:
              balancefile.write(str(float(userInput[2])))
            with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
              balance = balancefile.readline()
              print("User balance is now " + str(balance))
          else:
            print("Canceled")
      except:
        print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")

    elif userInput[0] == "subtract":
      try:
        with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
          balance = balancefile.readline()
          print("  " + userInput[1] + "'s balance is " + str(balance) + ", subtract " + str(float(userInput[2])) + "?")
          confirm = input("  Y/n")
          if confirm == "Y" or confirm == "y" or confirm == "":
            with open("balances/" + str(userInput[1]) + ".txt", "w") as balancefile:
              balancefile.write(str(float(balance)-float(userInput[2])))
            with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
              balance = balancefile.readline()
              print("User balance is now " + str(balance))
          else:
            print("Canceled")
      except:
        print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")

    elif userInput[0] == "add":
      try:
        with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
          balance = balancefile.readline()
          print("  " + userInput[1] + "'s balance is " + str(balance) + ", add " + str(float(userInput[2])) + "?")
          confirm = input("  Y/n")
          if confirm == "Y" or confirm == "y" or confirm == "":
            with open("balances/" + str(userInput[1]) + ".txt", "w") as balancefile:
              balancefile.write(str(float(balance)+float(userInput[2])))
            with open("balances/" + str(userInput[1]) + ".txt", "r") as balancefile:
              balance = balancefile.readline()
              print("User balance is now " + str(balance))
          else:
            print("Canceled")
      except:
        print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")
threading.Thread(target=InputManagement).start()

class ClientThread(threading.Thread): ######################## USER THREAD ########################
  def __init__(self, ip, port, clientsock):
    threading.Thread.__init__(self)
    self.ip = ip
    self.port = port
    self.clientsock = clientsock
    clientsock.send(bytes(VER, encoding='utf8'))


  def run(self):
    global server_info, hashrates, thread_id, diff, data, users, miners, registration_count
    username = ""
    thread_id = str(threading.current_thread().ident)
    server = self.clientsock

    while True:
      try:
        data = self.clientsock.recv(1024)
        if data:
          try:
            data = data.decode().rstrip('\n').lstrip('\n').split(",")
          except:
            break
        else:
          break
      except:
        break

      ######################## REGISTRATION SECTION ########################
      if data[0] == "REGI":
        username = data[1]
        password = data[2]
        email = data[3]
        registration_count += 1
        ServerLog("Client "+str(username)+" requested account registration.")

        # Check username and password for unallowed characters
        if re.match(regex,username) and re.match(regex,password) and len(username) < 18 and len(password) < 18 and 5 == 2:
          ServerLog("Client "+str(username)+" requested account registration.")
          hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
          server_info['miners'] += 1

          # Check if user already exists
          if not Path("users/" + username + ".txt").is_file() and not Path("emails/" + email + ".txt").is_file():
            eregex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if(re.search(eregex,email)):  
                message = MIMEMultipart("alternative")
                message["Subject"] = "Welcome to Duino-Coin network! " + u"\U0001F44B"
                message["From"] = duco_email
                message["To"] = email

                # Text version
                text = """\ 
                Hi, """+str(username)+"""!
                Your e-mail address has been successfully verified and you are now registered on Duino-Coin network!
                If you have any difficulties there are a lot of guides on our website: https://duinocoin.com/getting-started 
                You can also join our Discord server: https://discord.gg/kvBkccy to chat, take part in giveaways, trade and get help from other Duino-Coin users.
                Happy mining!
                Duino-Coin Team"""

                # HTML version
                html = """\
                <html>
                  <body>
                    <img src="https://i.imgur.com/0UJK85H.png" width="40%" height="auto"><br>
                    <h3>Hi, """+str(username)+"""!</h3>
                    <h4>Your e-mail address has been successfully verified and you are now registered on Duino-Coin network!</h4>
                    <p>If you have any difficulties there are a lot of <a href="https://duinocoin.com/getting-started">guides on our website</a>.<br> 
                       You can also join our <a href="https://discord.gg/kvBkccy">Discord server</a> to chat, take part in giveaways, trade and get help from other Duino-Coin users.<br><br>
                       Happy mining!<br>
                       <italic>Duino-Coin Team</italic>
                    </p>
                  </body>
                </html>
                """

                try:
                  # Turn these into plain/html MIMEText objects
                  part1 = MIMEText(text, "plain")
                  part2 = MIMEText(html, "html")
                  message.attach(part1)
                  message.attach(part2)

                  # Create secure connection with server and send email
                  context = ssl.create_default_context()
                  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtpserver:
                    smtpserver.login(duco_email, duco_password)
                    smtpserver.sendmail(duco_email, email, message.as_string())
                  ServerLog("Sent e-mail after registering user "+str(username))

                  # If user dosen't exist, save his password, email and balance
                  with open("users/" + username + ".txt", "w") as passwordfile:
                    passwordfile.write(password)
                  with open("emails/" + email + ".txt", "w") as usernamefile:
                    usernamefile.write(username)
                  with open("balances/" + username + ".txt", "w") as balancefile:
                    balancefile.write(str(".0"))

                  ServerLog("New user (" + username + ") registered")
                  server.send(bytes("OK", encoding='utf8'))
                    
                except:
                  ServerWarning("Error sending e-mail for user "+str(username)+" with e-mail: "+str(email))
                  server.send(bytes("OK", encoding='utf8'))
                  break

            else:
                ServerWarning("Invalid e-mail of user "+str(username)+" with e-mail: "+str(email))
                server.send(bytes("NO,E-mail is invalid", encoding='utf8'))
                break

          else:
            # User arleady exists, disconnect
            ServerLog("Account "+str(username)+" already exists!")
            server.send(bytes("NO,This account already exists", encoding='utf8'))
            break
        else:
          # User used unallowed characters, disconnect
          ServerLog("Unallowed characters used by "+str(username))
          server.send(bytes("NO,Registration temporarily disabled", encoding='utf8'))
          break

      ######################## LOGIN SECTION ########################
      elif data[0] == "LOGI":
        username = data[1]
        password = data[2]
        
        # Check username for unallowed characters (regex)
        if re.match(regex,username):
          server_info['miners'] += 1
          hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}

          # Check if that user exists
          try:
            # User exists, read his password
            with open("users/" + username + ".txt", "r") as usernamefile:
              usernamefile = usernamefile.read()
              filecont = usernamefile.splitlines()
          except:
            # Doesnt exist, disconnect
            #ServerLog("User "+str(username)+" doesn't exist!")
            #ServerLog("IP delikwenta: " + str(server.getpeername()))
            server.send(bytes("NO,This user doesn't exist", encoding='utf8'))
            break

          # Compare saved password with received password
          if password == filecont[0]:
            # Password matches
            try:
              server.send(bytes("OK", encoding='utf8'))
            except:
              break
            # Update statistics username
            try:
              hashrates[int(thread_id)]["username"] = username
            except:
              pass
          else:
            # Bad password, disconnect
            ServerLog("Incorrect password! " + password + " used by " + username)
            server.send(bytes("NO,Password is invalid", encoding='utf8'))
            break
        else:
          # User used unallowed characters, disconnect
          ServerLog("User "+str(username)+" used unallowed characters")
          ServerLog("IP: " + str(server.getpeername()) + " OR " + str(server.getsockname()))
          server.send(bytes("NO,You have used unallowed characters", encoding='utf8'))
          break

      ######################## MINING SECTION ########################
      elif data[0] == "JOB":
        try:
          username = data[1]
        except:
          pass

        blockFound = False
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}

        if supplyleft > 0:
          with locker:
            # Read lastblock's hash
            try:
                with open("config/lastblock", "r+") as lastblockfile:
                    lastblock = lastblockfile.readline()
            except:
                tcpsock.shutdown(socket.SHUT_RDWR)
                tcpsock.close()
                Warning("Restarting the server because of too many open files")
                time.sleep(1)
                os.execl(sys.executable, sys.executable, *sys.argv)

            # Read blocks amount
            with open("config/blocks", "r+") as blocksfile:
              blocks = int(blocksfile.readline())

            # Calculate difficulty
            try:
              diff = math.ceil(blocks / diff_incrase_per)
            except:
              diff = 10000
            rand = random.randint(1, 100 * diff)

            # Generate next block hash
            newBlockHash = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8")).hexdigest()

            try:
              # Send target hash to miner
              server.send(bytes(lastblock + "," + newBlockHash + "," + str(diff), encoding='utf8'))
              jobsent = datetime.datetime.now()
            except:
              break

            # Update lastblock's hash
            with open("config/lastblock", "r+") as lastblockfile:
              lastblockfile.seek(0)
              lastblockfile.write(newBlockHash)
              lastblockfile.truncate()

          try:
            # Wait until client solves hash
            response = server.recv(1024).decode()
            resultreceived = datetime.datetime.now()
          except:
            break

          # Add miner hashrate to statistics
          #try:
          if response.find(",") != -1:
            try:
              response = response.split(",")
              result = response[0]
              hashrate = response[1]
              if int(hashrate) > 0:
                
                hashrates[int(thread_id)]["hashrate"] = int(hashrate)
                server_info["pool_hashrate"] += int(hashrate) # TODO
              else:
                hashrates[int(thread_id)]["hashrate"] = 1000
                server_info["pool_hashrate"] += 1000
            except:
              pass
          else: # Arduino Miner compatibility
            try:
              result = response
              hashrates[int(thread_id)]["hashrate"] = 1000
              server_info["pool_hashrate"] += 1000
            except:
              pass
          #except:
            #pass
          #
          sharetime = resultreceived - jobsent # Time from start of hash computing to finding the result
          sharetime = int(sharetime.microseconds / 1000) # Convert to ms

          if result == str(rand) and int(sharetime) > 80:
            # Rewarding user for good hash
            with locker: # Using locker to fix problems when mining on many devices with one account
              try:
                  with open("balances/" + username + ".txt", "r") as bal:
                    balance = str(bal.readline()).rstrip("\n\r ")
              except:
                  server.send(bytes("INVU", encoding="utf8"))
                  break
              
              reward = int(int(sharetime) **2) / 450000000
              if random.randint(1, 10000000) == 77: # Low probability to find big block
                now = datetime.datetime.now()
                now = now.strftime("%d/%m/%Y %H:%M")
                newBlock = "Date: "+str(now)+" Miner: "+str(username)+" Hash: "+str(newBlockHash)+"\n"

                ServerLog("Block found")
                ServerLog(newBlock.rstrip("\n").lstrip("\n"))

                with open("config/foundBlocks", "a+") as foundBlocks:
                  foundBlocks.write(str(newBlock))

                reward += 7
                blockFound = True
              try:
                balance = float(balance) + float(reward)
                with open("balances/" + username + ".txt", "w") as bal:
                  bal.seek(0)
                  bal.write(str(balance))
              except:
                Warning("Error with "+str(username)+"'s' balance!")

            try:
              if blockFound:
                server.send(bytes("BLOCK", encoding="utf8"))
              else:
                server.send(bytes("GOOD", encoding="utf8"))
            except:
              break

            # Waiting fo unlocked files then lock them
            with locker:
              # Update amount of blocks
              blocks += 1
              with open("config/blocks", "w") as blo:
                blo.seek(0)
                blo.write(str(blocks))
          else:
            # If result is bad send "BAD"
            try:
                with open("balances/" + username + ".txt", "r") as bal:
                    balance = str(bal.readline()).rstrip("\n\r ")
                if float(balance) > .00000005:
                    balance = float(balance) - .00000005
                    with open("balances/" + username + ".txt", "w") as bal:
                        bal.seek(0)
                        bal.write(str(balance))
            except:
                Warning("Error with "+str(username)+"'s' balance!")
            try:
              server.send(bytes("BAD", encoding="utf8"))
            except:
              break
        else:
          try:
            server.send(bytes("BAD", encoding="utf8"))
          except:
            break
          
      ######################## LOW DIFF MINING SECTION ########################
      elif data[0] == "Job" or data[0] == "JOBLDIFF":
        try:
          username = data[1]
        except:
          pass
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        # Wait for unlocked files then lock them
        if supplyleft > 0:
          with locker:
            # Read lastblock's hash
            with open("config/lastblock", "r+") as lastblockfile:
              lastblock = lastblockfile.readline()

            # Read blocks amount
            with open("config/blocks", "r+") as blocksfile:
              blocks = int(blocksfile.readline())

            diff = 1500 # fixed diff for low power devices

            # Generate next block hash
            rand = random.randint(1, 1500)
            newBlockHash = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8")).hexdigest()

            try:
              # Send target hash to miner
              server.send(bytes(lastblock + "," + newBlockHash + "," + str(diff), encoding='utf8'))
              time.sleep(.055)
              jobsent = datetime.datetime.now()
            except:
              break

            # Update lastblocks hash
            with open("config/lastblock", "r+") as lastblockfile:
              lastblockfile.seek(0)
              lastblockfile.write(newBlockHash)
              lastblockfile.truncate()

          try:
            # Wait until client solves hash
            response = server.recv(1024).decode()
            resultreceived = datetime.datetime.now()
          except:
            break

          # Add miner hashrate to statistics
          try:
            if response.find(",") != -1:
              try:
                response = response.split(",")
                result = response[0]
                hashrate = response[1]
                if int(hashrate) > 0:
                    hashrates[int(thread_id)]["hashrate"] = int(hashrate)
                    server_info["pool_hashrate"] += int(hashrate) # TODO
                else:
                    hashrates[int(thread_id)]["hashrate"] = 1000 #1kH/s
                    server_info["pool_hashrate"] += 1000
              except:
                pass
            else: # Arduino Miner compatibility
              try:
                result = response
                hashrates[int(thread_id)]["hashrate"] = 1000 #1kH/s
                server_info["pool_hashrate"] += 1000
              except:
                pass
          except:
            pass

          #server_info["pool_hashrate"] += int(hashrate)
          sharetime = resultreceived - jobsent # Time from start of hash computing to finding the result
          sharetime = int(sharetime.microseconds / 1000) # Convert to ms

          # Checking received result
          if result == str(rand) and int(sharetime) > 50: # TODO
            # Rewarding user for good hash
            with locker: # Using locker to fix problems when mining on many devices with one account
              try:
                with open("balances/" + username + ".txt", "r") as bal:
                  balance = str(float(bal.readline())).rstrip("\n\r ")
              except:
                server.send(bytes("INVU", encoding="utf8"))
                break

              reward = int(int(sharetime) **2) / 450000000
              
              balance = float(balance) + float(reward)
              with open("balances/" + username + ".txt", "w") as bal:
                bal.seek(0)
                bal.write(str(balance))
                bal.truncate()

            try:
              server.send(bytes("GOOD", encoding="utf8"))
            except:
              break

            # Waiting fo unlocked files then lock them
            with locker:
              # Update amount of blocks
              blocks += 1
              with open("config/blocks", "w") as blo:
                blo.seek(0)
                blo.write(str(blocks))

          else:
            # If result is bad send "BAD"
            try:
              server.send(bytes("BAD", encoding="utf8"))
            except:
              break
        else:
          try:
            server.send(bytes("BAD", encoding="utf8"))
          except:
            break
        time.sleep(.025)

      ######################## LOW DIFF MINING SECTION ########################
      elif data[0] == "Job2" or data[0] == "JOBAVR":
        try:
          username = data[1]
        except:
          pass
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        # Wait for unlocked files then lock them
        if supplyleft > 0:
          with locker:
            # Read lastblock's hash
            with open("config/lastblock", "r+") as lastblockfile:
              lastblock = lastblockfile.readline()

            # Read blocks amount
            with open("config/blocks", "r+") as blocksfile:
              blocks = int(blocksfile.readline())

            diff = 300 # fixed diff for low power devices

            # Generate next block hash
            rand = random.randint(1, 250)
            newBlockHash = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8")).hexdigest()

            try:
              # Send target hash to miner
              server.send(bytes(lastblock + "," + newBlockHash + "," + str(diff), encoding='utf8'))
              time.sleep(.055)
              jobsent = datetime.datetime.now()
            except:
              break

            # Update lastblocks hash
            with open("config/lastblock", "r+") as lastblockfile:
              lastblockfile.seek(0)
              lastblockfile.write(newBlockHash)
              lastblockfile.truncate()

          try:
            # Wait until client solves hash
            response = server.recv(1024).decode()
            resultreceived = datetime.datetime.now()
          except:
            break

          # Add miner hashrate to statistics
          try:
            if response.find(",") != -1:
              try:
                response = response.split(",")
                result = response[0]
                hashrate = response[1]
                if int(hashrate) > 0:
                    hashrates[int(thread_id)]["hashrate"] = int(hashrate)
                    server_info["pool_hashrate"] += int(hashrate) # TODO
                else:
                    hashrates[int(thread_id)]["hashrate"] = 1000 #1kH/s
                    server_info["pool_hashrate"] += 1000
              except:
                pass
            else: # Arduino Miner compatibility
              try:
                result = response
                hashrates[int(thread_id)]["hashrate"] = 1000 #1kH/s
                server_info["pool_hashrate"] += 1000
              except:
                pass
          except:
            pass

          #server_info["pool_hashrate"] += int(hashrate)
          sharetime = resultreceived - jobsent # Time from start of hash computing to finding the result
          sharetime = int(sharetime.microseconds / 1000) # Convert to ms

          # Checking received result
          if result == str(rand) and int(sharetime) > 50: # TODO
            # Rewarding user for good hash
            with locker: # Using locker to fix problems when mining on many devices with one account
              try:
                with open("balances/" + username + ".txt", "r") as bal:
                  balance = str(float(bal.readline())).rstrip("\n\r ")
              except:
                server.send(bytes("INVU", encoding="utf8"))
                break

              reward = int(int(sharetime) **2) / 450000000
              
              balance = float(balance) + float(reward)
              with open("balances/" + username + ".txt", "w") as bal:
                bal.seek(0)
                bal.write(str(balance))
                bal.truncate()

            try:
              server.send(bytes("GOOD", encoding="utf8"))
            except:
              break

            # Waiting fo unlocked files then lock them
            with locker:
              # Update amount of blocks
              blocks += 1
              with open("config/blocks", "w") as blo:
                blo.seek(0)
                blo.write(str(blocks))

          else:
            # If result is bad send "BAD"
            try:
              server.send(bytes("BAD", encoding="utf8"))
            except:
              break
        else:
          try:
            server.send(bytes("BAD", encoding="utf8"))
          except:
            break
        time.sleep(.025)

      ######################## CHECK USER STATUS SECTION ########################
      elif username != "" and data[0] == "STAT": # TODO
        foundEmail = "NoEmail"
        for file in os.listdir("emails/"):
          with open("emails/" + file, "r") as emailcont:
            if username in emailcont:
              foundEmail = str(emailcont.readline())

        server.send(bytes(str(foundEmail), encoding='utf8'))

      ######################## CLIENT INFO SECTION ########################
      #elif data[0] == "FROM": # TODO
        #with open("userdata/" + str(username) + ".txt", "a") as userdatafile:
          #writableUserData = data
          #try:
            #writableUserData.pop(0) # Remove "FROM"
            #userdatafile.writelines(" ".join(writableUserData) + "\n")
          #except:
            #pass
  
      ######################## PASSWORD CHANGE SECTION ########################
      elif username != "" and data[0] == "CHGP":
        oldPassword = data[1]
        newPassword = data[2]
        ServerLog("Client request changing password")
        
        try:
          with open("users/" + username + ".txt", "r") as usernamefile:
            lines = usernamefile.readlines()
            serverOldPassword = lines[0]
            serverOldPassword = serverOldPassword.replace("\n", "")
        except:
          Warning("Can't check clients' username for changing password")

        if str(serverOldPassword) == str(oldPassword):
          with open("users/" + username + ".txt", "r") as usernamefile:
            lines = usernamefile.readlines()

          with open("users/" + username + ".txt", "w") as usernamefile:
            lines[0] = str(newPassword)
            usernamefile.writelines(lines)
          
          try:
            server.send(bytes("Success! Your password has been changed.", encoding='utf8'))
          except:
            break
        else:
          try:
            server.send(bytes("Error! Your old password doesn't match!", encoding='utf8'))
          except:
            break
          
      ######################## SENDING SECTION ########################
      elif username != "" and data[0] == "SEND":
        try:
            sender = str(username)
            receiver = str(data[2])
            amount = float(data[3])
            ServerLog("Client request transfer funds")

            # Get current amount of funds
            try:
              with open("balances/" + str(sender) + ".txt", "r+") as balancefile:
                balance = float(balancefile.readline())
            except:
              ServerLog("Can't checks senders' (" + str(sender) + ") balance")

            # Verify that the balance is higher or equal to transfered amount
            if float(balance) <= float(amount) or str(receiver) == str(sender) or float(amount) <= 0:
              try:
                server.send(bytes("Error! Your balance is lower than amount you want to transfer or you're sending funds to yourself!", encoding='utf8'))
              except:
                break

            if float(balance) >= float(amount) and str(receiver) != str(sender) and float(amount) >= 0: # Check if recipient adress exists
              if Path("balances/" + receiver + ".txt").is_file():
                try:
                  # Remove amount from senders' balance
                  balance -= amount
                  with open("balances/" + str(sender) + ".txt", "r+") as balancefile:
                    balancefile.seek(0)
                    balancefile.write(str(balance))

                  # Get receipents' balance and add transferred amount
                  with open("balances/" + str(receiver) + ".txt", "r+") as receiverfile:
                    receiverbal = float(receiverfile.readline())
                    receiverbal += amount
                    receiverfile.seek(0)
                    receiverfile.write(str(receiverbal))

                  try:
                    server.send(bytes("Successfully transferred funds!", encoding='utf8'))
                  except:
                    break
                  ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + receiver)

                except:
                  try:
                    server.send(bytes("Error! Unknown error occured while sending funds. Try again later.", encoding='utf8'))
                    Warning("Unknown error while sending funds")
                  except:
                    break

              else: # Send message if receipent doesn't exist
                ServerLog("The recepient "+receiver+" doesn't exist!")
                try:
                  server.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
                except:
                  break
        except:
            try:
                server.send(bytes("Error! Unknown error occured while sending funds. Try again later.", encoding='utf8'))
                Warning("Unknown error while sending funds")
            except:
                break
            
      ######################## BALANCE CHECK SECTION ########################
      elif username != "" and data[0] == "BALA":
        with open("balances/" + username + ".txt", "r") as balancefile:
          balance = balancefile.readline()

        try:
          server.send(bytes(balance, encoding='utf8'))
        except:
          break


    server.close()

    #try:
    #del hashrates[int(thread_id)]
    #except:
      #try:
        #del hashrates[str(thread_id)]
      #except:
        #try:
          #del hashrates[thread_id]
        #except:
    hashrates.pop(thread_id, None)

    users = users.replace(" "+str(username), "")
    server_info['miners'] -= 1

    sys.exit(0)
    time.sleep(1)
      
######################## VARIABLES ########################
Watchdog("Server declares it's reading setup variables")
regex = r'^[\w\d_()]*$'
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
threads = []
server_info = {'miners' : 0, 'pool_hashrate' : 0, 'users' : 0}
userinfo = ""
hashrates = {}
config = configparser.ConfigParser()
locker = threading.Lock()
update_count = 0
users = ""
xmgusd = .014541
supply = 35000000 # 35 million circulating supply
VER = "1.7" # Version number
smtp_server = "smtp.xxx.com"
duco_email = "xxx" # Enter your address
registration_count = 0
duco_password = "xxx"

config.read("config/config.ini")
host = config['server']['host']
port = 14808
new_user_balance = config['server']['new_user_bal']
diff_incrase_per = config['server']['diff_incrase_per']
gitusername = config['server']['gitusername']
gitpassword = config['server']['gitpassword']
gitrepo = config['server']['gitrepo']
port = int(port)
diff_incrase_per = int(diff_incrase_per)
Watchdog("Server declares it finished reading setup variables")

######################## BIND SOCKETS ########################
try:
  tcpsock.bind((host, port))
  Watchdog("Server declares it binded TCP socket")
except:
  Warning("Server reports problems binding TCP socket")
  raise

######################## MAIN LOOP ########################
threading.Thread(target=Backuper).start()
GenerateAPIfile()

# Start thread for updating server info api
Watchdog("Server declares it's now listening for incoming connections")
while True:
  try:
    # Listen for new connections
    tcpsock.listen(1)
    (conn, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)
  except:
    Warning("Server reports problems listening to new connections. Restarting")
    tcpsock.shutdown(socket.SHUT_RDWR)
    tcpsock.close()
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)

for t in threads:
  t.join()
  t.setDaemon(True)
