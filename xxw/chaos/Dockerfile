FROM ccr.ccs.tencentyun.com/ops-public/python:3.6.5
WORKDIR /srv
ADD . /srv
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN cd /srv && chmod +x entrypoint.sh
ENTRYPOINT ["/srv/entrypoint.sh"]
