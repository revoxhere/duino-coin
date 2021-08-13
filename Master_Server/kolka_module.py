# Duino-Coin Kolka algorithms and formulas
# 2019-2021 Duino-Coin community
from fastrand import pcg32bounded as fastrandint
from math import floor, log
MULTIPLIER = 1
DECIMALS = 20


def kolka_v1(hashrate, difficulty, workers):
    """ Kolka V1 reward system - to be extended in the future
        Authors: revox """
    pc_mining_perc = 0.80
    avr_mining_perc = 0.96

    highest_avr_diff = 1500
    highest_pc_diff = 150000

    MAX_AVR_HASHRATE = 210
    MAX_MEGAAVR_HASHRATE = 700
    MAX_ESP_HASHRATE = 11000

    try:
        if hashrate <= MAX_AVR_HASHRATE:
            output = log(hashrate) / 6006
        elif hashrate <= MAX_MEGAAVR_HASHRATE:
            output = log(hashrate) / 6226
        elif hashrate <= MAX_ESP_HASHRATE:
            output = log(hashrate) / 8558
        else:
            output = log(hashrate) / 20002
    except:
        output = 0

    if difficulty > highest_pc_diff:
        output = 2*(output * \
            (pc_mining_perc ** (workers-1)) / (28110 ** workers))
    elif difficulty > highest_avr_diff:
        output = 2*(output * (pc_mining_perc ** (workers-1)))
    else:
        output = 2*(output * (avr_mining_perc ** (workers-1)))

    return round(output, DECIMALS)


def kolka_v2(current_difficulty, difficulty_list):
    """ Part of Kolka V2 system - move miner to the next diff tier
        Authors: revox """

    if current_difficulty == "AVR":
        return "MEGA"
    if current_difficulty == "MEGA":
        return "ARM"
    if current_difficulty == "ARM":
        return "DUE"
    if current_difficulty == "DUE":
        return "ESP8266"
    if current_difficulty == "ESP8266":
        return "ESP32"
    if current_difficulty == "ESP32":
        return "LOW"
    if current_difficulty == "LOW":
        return "MEDIUM"
    if current_difficulty == "MEDIUM":
        return "NET"
    else:
        return "EXTREME"


def kolka_v3(sharetime, expected_sharetime, difficulty):
    """ Kolka V3 system - variable difficulty
        Takes: sharetime, exp. sharetime and current diff 
        Authors: EinWildesPanda, revox """

    """ Calculate the difficulty multiplier """
    p = 2 - sharetime / expected_sharetime
    new_difficulty = difficulty

    """ Checks whether sharetime was higher than expected
        or has exceeded the buffer of 10%
        (p = 1 equals to sharetime = expected_sharetime) """
    if p < 1 or p > 1.1:
        new_difficulty = int(difficulty * p)

        """ Checks whether the diff is lower than 0
        (sharetime was way higher than expected) """
        if new_difficulty < 0:
            """ Divided by abs(p) + 2 to drastically lower the diff
                +2 is added to avoid dividing by +-0.x
                *0.9 is used to decrease it when the sharetime is
                3x higher than expected; everything rounded down
                to not make the 0.9 useless; +1 is added to avoid
                getting diffs equal to 0 """
            new_difficulty = floor(int(difficulty / (abs(p) + 2)) * 0.9) + 1

        # Check if sharetime was exactly double than expected
        elif new_difficulty == 0:
            # Thus roughly halve the difficulty
            new_difficulty = int(difficulty * 0.5)
    if new_difficulty < 5000:
        new_difficulty = 5000
    return int(new_difficulty)


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
