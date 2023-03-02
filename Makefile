
run:
	python3 main.py
test:
	python3 -m unittest discover -p "*.py"
freeze:
	pip3 freeze > requirements.txt
install:
	pip3 install -r requirements.txt
