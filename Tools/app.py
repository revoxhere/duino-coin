import os
import time
import json
from datetime import datetime
from urllib.request import urlopen

#username
username = input("Enter your username here: ")

def main():
    while True:
        os.system('cls||clear')
        datetimenow = datetime.now()

        #getapi
        # api source :
        # 'https://server.duinocoin.com/users/ + username'
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
        print("----------------------------------------------------")
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
        print("----------------------------------------------------")
        print("Miner Info")
        print("")
        # display the miners info
        z = 0
        x = 1
        if minerlist == 0:
            print("No Miners Active")
        elif minerlist == 50:
            print("Sorry we can't show your miners")
        else:
            for maindata in result['miners']:
              data = maindata['software'], maindata['identifier'], maindata['algorithm'], maindata['hashrate'], maindata['diff'], maindata['accepted'], maindata['rejected'], maindata['pool']
              minername, a, b, c, d, e, f, g = data
              print("Miner no." + str(x))
              print("Miner: " + str(minername))
              print("Identifier: " + str(a))
              print("Algorithm: " + str(b))
              print("Hashrate: " + str(c))
              print("Difficulty: " + str(d))
              print("Total accepted: " + str(e))
              print("Total rejected: " + str(f))
              print("Pool: " + str(g))
              print("")
              if x == minerlist:
                break
              z += 1
              x += 1

        print("")
        print("----------------------------------------------------")
        time.sleep(10)


main()
#"Please zoom out to see the full screen"

"""
next update soon:
add total hashrate in profile
maybe gui version
"""
