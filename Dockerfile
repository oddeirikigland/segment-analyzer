FROM python:3.7

ADD ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt

ADD ./ /app
WORKDIR /app

CMD ["python", "run.py"]