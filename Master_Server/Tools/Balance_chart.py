# Create a chart of top balances
# 2020 revox from the Duino team

import matplotlib.pyplot as plt
import numpy as np
import requests
import json


def sortFunction(value):
    return data[value]


r = requests.get("https://server.duinocoin.com/balances").content.decode()
data = json.loads(r)["result"]


sorted_data = sorted(data, key=sortFunction, reverse=True)

ys = []
xs = []
i = 1
others = 0

for user in sorted_data:
    if i < 20:
        ys.append(float(data[user]))
        xs.append(str(i) + ". " + user +
                  " (" + str(round(float(data[user]))) + " DUCO)")

    if i >= 20:
        others += float(data[user])

    i += 1

ys.append(others)
xs.append("Other accounts" + " (" + str(int(others)) + " DUCO)")

plt.pie(ys,
        labels=xs,
        autopct='%1.1f%%',
        pctdistance=.925,
        labeldistance=1.05,
        radius=1.15,
        textprops=dict(color="#777777", fontsize=7),
        startangle=80,
        colors=[
            "#FFE17D",
            "#FAA878",
            "#F47A7A",
            "#615C8F",
            "#59ADBE",
            "#B1E3D4",
        ])

plt.title('Balance distribution', fontsize=16, color="#777777")
plt.savefig("/home/debian/websites/duino-coin-websocket-proxy/"
            + "balancechart.png",
            transparent=True, dpi=300, bbox_inches="tight")
