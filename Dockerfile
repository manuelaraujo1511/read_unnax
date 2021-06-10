FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt

WORKDIR /local
RUN rabbitmqctl add_user admin 19200130
RUN rabbitmqctl add_vhost /my_vhost
RUN rabbitmqctl set_user_tags admin mytag
RUN rabbitmqctl set_permissions -p /my_vhost admin ".*" ".*" ".*"