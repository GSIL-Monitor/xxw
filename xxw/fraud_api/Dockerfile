FROM ccr.ccs.tencentyun.com/ops-public/python:3.6.5
WORKDIR /srv
ADD . /srv
RUN export http_proxy=http://http-proxy.xwfintech.com:8118 && export https_proxy=http://http-proxy.xwfintech.com:8118 && wget https://pypi.tuna.tsinghua.edu.cn/packages/20/53/1bb8ad34ad5c2047a11651290325e55086bc18fce7cfdbbe6f5522bd0ae5/flask-mongoengine-0.9.5.tar.gz && tar zxf flask-mongoengine-0.9.5.tar.gz && cd flask-mongoengine-0.9.5 && python setup.py install
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN cd /srv && chmod +x entrypoint.sh
ENTRYPOINT ["/srv/entrypoint.sh"]
