# Duino-Coin Kolka algorithms and formulas
# 2019-2021 Duino-Coin community
from fastrand import pcg32bounded as fastrandint
from math import floor
MULTIPLIER = 1


def kolka_v1(basereward, sharetime, difficulty, workers, penalty=False):
    """ Kolka V1 reward system - to be extended in the future
        Authors: revox """
    pc_mining_perc = .80
    avr_mining_perc = .96
    if penalty:
        output = float(int(int(sharetime) ** 2) / 1000000) * -1
    else:
        output = (MULTIPLIER * basereward
                   + float(sharetime) / 10000
                   + float(difficulty) / 100000000)
    if difficulty > 600:
        output = output + (output * (pc_mining_perc ** (workers-1)))
    else:
        output = output + (output * (avr_mining_perc ** (workers-1)))

    return float(output)


def kolka_v2(current_difficulty, difficulty_list):
    """ Kolka V2 system - move miner to the next diff tier
        Authors: revox """
    if current_difficulty == "AVR":
        return "ESP8266"
    if current_difficulty == "ESP8266":
        return "ESP32"
    if current_difficulty == "ESP32":
        return "LOW"
    if current_difficulty == "LOW":
        return "MEDIUM"
    if current_difficulty == "MEDIUM":
        return "NET"
    if current_difficulty == "NET":
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

        # Checks if sharetime was exactly double than expected
        elif new_difficulty == 0:
            # Thus roughly half the difficulty
            new_difficulty = int(difficulty * 0.5)
    if new_difficulty <= 0:
        new_difficulty = 1
    return int(new_difficulty)


def kolka_v4(sharetime, expected_test_sharetime):
    """ Experimental Kolka V4 - sharetime exploit test
        Author: EinWildesPanda"""

    """ Calculates how far apart the shares are (in percent)"""
    p = sharetime / expected_test_sharetime
    """ Checks whether the sharetime took more 
        than 50% longer than it should've """
    if p > 1.5:
        rejectedShares += 1
        """ Calculate penalty dependent on share 
            submission time - Kolka V1 combined with V4 """
        penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
        try:
            """ Adds username to the dict so it will
                be penalized in the next DB update """
            balancesToUpdate[username] += penalty
        except Exception:
            balancesToUpdate[username] = penalty


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
