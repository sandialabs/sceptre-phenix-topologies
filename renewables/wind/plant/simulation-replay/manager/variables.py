#file: variables.py
#auth: rafer cooley
#desc: provide default variables to the rest of the program

import os

#NOTE: this datetime format follows the `date_time_no_millis` format from elasticsearch defined as:
#   A formatter that combines a full date and time without millis, separated by a T: yyyy-MM-dd'T'HH:mm:ssZ. 
# pay attention to the single quotes around the T separator but not the Z terminator
MASTER_OUTPUT_DATETIME_FORMAT_STRING = "%Y-%m-%d'T'%H:%M:%SZ"
# MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING = "date_time_no_millis"
MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING = "epoch_second"

#NOTE: environment variables are passed from .env and .env_data_manager_version through docker-compose.yml to this program
DATA_MANAGER_VERSION = os.getenv("DATA_MANAGER_VERSION","0.1")
BASE_ES_URL = os.getenv("ELASTICSEARCH_CONTAINER_NAME","localhost")
# BASE_ES_URL = os.getenv("ELASTIC_IP","localhost")
BASE_ES_URL = f"http://{BASE_ES_URL}:9200"
BASE_GRAFANA_URL = f"http://{os.getenv('GRAFANA_CONTAINER_NAME','localhost')}:3000"
BASE_HEADERS = {'Content-type': 'application/json'}

#NOTE: remember all filepaths will need to correspond with the locations in the python docker container
# i.e. data folder and scripts uploaded to /opt/app/ (see manager/Dockerfile)

DOCKER_UPLOADED_PATH="/opt/app"
WIND_DATA_FOLDER_NAME="wind_data_final"
INDEX_DATASOURCE_CLEANING_CSV_PATH=os.path.join(DOCKER_UPLOADED_PATH,'index_datasource_cleaning.csv')

MAX_MULTIPROCESSING_WORKERS=int(os.getenv("DATA_MANAGER_MULTIPROCESSING_WORKER_COUNT",4))
USE_MULTIPROCESSING=bool(os.getenv("DATA_MANAGER_USE_MULTIPROCESSING",True))
