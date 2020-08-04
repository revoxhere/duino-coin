#!/usr/bin/env python3
##########################################
# Duino-Coin Server (v1.5) 
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# This file doesn't contain API keys and password used by Duino-Coin server. They were replaced with 'xxx'
# © revox, MrKris7100 2020
##########################################
import socket, threading, time, random, glob, hashlib, math, datetime, re, configparser, sys, errno, os, psutil, string, json
from pathlib import Path
from collections import OrderedDict
from github import Github

from natsort import natsorted

import requests, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import shutil
from datetime import date

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def ServerLog(whattolog):
  now = datetime.datetime.now()
  now = now.strftime("%H:%M:%S")
  print(now, whattolog)

def ServerWarning(whattolog): # Warning section
  print("!!! " + whattolog + " !!!")

def search(myDict, search1):
    search.a=[]
    for key, value in myDict.items():
        if search1 in value:
            search.a.append(key)

def Backup():
  today = date.today()
  if not os.path.isdir('backups/'+str(today)+'/'):
    ServerLog("Backup for today ("+str(today)+") started")
    try:
      os.makedirs("backups/"+str(today)+"/balances")
      os.makedirs("backups/"+str(today)+"/emails")
      os.makedirs("backups/"+str(today)+"/users")
    except:
      pass
    copytree("balances/", "backups/"+str(today)+"/balances/")
    copytree("emails/", "backups/"+str(today)+"/emails/")
    copytree("users/", "backups/"+str(today)+"/users/")
    ServerLog("Backup for today ("+str(today)+") finished")
  
def UpdateServerInfo(): ######################## API PROTOCOL ########################
  global server_info, hashrates, threads, diff, update_count, gitrepo, miners, gitusername, rewardap, blocks, userinfo
  global supplyleft, minedBlocks

  threading.Timer(3.0, UpdateServerInfo).start()

  now = datetime.datetime.now()
  now = now.strftime("%d/%m/%Y %H:%M")

  miners = []
  res = []
  leadersdata = []
  server_info['pool_hashrate'] = 0
  server_info['users'] = len(os.listdir('users'))
  allmined = 0

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

  coingecko = requests.get("https://api.coingecko.com/xxx", data = None)
  if coingecko.status_code == 200:
    geckocontent = coingecko.content.decode()
    geckocontentjson = json.loads(geckocontent)
    xmgusd = float(geckocontentjson["magi"]["usd"])
  else:
    xmgusd = 0.02

  workersNumber = str(len(res))
  workersList = str(" (") + str(', '.join(map(str, res))) + str(")")
  usersNumber = str(server_info["users"])

  rand = random.randint(2500,3100)
  rand = rand / 1000
  ducousdLong = float(xmgusd) * float(rand)
  ducoPrice = round(float(ducousdLong) / int(10), 8) 

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
    lastblok = open("config/lastblock", "r+")
    lastblokid = lastblok.readline().rstrip("\n\r ")
    lastblockHash = str(lastblokid)[:10]+"..."
    lastblok.close()

  with locker: # Difficulty and mined blocks
    blok = open("config/blocks", "r")
    minedBlocks = blok.readline()
    blok.close()
    difficulty = math.ceil(int(minedBlocks) / int(diff_incrase_per))
    supplyleft = int(supply) - int(minedBlocks) # Remaining blcks

  with locker:
      foundb = open("config/foundBlocks", "r")
      foundBlocks = foundb.read().splitlines()
      foundb.close()

  if workersList == " ()":
    workersList = " (No active workers)"

  for filename in os.listdir("balances/"): # All-time mined duco
    if filename.endswith(".txt"):
        try:
          with locker:
            f = open("balances/"+filename)
            lines = f.read()
            allmined += float(lines)
          continue
        except Exception:
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
          leadersdata.append(leaderline + " DUCO - " + leaderfile.replace("balances\\", "").replace(".txt", ""))
        except:
          Warning(leaderfile + " has problems with the balance!")
  leadersdata = natsorted(leadersdata, reverse=True) # Sort in descending order
  
  ########## PREPARE JSON #########
  jsonfile = open("config/api.json", "w")
  jsonapi = json.dumps(
    {
     'Server version': str(VER),
     'Last update': str(now)+str(" (GMT+1)"),
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
     'Full last block hash': str(lastblokid),
     'Big blocks and finders': str(", ").join(foundBlocks)}
     , sort_keys=False, indent=4)

  jsonfile.write(str(jsonapi))
  jsonfile.close()

