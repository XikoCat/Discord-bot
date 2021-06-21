install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black -t py39 ./
	
run:
	python3 bot.py

all: install format run