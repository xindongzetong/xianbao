FROM python:3.9
ADD . /work
WORKDIR /work
VOLUME /work
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
CMD ["python","/work/main.py"]