# pull official base image
FROM ubuntu

RUN apt update -y && apt upgrade -y && \
    apt install -y python3 python3-pip python3-venv && \
    pip3 install --upgrade pip && \
    apt install netcat curl -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUBUFFERED 1
ENV PYTHONENCODING UTF-8
ARG APP_FOLDER
ENV ENV_APP_FOLDER=$APP_FOLDER
ENV PYTHONPATH /$APP_FOLDER


# intentional separation, code in folder changes more often than requirements file so less unneccesary pip3 installs
COPY ./Deployment/entrypoint.sh /$APP_FOLDER/
COPY ./$APP_FOLDER/requirements.txt /$APP_FOLDER/
RUN pip3 install -r /$APP_FOLDER/requirements.txt
COPY ./Common_utilities /Common_utilities
COPY ./$APP_FOLDER /$APP_FOLDER
