build:
	python3 -m compileall PC_Miner.py AVR_Miner.py
	mkdir bin
	cp __pycache__/PC_Miner.cpython-38.pyc bin/PC_Miner
	cp __pycache__/AVR_Miner.cpython-38.pyc bin/AVR_Miner
	rm -rf __pycache__/
	cd bin
	chmod +x PC_Miner AVR_Miner

