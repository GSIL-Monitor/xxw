format:
	black . --py36 --fast -q
	isort . -rc -q
test:
	pytest  --cov=src --flake8

gen:
	pyinstaller src/main.py --onefile --name app --additional-hooks-dir . --clean

dev:
	export FLASK_APP=src/main.py && export FLASK_ENV=development && flask run -h 0.0.0.0 -p 10120