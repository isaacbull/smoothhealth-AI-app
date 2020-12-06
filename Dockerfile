FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn3 -y

COPY requirements.txt requirements.txt
COPY app /opt/

RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install tensorflow==2.2.0
RUN pip3 install -r requirements.txt

WORKDIR /opt/

EXPOSE 8000

ENTRYPOINT ["python3"]

CMD ["app.py"]