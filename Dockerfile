FROM python:3.7
ADD . /usr/src/app
WORKDIR /usr/src/app
EXPOSE 4000
RUN python setup.py install --user
ENTRYPOINT ["python", "run.py"]