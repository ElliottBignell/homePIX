FROM python:3

# install nginx
# COPY nginx.default /etc/nginx/sites-available/default

# copy source and install dependencies
# RUN mkdir -p /opt/app
# RUN mkdir -p /opt/app/pip_cache
# RUN mkdir -p /opt/app/martor_demo
# COPY requirements.txt start-server.sh /opt/app/
# WORKDIR /opt/app
# RUN pip3 install -r requirements.txt --cache-dir /opt/app/pip_cache
# RUN chown -R www-data:www-data /opt/app

# COPY . /code/
# COPY ./server.crt /etc/ssl/certs/
# COPY ./server.key /etc/ssl/private/

# ENV PYTHONUNBUFFERED=1
# WORKDIR /code
# CMD ["/opt/app/start-server.sh"]


ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/
COPY ./server.crt /etc/ssl/certs/
COPY ./server.key /etc/ssl/private/

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM

# RUN python manage.py runsslserver --certificate /code/server.crt --key /code/server.key