class ClientThread(threading.Thread): ######################## USER THREAD ########################
  def __init__(self, ip, port, clientsock):
    threading.Thread.__init__(self)
    self.ip = ip
    self.port = port
    self.clientsock = clientsock

    try:
      # Send server version to client
      clientsock.send(bytes(VER, encoding='utf8'))
    except socket.error as err:
      if err.errno == errno.ECONNRESET:
        err = True

  def run(self):
    global server_info, hashrates, thread_id, diff, data, users, miners, registration_count
    err = False
    username = ""
    thread_id = str(threading.current_thread().ident)

    while True:

      try:
        # Listen for requests from clients
        data = self.clientsock.recv(1024)
      except socket.error as err:
        if err.errno == errno.ECONNRESET:
          break

      if data:
        try:
          data = data.decode().rstrip('\n').lstrip('\n').split(",")
        except:
          break
      else:
        break

      ######################## REGISTRATION PROTOCOL ########################
      if data[0] == "REGI":
        username = data[1]
        password = data[2]
        email = data[3]
        server_info['miners'] += 1
        registration_count += 1
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        ServerLog("Client "+str(username)+" requested account registration.")

        # Check username and password for unallowed characters
        if re.match(regex,username) and re.match(regex,password) and len(username) < 18 and len(password) < 18:
          ServerLog("Client "+str(username)+" requested account registration.")
          server_info['miners'] += 1
          hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}

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
                If you have any difficulties there are a lot of guides on our website: https://revoxhere.github.io/duino-coin/getting-started 
                You can also join our Discord server: https://discord.gg/KyADZT3 to chat, take part in giveaways, trade and get help from other Duino-Coin users.
                Happy mining!
                Duino-Coin Team"""

                # HTML version
                html = """\
                <html>
                  <body>
                    <img src="https://i.imgur.com/0UJK85H.png" width="40%" height="auto"><br>
                    <h3>Hi, """+str(username)+"""!</h3>
                    <h4>Your e-mail address has been successfully verified and you are now registered on Duino-Coin network!</h4>
                    <p>If you have any difficulties there are a lot of guides on <a href="https://revoxhere.github.io/duino-coin/getting-started">our website</a>.<br> 
                       You can also join our <a href="https://discord.gg/KyADZT3">Discord server</a> to chat, take part in giveaways, trade and get help from other Duino-Coin users.<br><br>
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
                    with smtplib.SMTP_SSL("xxx.xxx.xxx", 465, context=context) as server:
                        server.login(duco_email, duco_password)
                        server.sendmail(duco_email, email, message.as_string())
                    ServerLog("Sent e-mail after registering user "+str(username))

                    # If user dosen't exist, save his password, email and balance
                    file = open("users/" + username + ".txt", "w")
                    file.write(password)
                    file.close()

                    file = open("emails/" + email + ".txt", "w")
                    file.write(username)
                    file.close()

                    file = open("balances/" + username + ".txt", "w")
                    file.write(str("0.0"))
                    file.close()

                    ServerLog("New user (" + username + ") registered")
                    self.clientsock.send(bytes("OK", encoding='utf8'))
                    
                except Exception:
                    ServerWarning("Error sending e-mail for user "+str(username)+" with e-mail: "+str(email))
                    self.clientsock.send(bytes("NO,Error checking e-mail", encoding='utf8'))
                    break

            else:
                ServerWarning("Invalid e-mail of user "+str(username)+" with e-mail: "+str(email))
                self.clientsock.send(bytes("NO,E-mail is invalid", encoding='utf8'))
                break

          else:
            # User arleady exists, disconnect
            ServerLog("Account "+str(username)+" already exists!")
            self.clientsock.send(bytes("NO,This account already exists", encoding='utf8'))
            break
        else:
          # User used unallowed characters, disconnect
          ServerLog("Unallowed characters used by "+str(username))
          self.clientsock.send(bytes("NO,You have used unallowed characters or data is too long", encoding='utf8'))
          break

      ######################## ADD EMAIL TO EXISTING ACCOUNT PROTOCOL ########################
      elif data[0] == "ADDEMAIL":
        username = data[1]
        password = data[2]
        email = data[3]
        # Check username for unallowed characters (regex)
        if re.match(regex,username) and re.match(regex,password):
          ServerLog("Client "+str(username)+" requested adding e-mail to account")
          server_info['miners'] += 1
          hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}

          # Check if that user exists
          try:
            # User exists, read his password
            file = open("users/" + username + ".txt", "r")
            file = file.read()
            filecont = file.splitlines()
          except Exception:
            # Doesnt exist, disconnect
            ServerLog("User "+str(username)+" doesn't exist!")
            self.clientsock.send(bytes("This account doesn't exist!", encoding='utf8'))
            break

          if filecont[0] == password and Path("users/" + username + ".txt").is_file() and not Path("emails/" + email + ".txt").is_file():
            
            eregex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if(re.search(eregex,email)): 
                message = MIMEMultipart("alternative")
                message["Subject"] = "Welcome to Duino-Coin network! " + u"\U0001F44B"
                message["From"] = duco_email
                message["To"] = email
                try:
                    # Text email version
                    text = """\ 
                    Hi, """+str(username)+"""!
                    Your e-mail address has been successfully verified and you are now registered on Duino-Coin network!
                    If you have any difficulties there are a lot of guides on our website: https://revoxhere.github.io/duino-coin/getting-started 
                    You can also join our Discord server: https://discord.gg/KyADZT3 to chat, take part in giveaways, trade and get help from other Duino-Coin users.
                    Happy mining!
                    Duino-Coin Team"""

                    # HTML email version
                    html = """\
                    <html>
                      <body>
                        <img src="https://i.imgur.com/0UJK85H.png" width="40%" height="auto"><br>
                        <h3>Hi, """+str(username)+"""!</h3>
                        <h4>Your e-mail address has been successfully verified and you are now registered on Duino-Coin network!</h4>
                        <p>If you have any difficulties there are a lot of guides on <a href="https://revoxhere.github.io/duino-coin/getting-started">our website</a>.<br> 
                           You can also join our <a href="https://discord.gg/KyADZT3">Discord server</a> to chat, take part in giveaways, trade and get help from other Duino-Coin users.<br><br>
                           Happy mining!<br>
                           <italic>Duino-Coin Team</italic>
                        </p>
                      </body>
                    </html>
                    """
                    # Turn these into plain/html MIMEText objects
                    part1 = MIMEText(text, "plain")
                    part2 = MIMEText(html, "html")
                    message.attach(part1)
                    message.attach(part2)

                    # Create secure connection with server and send email
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("xxx.xxx.xxx", 465, context=context) as server:
                        server.login(duco_email, duco_password)
                        server.sendmail(duco_email, email, message.as_string())
                    ServerLog("Sent e-mail after adding e-mail to user "+str(username))

                    file = open("emails/" + email + ".txt", "w")
                    file.write(username)
                    file.close()

                    self.clientsock.send(bytes("E-mail has been successfully added to your account.", encoding='utf8'))
                    
                except Exception:
                    ServerWarning("Error sending e-mail to user "+str(username))
                    self.clientsock.send(bytes("There was a fatal error checking your e-mail. Please try again later.", encoding='utf8'))
                    break

            else:
                ServerWarning("Invalid e-mail of user "+str(username)+" with e-mail: "+str(email))
                self.clientsock.send(bytes("This e-mail is invalid. Please use a valid one next time you'll launch your wallet.", encoding='utf8'))
                break

          else:
              # User arleady exists, disconnect
              ServerWarning("Error checking e-mail of user "+str(username)+" with e-mail: "+str(email))
              self.clientsock.send(bytes("There was a fatal error checking your e-mail. Please try again later.", encoding='utf8'))
              break

      ######################## LOGIN PROTOCOL ########################
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
            file = open("users/" + username + ".txt", "r")
            file = file.read()
            filecont = file.splitlines()
          except Exception:
            # Doesnt exist, disconnect
            ServerLog("User "+str(username)+" doesn't exist!")
            self.clientsock.send(bytes("NO,This user doesn't exist", encoding='utf8'))
            break

          # Compare saved password with received password
          if password == filecont[0]:
            # Password matches
            try:
              self.clientsock.send(bytes("OK", encoding='utf8'))
            except Exception:
              break
            # Update statistics username
            try:
              hashrates[int(thread_id)]["username"] = username
            except Exception:
              pass
          else:
            # Bad password, disconnect
            ServerLog("Incorrect password!    " + password)
            self.clientsock.send(bytes("NO,Password is invalid", encoding='utf8'))
            break
        else:
          # User doesn't exist, disconnect
          ServerLog("User "+str(username)+" doesn't exist!    " + password)
          self.clientsock.send(bytes("NO,You have used unallowed characters", encoding='utf8'))
          break
        time.sleep(0.05)

      ######################## MINING PROTOCOL ########################
      elif username != "" and data[0] == "JOB":
        blockFound = False
        # Wait for unlocked files then lock them
        if supplyleft > 0:
          with locker:
            # Read lastblock's hash
            file = open("config/lastblock", "r+")
            lastblock = file.readline()
            file.close()

            # Read blocks amount
            file = open("config/blocks", "r+")
            blocks = int(file.readline())
            file.close()

            # Calculate difficulty
            try:
                diff = math.ceil(blocks / diff_incrase_per)
            except Exception:
                diff = 10000
            rand = random.randint(1, 100 * diff)

            # Generate next block hash
            hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))

            try:
              # Send target hash to miner
              self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
            except Exception:
              break

            # Update lastblock's hash
            file = open("config/lastblock", "r+")
            file.seek(0)
            file.write(hashing.hexdigest())
            file.truncate()
            file.close()

          try:
            # Wait until client solves hash
            response = self.clientsock.recv(1024).decode()
          except Exception:
            break

          # Add miner hashrate to statistics
          try:
            if response.find(",") != -1:
              try:
                response = response.split(",")
                result = response[0]
                hashrate = response[1]
                if float(hashrate) > 0:
                    hashrates[int(thread_id)]["hashrate"] = float(hashrate)
                else:
                    hashrates[int(thread_id)]["hashrate"] = 0
              except Exception:
                pass
            else: # Arduino Miner compatibility
              try:
                result = response
                hashrates[int(thread_id)]["hashrate"] = 0
              except Exception:
                pass
          except Exception:
            pass

          # Checking received result
          if result == str(rand):
            # Rewarding user for good hash
            with locker: # Using locker to fix problems when mining on many devices with one account
              bal = open("balances/" + username + ".txt", "r")
              balance = str(float(bal.readline())).rstrip("\n\r ")
              
              reward = random.uniform(0.000256, 0.0000000888)
              if 0.000000889 > float(reward) > 0.000000884: # Low probability to find big block
                now = datetime.datetime.now()
                now = now.strftime("%d/%m/%Y %H:%M")
                newBlock = "Date: "+str(now)+" Miner: "+str(username)+" Hash: "+str(hashing.hexdigest())+"\n"

                ServerLog("Block found")
                ServerLog(newBlock.rstrip("\n").lstrip("\n"))

                foundBlocks = open("config/foundBlocks", "a+")
                foundBlocks.write(str(newBlock))
                foundBlocks.close()

                reward += 7.7
                blockFound = True
                
              balance = float(balance) + float(reward)
              bal = open("balances/" + username + ".txt", "w")
              bal.seek(0)
              bal.write(str(balance))
              bal.truncate()
              bal.close()

            try:
              if blockFound:
                self.clientsock.send(bytes("BLOCK", encoding="utf8"))
              else:
                self.clientsock.send(bytes("GOOD", encoding="utf8"))
            except Exception:
              break

            # Waiting fo unlocked files then lock them
            with locker:
              # Update amount of blocks
              blocks += 1
              blo = open("config/blocks", "w")
              blo.seek(0)
              blo.write(str(blocks))
              blo.close()
          else:
            # If result is bad send "BAD"
            try:
              self.clientsock.send(bytes("BAD", encoding="utf8"))
            except Exception:
              break
        else:
          try:
            self.clientsock.send(bytes("BAD", encoding="utf8"))
          except Exception:
            break

      ######################## CHECK USER STATUS PROTOCOL ########################
      elif username != "" and data[0] == "STAT":
        file = open("users/" + username + ".txt", "r")
        filecont = file.readlines()
        file.close()

        foundEmail = "NoEmail"
        for file in os.listdir("emails/"):
          emailcont = open("emails/" + file, "r")
          if username in emailcont:
            foundEmail = str(emailcont.readline())

        try:
                userstatus = filecont[1]
                self.clientsock.send(bytes(str(userstatus)+","+str(foundEmail), encoding='utf8'))
        except:
                self.clientsock.send(bytes("Member,"+str(foundEmail), encoding='utf8'))

        
      ######################## CLIENT INFO PROTOCOL ########################
      elif username != "" and data[0] == "FROM":
        try:
          if data[1]:
            client = data[1]
          if data[2]:
            pcusername = data[2]
          if data[3]:
            ip = data[3]
            country = requests.get('http://ip-api.com/line/'+str(ip)+'?fields=country')
            country = country.text
          if data[4]:
            platform = data[4]
          if data:
            ServerLog("Metrics from " + str(username) + ": " + str(client).rstrip() + " from " + str(country).rstrip() + " running on " + str(platform))
        except Exception:
          pass
        time.sleep(0.025)
  
      ######################## PASSWORD CHANGE PROTOCOL ########################
      elif username != "" and data[0] == "CHGP":
        time.sleep(0.025)
        oldPassword = data[1]
        newPassword = data[2]
        ServerLog("Client request changing password")
        
        try:
          file = open("users/" + username + ".txt", "r")
          lines = file.readlines()
          serverOldPassword = lines[0]
          serverOldPassword = serverOldPassword.replace("\n", "")
          file.close()
        except:
          ServerLog("Can't check clients' username")

        if str(serverOldPassword) == str(oldPassword):
          file = open("users/" + username + ".txt", "r")
          lines = file.readlines()
          file.close

          file = open("users/" + username + ".txt", "w")
          lines[0] = str(newPassword+"\n")
          file.writelines(lines)
          file.close()
          
          try:
            self.clientsock.send(bytes("Success! Your password has been changed.", encoding='utf8'))
          except:
            break
        else:
          try:
            self.clientsock.send(bytes("Error! Your old password doesn't match!", encoding='utf8'))
          except:
            break
          
      ######################## SENDING PROTOCOL ########################
      elif username != "" and data[0] == "SEND":
        time.sleep(0.001)
        sender = username
        receiver = data[2]
        amount = float(data[3])
        ServerLog("Client request transfer funds")

        # Get current amount of funds
        try:
          file = open("balances/" + sender + ".txt", "r+")
          balance = float(file.readline())
        except:
          ServerLog("Can't checks senders' (" + sender + ") balance")

        # Verify that the balance is higher or equal to transfered amount
        if amount > balance or receiver == sender or amount <= 0:
          try:
            self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer or you're sending funds to yourself!", encoding='utf8'))
          except:
            break

        else: # Check if recipient adress exists
          if Path("balances/" + receiver + ".txt").is_file():
            try:
              # Remove amount from senders' balance
              balance -= amount
              file.seek(0)
              file.write(str(balance))
              file.close()

              # Get receipents' balance and add transferred amount
              file = open("balances/" + receiver + ".txt", "r+")
              receiverbal = float(file.readline())
              receiverbal += amount
              file.seek(0)
              file.write(str(receiverbal))
              file.close()

              try:
                self.clientsock.send(bytes("Successfully transfered funds!", encoding='utf8'))
              except:
                break
              ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + receiver)

            except:
              try:
                self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
              except:
                break

          else: # Send message if receipent doesn't exist
            ServerLog("The recepient "+receiver+" doesn't exist!")
            try:
              self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
            except:
              break
            
      ######################## BALANCE CHECK PROTOCOL ########################
      elif username != "" and data[0] == "BALA":
        time.sleep(0.045)

        file = open("balances/" + username + ".txt", "r")
        balance = file.readline()
        file.close()

        try:
          self.clientsock.send(bytes(balance, encoding='utf8'))
        except:
          break

    # Close socket connection
    self.clientsock.close()
    # Delete this miner from statistics
    try:
      del hashrates[int(thread_id)]
    except:
      try:
        del hashrates[str(thread_id)]
      except:
        try:
          del hashrates[thread_id]
        except:
          hashrates.pop(thread_id, None)
    try:
      users = users.replace(" "+str(username), "")
      server_info['miners'] -= 1
    except:
      pass
    time.sleep(1)
      
