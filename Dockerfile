FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN python3 -m ensurepip --upgrade
RUN pip3 install -r requirements.txt

COPY . /code/
RUN ls /code/

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM

RUN python3 manage.py runserver 0.0.0.0:8020
# RUN python3 manage.py runsslserver --certificate /code/server.crt --key /code/server.key
