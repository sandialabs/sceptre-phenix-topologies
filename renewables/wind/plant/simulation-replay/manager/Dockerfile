#Dockerfile for data manager container
FROM python:3.10-slim-buster

# ARG DATA_MANAGER_VERSION
# ENV DATA_MANAGER_VERSION $DATA_MANAGER_VERSION

RUN apt update && apt install -y curl

COPY ./requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

COPY ./ /opt/app/
# COPY requirements.txt /tmp/

RUN chmod ugo+x /opt/app/wait*
# COPY wind_data_final /opt/app/
# COPY data_manager.py /opt/app/

# NOTE: trying to setup running this as non-priviledged user but can't figure it out, putting on backburner
# RUN addgroup -S dashmanagergroup && adduser -S dashmanager -G dashmanagergroup
# RUN groupadd -r dashmanager -g 901 && useradd -u 901 -r -g dashmanager
# RUN useradd -u 901 --system --user-group dashmanager
# USER dashmanager

WORKDIR /opt/app
# ENTRYPOINT [ "python", "data_manager.py" ]
