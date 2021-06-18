install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
run:
	python3 bot.py

all: install run