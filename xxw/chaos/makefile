.PHONY: all test clean

format:
	black . --py36 --fast -q
	isort . -rc -q

test:
	make format
	pytest  --cov=src --flake8

gen:
	make test
	pyinstaller src/app.py --onefile --name $(notdir $(CURDIR)) --additional-hooks-dir . --clean

local:
	export ZK_SERVERS=127.0.0.1:2181 && \
	export FLASK_APP=src/app.py && export CUR_ENV=local && flask run --port 20001 --host 0.0.0.0

dev:
	export ZK_SERVERS=111.230.231.89:2181,111.230.231.89:2182,111.230.231.89:2183 && \
	export REDIS_URL=redis://:xxw2018@111.230.231.89:6379 && \
	export CHAOS_DB=mysql+pymysql://xxw_local:xxwlocal2018@172.16.1.49/local_chaos && \
	export SERVICE_NAME=chaos && \
	export MONGO_URI=mongodb://localhost:27017/ip_address && \
	export FLASK_APP=src/main.py && export FLASK_ENV=development && flask run --port 20001 --host 0.0.0.0