######################## VARIABLES ########################
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
xmgusd = 0.015
supply = 35000000 # 35 million circulating supply
VER = "1.5" # Version number
smtp_server = "xxx.xxx.xxx"
duco_email = "xxx@xxx.xxx"  # Enter your address
registration_count = 0
duco_password = "xxx"


######################## INITIAL FILE CREATION ########################
if not Path("config").is_dir():
  os.mkdir("config")
if not Path("users").is_dir():
  os.mkdir("users")
if not Path("balances").is_dir():
  os.mkdir("balances")
if not Path("config/lastblock").is_file():
  file = open("config/lastblock", "w")
  file.write(hashlib.sha1(str("revox.heremrkris7100").encode("utf-8")).hexdigest()) #First block
  file.close()
if not Path("config/blocks").is_file():
  file = open("config/blocks", "w")
  file.write("1")
  file.close()

######################## INITIAL CONFIGURATION ########################
if not Path("config/config.ini").is_file():
  print("Initial server configuration\n")
  host = input("Enter server host adddress: ")
  port = input("Enter server port: ")
  new_user_balance = input("Default balance for new users: ")
  diff_incrase_per = input("How many blocks are needed for incrase difficulty: ")
  gitusername = input("GitHub username to push api to: ")
  gitpassword = input("GitHub password to push api to: ")
  gitrepo = input("GitHub repository name to push api to: ")
  config['server'] = {"host": host,
  "port": port,
  "new_user_bal": new_user_balance,
  "diff_incrase_per": diff_incrase_per,
  "gitusername": gitusername,
  "gitpassword": gitpassword,
  "gitrepo": gitrepo}
  with open("config/config.ini", "w") as configfile:
    config.write(configfile)
    
######################## LOAD CONFIGFILE ########################
else:
  config.read("config/config.ini")
  host = config['server']['host']
  port = config['server']['port']
  new_user_balance = config['server']['new_user_bal']
  diff_incrase_per = config['server']['diff_incrase_per']
  gitusername = config['server']['gitusername']
  gitpassword = config['server']['gitpassword']
  gitrepo = config['server']['gitrepo']
  port = int(port)
  diff_incrase_per = int(diff_incrase_per)

######################## BIND SOCKETS ########################
try:
  tcpsock.bind((host, port))
  ServerLog("Binded TCP socket")
except:
  Warning("Error binding TCP socket!")
  time.sleep(5)

######################## MAIN LOOP ########################
threading.Thread(target=Backup).start()
UpdateServerInfo()

ServerLog("Listening for incoming connections...")
# Start thread for updating server info api
while True:
  try:
    # Listen for new connections
    tcpsock.listen(1)
    (conn, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)
  except:
    ServerLog("Error in main loop!")
  time.sleep(0.025)

for t in threads:
  t.join()
