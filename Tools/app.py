import time
import json
from datetime import datetime
from urllib.request import urlopen

datetimenow = datetime.now()

#username
'''
with open("src/userinfo") as userinfo:
    username = userinfo.read().rstrip()
'''
username = input("Enter your username here: ")
# DEBUG: for debuging (remove the hashtag to sea the results)
#print(username)

#getapi
# api source :
# 'https://server.duinocoin.com/users/ + your_username'
# 'https://duco.sytes.net/api/rewards.php/" + username'

api = "https://server.duinocoin.com/users/" + username
api2 = "https://duco.sytes.net/api/rewards.php/" + username
read = json.loads(urlopen(api).read())
read2 = json.loads(urlopen(api2).read())
# DEBUG: for debuging (remove the hashtag to sea the results)
#print(api)
#print(read)
#print(api2)
#print(read2)

#apimapping
result = read['result']
tempbalance = result['balance']
mainbalance = tempbalance['balance']
mainuser = tempbalance['username']
stake = tempbalance['stake_amount']
miners = result['miners']
result2 = read2['data']
daily_income = result2['daily_2m']
# DEBUG: for debuging (remove the hashtag to sea the results)
#print(result)
#print(tempbalance)
#print(mainbalance)
#print(stake)
#print(miners)
#print(result2)
#print(daily_income)

print("")
print("------------------------------------------------------------------------")
print("")
print("Profile")
print("")

#userinfo (profile)
print("Username: " + str(mainuser))
print("Estimated Daily Income: " + str(daily_income))
print("Total Balance: " + str(mainbalance))
print("Stakes: " + str(stake))

#minerslist
minerlist = len(miners)
print("Total Active Miner is: " + str(minerlist))
print("Date and Time: " + str(datetimenow))

print("")
print("------------------------------------------------------------------------")
print("")
print("Miner Info")
print("")
# display the miners info (total display upto 10)
if minerlist == 0:
    print("No Miners Active")
elif minerlist == 1:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 2:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 3:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 4:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 5:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 6:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[5]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.6")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 7:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[5]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.6")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[6]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.7")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 8:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[5]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.6")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[6]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.7")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[7]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.8")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 9:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[5]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.6")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[6]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.7")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[7]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.8")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[8]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.9")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
elif minerlist == 10:
    maindata = miners[0]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.1")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[1]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.2")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[2]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.3")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[3]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.4")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[4]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.5")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[5]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.6")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[6]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.7")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[7]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.8")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[8]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.9")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
    maindata = miners[9]
    data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
    minername, a, b, c, d, e, f, g = data
    print("Miner no.10")
    print("Miner: " + str(minername))
    print("Identifier: " + str(a))
    print("Algorithm: " + str(b))
    print("Hashrate: " + str(c))
    print("Difficulty: " + str(d))
    print("Total accepted: " + str(e))
    print("Total rejected: " + str(f))
    print("Pool: " + str(g))
    print("")
else:
    print("Sorry we can't show your miners")

print("")
print("------------------------------------------------------------------------")

"""
next update soon:
use for loop
add total hashrate in profile
maybe gui version
"""
