import requests, json
import time
import schedule




###dry run


f = open("/home/ubuntu/Faucet_Furimo/connect.txt", "r")

check_if_json = f.read()

if check_if_json != "json":
    print("i will do nothing because json does not work")
if check_if_json == "json":
    filename = "offers-backend.txt"
    with open(filename) as f_input:
        data = f_input.read().rstrip('\n')
    with open(filename, 'w') as f_output:    
        f_output.write(data)
    f = open("offers-backend.txt", "r")
    yes0 = f.read()
    yes1 = yes0.splitlines()
    open('offers-frontend.txt', 'w').close()
    for value in yes1:
        coingecko_api = requests.get(
        "https://api.coingecko.com/"
        + "api/v3/simple/price?ids=tron&vs_currencies=usd",
        data=None
        ).json()

        trx_usd = float(coingecko_api["tron"]["usd"])
        print(coingecko_api)
        print(trx_usd)
        array_splitted = value.split(",")
        print(array_splitted)
        Username = array_splitted[0]
        Hashrate = array_splitted[1]
        Price_per_day = array_splitted[2]
        Trx_Address = array_splitted[3]
        Hash_of_the_offer = array_splitted[4]
        real_duco_username = array_splitted[5]
        price_per_day_usd_trx_var = ((float(Price_per_day)) * (float(trx_usd)))
        price_per_day_usd_trx_var_rounded = str(round(price_per_day_usd_trx_var, 2))
        print("Username: ", Username)
        print("Hashrate:", Hashrate)
        print("Price per day: ", Price_per_day)
        print("Price per day in USD: ", price_per_day_usd_trx_var)
        print("Trx address of miner", Trx_Address)
        print("Hash of the offer", Hash_of_the_offer)
        print("Real duco username", real_duco_username)
        f = open("offers-frontend.txt", "a")
        json_check_account = requests.get("https://server.duinocoin.com/balances/{}".format(Username)).json()

        check_if_account_exists = json_check_account["success"]
        print(check_if_account_exists)

        str_check_if_account_exists = (str(check_if_account_exists))
        if str_check_if_account_exists == "False":
            
                    with open("offers-backend.txt","r+") as f:
                        new_f = f.readlines()
                        f.seek(0)
                        for line in new_f:
                            if "{}".format(Username) not in line:
                                f.write(line)
                        f.truncate()
                        time.sleep(1)
        time.sleep(3)
        if str_check_if_account_exists == "True":
            sum_miner_hashrate_var = 0
            json_ze_strony = requests.get("https://server.duinocoin.com/users/{}".format(Username)).json()
            for miner in json_ze_strony["result"]["miners"]:
                miner_hashrate_var = (miner["hashrate"])
                sum_miner_hashrate_var += miner_hashrate_var
            json_api_username_var = (json_ze_strony["result"]["balance"]["username"])
            print(json_api_username_var, "Final hashrate", sum_miner_hashrate_var)
            real_sum_miner_hashrate_var = (sum_miner_hashrate_var / 1000)
            f.write("{},{}kH/s,{}TRX     {}$,{},{}\n".format(Username, real_sum_miner_hashrate_var, Price_per_day, price_per_day_usd_trx_var_rounded, Trx_Address, Hash_of_the_offer))
            f.close()
    filename = "offers-frontend.txt"

    with open(filename) as f_input:
        data = f_input.read().rstrip('\n')

    with open(filename, 'w') as f_output:    
        f_output.write(data)


### dry run

def backend_website():
    f = open("/home/ubuntu/Faucet_Furimo/connect.txt", "r")

    check_if_json = f.read()

    if check_if_json != "json":
        print("i will do nothing because json does not work")
    if check_if_json == "json":
        filename = "offers-backend.txt"
        with open(filename) as f_input:
            data = f_input.read().rstrip('\n')
        with open(filename, 'w') as f_output:    
            f_output.write(data)
        f = open("offers-backend.txt", "r")
        yes0 = f.read()
        yes1 = yes0.splitlines()
        open('offers-frontend.txt', 'w').close()
        for value in yes1:
            coingecko_api = requests.get(
            "https://api.coingecko.com/"
            + "api/v3/simple/price?ids=tron&vs_currencies=usd",
            data=None
            ).json()

            trx_usd = float(coingecko_api["tron"]["usd"])
            print(coingecko_api)
            print(trx_usd)
            array_splitted = value.split(",")
            print(array_splitted)
            Username = array_splitted[0]
            Hashrate = array_splitted[1]
            Price_per_day = array_splitted[2]
            Trx_Address = array_splitted[3]
            Hash_of_the_offer = array_splitted[4]
            real_duco_username = array_splitted[5]
            price_per_day_usd_trx_var = ((float(Price_per_day)) * (float(trx_usd)))
            price_per_day_usd_trx_var_rounded = str(round(price_per_day_usd_trx_var, 2))
            print("Username: ", Username)
            print("Hashrate:", Hashrate)
            print("Price per day: ", Price_per_day)
            print("Price per day in USD: ", price_per_day_usd_trx_var)
            print("Trx address of miner", Trx_Address)
            print("Hash of the offer", Hash_of_the_offer)
            print("Real duco username", real_duco_username)
            f = open("offers-frontend.txt", "a")
            json_check_account = requests.get("https://server.duinocoin.com/balances/{}".format(Username)).json()

            check_if_account_exists = json_check_account["success"]
            print(check_if_account_exists)

            str_check_if_account_exists = (str(check_if_account_exists))
            if str_check_if_account_exists == "False":
                
                        with open("offers-backend.txt","r+") as f:
                            new_f = f.readlines()
                            f.seek(0)
                            for line in new_f:
                                if "{}".format(Username) not in line:
                                    f.write(line)
                            f.truncate()
                            time.sleep(1)
            time.sleep(3)
            if str_check_if_account_exists == "True":
                sum_miner_hashrate_var = 0
                json_ze_strony = requests.get("https://server.duinocoin.com/users/{}".format(Username)).json()
                for miner in json_ze_strony["result"]["miners"]:
                    miner_hashrate_var = (miner["hashrate"])
                    sum_miner_hashrate_var += miner_hashrate_var
                json_api_username_var = (json_ze_strony["result"]["balance"]["username"])
                print(json_api_username_var, "Final hashrate", sum_miner_hashrate_var)
                real_sum_miner_hashrate_var = (sum_miner_hashrate_var / 1000)
                f.write("{},{}kH/s,{}TRX     {}$,{},{}\n".format(Username, real_sum_miner_hashrate_var, Price_per_day, price_per_day_usd_trx_var_rounded, Trx_Address, Hash_of_the_offer))
                f.close()
        filename = "offers-frontend.txt"

        with open(filename) as f_input:
            data = f_input.read().rstrip('\n')

        with open(filename, 'w') as f_output:    
            f_output.write(data)



                # with open("offers-frontend.txt","r+") as f:
                #     new_f = f.readlines()
                #     f.seek(0)
                #     for line in new_f:
                #         if "{}".format(offer_hash_var) not in line:
                #             f.write(line)
                #     f.truncate()

                # with open("offers-backend.txt","r+") as f:
                #     new_f = f.readlines()
                #     f.seek(0)
                #     for line in new_f:
                #         if "{}".format(offer_hash_var) not in line:
                #             f.write(line)
                #     f.truncate()



schedule.every(6).hours.do(backend_website)

while True:
    schedule.run_pending()
    time.sleep(1)
 
