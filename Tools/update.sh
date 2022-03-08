#!/bin/sh
sudo apt update && sudo apt upgrade -y
sudo apt install git
cd 
rm -rf duino-coin
git clone https://github.com/revoxhere/duino-coin.git
cd duino-coin
python3 -m pip install -r requirements.txt
chmod +x Tools/update.sh
clear
