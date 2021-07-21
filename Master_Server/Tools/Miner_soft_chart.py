# Create a chart of most used miner softwares
# 2020 revox from the Duino team

import json
import requests
import matplotlib.pyplot as plt2
url = 'https://server.duinocoin.com/miners'
data = {}
while len(data) < 1:
    resp = requests.get(url=url)
    data = resp.json()

softwares = {}
data = data["result"]
for user in data:
    minerName = data[user][0]["software"]
    if minerName:
        if "PC" in minerName:
            # Typical CPU uses four cores
            try:
                softwares[minerName] += 0.2
            except:
                softwares[minerName] = 0.2
        elif "ESP32" in minerName:
            # One esp uses two cores
            try:
                softwares[minerName] += 0.5
            except:
                softwares[minerName] = 0.5
        else:
            try:
                softwares[minerName] += 1
            except:
                softwares[minerName] = 1

names = []
count = []
for minerName in softwares:
    if softwares[minerName] > 16:
        names.append(minerName)
        count.append(softwares[minerName])

labels = names
sizes = count

plt2.pie(sizes,
         startangle=10,
         labels=labels,
         autopct='%1.0f%%',
         pctdistance=0.925,
         labeldistance=1.05,
         radius=0.8,
         textprops=dict(
             color="#777777", fontsize=7),
         colors=[
             "#FFE17D",
             "#FAA878",
             "#F47A7A",
             "#615C8F",
             "#59ADBE",
             "#B1E3D4",
         ])
plt2.title('Most popular mining softwares', fontsize=16, color="#777777")
plt2.savefig("/home/debian/websites/duino-coin-websocket-proxy/"
             + "minerchart.png",
             dpi=300, transparent=True, bbox_inches="tight")
