#!/usr/bin/env python3
"""
Duino-Coin Kolka module © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin-rest-api
Duino-Coin Team & Community 2019-2021
"""

from fastrand import pcg32bounded as fastrandint
from math import floor, log
import json

with open('/home/debian/websites/PoolRewards.json', 'r') as f:
    pool_rewards = json.load(f)

MULTIPLIER = 1
DECIMALS = 20
MAX_PC_DIFF = 150000
MAX_AVR_DIFF = 1500
PC_KOLKA_DROP = pool_rewards["NET"]["kolka_decrease_perc"] * 0.01
ESP_KOLKA_DROP = pool_rewards["ESP32"]["kolka_decrease_perc"] * 0.01
AVR_KOLKA_DROP = pool_rewards["AVR"]["kolka_decrease_perc"] * 0.01


def kolka_v1(hashrate, difficulty, workers, reward_div):
    """
    Kolka V1 reward system - to be extended in the future
    Authors: revox
    """

    try:
        output = log(hashrate) / reward_div
    except:
        output = 0

    if (difficulty > MAX_PC_DIFF):
        output = 2 * (output * (PC_KOLKA_DROP ** (workers - 1))) / (pool_rewards["EXTREME"]["reward"] * workers)
    elif (difficulty > pool_rewards["ESP32"]["difficulty"]):
        output = 2 * (output * (ESP_KOLKA_DROP ** (workers - 1)))
    else:
        output = 2 * (output * (AVR_KOLKA_DROP ** (workers - 1)))

    return round(output, DECIMALS)



def kolka_v2(current_difficulty, difficulty_list):
    """
    Part of Kolka V2 system - move miner to the next diff tier
    Authors: revox
    """
    if current_difficulty == "XXHASH":
        return "XXHASH"
    if current_difficulty == "AVR":
        return "MEGA"
    if current_difficulty == "MEGA":
        return "ARM"
    if current_difficulty == "ARM":
        return "DUE"
    if current_difficulty == "DUE":
        return "ESP8266"
    if current_difficulty == "ESP8266":
        return "ESP8266H"
    if current_difficulty == "ESP8266H":
        return "ESP32"
    if current_difficulty == "ESP32":
        return "LOW"
    if current_difficulty == "LOW":
        return "MEDIUM"
    if current_difficulty == "MEDIUM":
        return "NET"
    if current_difficulty == "NET":
        return "EXTREME"
    if current_difficulty == "EXTREME":
        return "EXTREME"


def kolka_v3(sharetime, expected_sharetime, difficulty):
    """
    Kolka V3 system - variable difficulty
    Takes: sharetime, exp. sharetime and current diff
    Authors: EinWildesPanda, revox
    """

    """ Calculate the difficulty multiplier """
    p = 2 - sharetime / expected_sharetime
    new_difficulty = difficulty

    """
    Checks whether sharetime was higher than expected
    or has exceeded the buffer of 10%
    (p = 1 equals to sharetime = expected_sharetime)
    """
    if p < 1 or p > 1.1:
        new_difficulty = int(difficulty * p)

        """
        Checks whether the diff is lower than 0
        (sharetime was way higher than expected)
        """
        if new_difficulty < 0:
            """
            Divided by abs(p) + 2 to drastically lower the diff
            +2 is added to avoid dividing by +-0.x
            *0.9 is used to decrease it when the sharetime is
            3x higher than expected; everything rounded down
            to not make the 0.9 useless; +1 is added to avoid
            getting diffs equal to 0
            """
            new_difficulty = floor(int(difficulty / (abs(p) + 2)) * 0.9) + 1

        """ Check if sharetime was exactly double than expected """
        if new_difficulty == 0:
            """ Thus roughly halve the difficulty """
            new_difficulty = int(difficulty * 0.5)

    if new_difficulty < 5000:
        new_difficulty = 5000

    return int(new_difficulty)


def floatmap(x, in_min, in_max, out_min, out_max):
    """ Arduino's built in map function remade in python """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
