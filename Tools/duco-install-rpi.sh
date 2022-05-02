#!/bin/sh
# Made by Grantrocks
u="$USER"
echo "Installing Duino Coin On Your Raspberry Pi"
sleep 1
sudo apt update
sudo apt install python3 python3-pip git python3-pil python3-pil.imagetk -y # Install dependencies
cd

# Update if duino con exists
if [ -d ~/duino-coin/ ];then
  cd ~/duino-coin
  git pull
fi

if [ ! -d ~/duino-coin/ ];then
    echo "Duino Coin not yet downloaded. Downloading...."
    git clone https://github.com/revoxhere/duino-coin # Clone Duino-Coin repository
fi

cd ~/duino-coin
echo "Installing python packages"
python3 -m pip install -r requirements.txt # Install pip dependencies

#Check if the app exists
if [ ! -f ~/.local/share/applications/duino-coin-pc-miner.desktop ];then
    echo "Creating PC Miner button..."
fi

# Shortcut For PC Miner

mkdir -p ~/.local/share/applications
echo "[Desktop Entry]
Name=Duino Coin PC Miner
Comment=Duino Coin miner for the raspberry pi
Exec=python3 /home/$u/duino-coin/PC_Miner.py
Icon=/home/$u/duino-coin/Resources/PCMiner.png
Terminal=true
Type=Application
Categories=Utility;
StartupNotify=true" > ~/.local/share/applications/duino-coin-pc-miner.desktop

# Check if the app exists
if [ ! -f ~/.local/share/applications/duino-coin-avr.desktop ];then
    echo "Creating AVR Miner menu button..."
fi

#Create The Shortcut For Avr Miner
echo "[Desktop Entry]
Name=Duino Coin AVR Miner
Comment=AVR miner for duino coin.
Exec=python3 /home/$u/duino-coin/AVR_Miner.py
Icon=/home/$u/duino-coin/Resources/AVRMiner.png
Terminal=true
Type=Application
Categories=Utility;
StartupNotify=true" > ~/.local/share/applications/duino-coin-avr.desktop
cd ~/
if [ -f ~/duco-install-rpi.sh]; then
    rm duco-install-rpi.sh
fi
echo "Installed"