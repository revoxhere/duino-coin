echo "Installing Duino Coin On Your Raspberry Pi"
sleep 1
sudo apt update
sudo apt install python3 python3-pip git python3-pil python3-pil.imagetk -y # Install dependencies
cd
if [ ! -d ~/duino-coin/ ];then
  echo "Duino Coin not yet downloaded. Downloading...."
  git clone https://github.com/revoxhere/duino-coin # Clone Duino-Coin repository
fi
cd ~/duino-coin
python3 -m pip install -r requirements.txt # Install pip dependencies
#menu button
if [ ! -f ~/.local/share/applications/duino-coin-pc-miner.desktop ];then
  echo "Creating menu button..."
fi
mkdir -p ~/.local/share/applications
echo "[Desktop Entry]
Name=Duino Coin PC Miner
Comment=Duino Coin miner for the raspberry pi
Exec=python3 /home/pi/duino-coin/PC_Miner.py
Icon=cd/home/pi/resources/PCMiner.png
Terminal=true
Type=Application
Categories=Utility;
StartupNotify=true" > ~/.local/share/applications/duino-coin-pc-miner.desktop

if [ ! -f ~/.local/share/applications/duino-coin-avr.desktop ];then
  echo "Creating Settings menu button..."
fi
echo "[Desktop Entry]
Name=Duino Coin AVR Miner
Comment=AVR miner for duino coin.
Exec=python3 /home/pi/duino-coin/AVR_Miner.py
Icon=home/pi/duino-coin/resources/AVRMiner.png
Terminal=true
Type=Application
Categories=Utility;
StartupNotify=true" > ~/.local/share/applications/duino-coin-avr.desktop
echo "Installed"