#file: utilities.py
#auth: rafer cooley
#desc: helper functions for the datamanager
import os
import glob
import json
from elasticsearch import Elasticsearch
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
# from tqdm import tqdm
from tqdm.auto import tqdm, trange
from multiprocessing import Pool, RLock
from functools import partial
import random

from index_templates import *
from variables import *

def get_data_filepaths(docker_uploaded_path:str,wind_data_folder_name:str,simulations:list[str]=None) -> list[str]:
    """Internal helper function to search for json files, either for a particular simulation or all files

    Args:
        docker_uploaded_path (str): path to base shared volume folder in docker container
        wind_data_folder_name (str): name of data folder contained in the shared volume folder
        simulations (list[str], optional): name of simulations to get data from. Defaults to None meaning return data for all simulations.

    Raises:
        Exception: SIM_NOT_FOUND if provided simulation name does not exist in collection of simulation data.

    Returns:
        list[str]: list of absolute filepaths
    """
    if simulations==None or len(simulations)==0:
        return glob.glob(os.path.join(docker_uploaded_path,wind_data_folder_name,'**/*.json'),recursive=True)
    elif "all" in simulations:
        return glob.glob(os.path.join(docker_uploaded_path,wind_data_folder_name,'**/*.json'),recursive=True)
    else:
        available_simulations = get_simulations(docker_uploaded_path,wind_data_folder_name)
        combined_simulations_datafiles = []
        for simulation in simulations:
            if not simulation in available_simulations:
                raise Exception(f"Provided simulation name not found:\nGiven: {simulation}\nExpected: {available_simulations}")
            combined_simulations_datafiles = combined_simulations_datafiles + glob.glob(os.path.join(docker_uploaded_path,wind_data_folder_name,simulation,'**/*.json'),recursive=True)
        return combined_simulations_datafiles

def get_simulations(docker_uploaded_path:str,wind_data_folder_name:str) -> list[str]:
    """Get list of all simulation folder names

    Args:
        docker_uploaded_path (str): path to base shared volume folder in docker container
        wind_data_folder_name (str): name of data folder contained in the shared volume folder

    Returns:
        list[str]: list of folder names that contain the data exported from different simulations. These folder names will be used as the names of the simulations throughout the rest of this program.
    """
    available_simulations = []
    for sim in os.listdir(os.path.join(docker_uploaded_path,wind_data_folder_name)):
        if os.path.isdir(os.path.join(docker_uploaded_path,wind_data_folder_name,sim)):
            available_simulations.append(sim)
    print('>> data_manager.utilities.get_simulations complete')
    print('-'*50)
    return available_simulations

def upload_index_templates(es:Elasticsearch) -> None:
    """Create index template patterns in elasticsearch to properly format indices as we upload the data

    Args:
        es (Elasticsearch): elasticsearch client instance
    """
    all_templates = [
        ("bennu-template",BENNU_INDEX_TEMPLATE),
        ("detections-template",DETECTIONS_INDEX_TEMPLATE),
        ("tests-template",TESTS_INDEX_TEMPLATE),
        ("logstash-template",LOGSTASH_INDEX_TEMPLATE),
        ("wazuh-alerts-template",WAZUH_ALERTS_INDEX_TEMPLATE),
        ("wazuh-monitoring-template",WAZUH_MONITORING_INDEX_TEMPLATE),
        ("xsoar-template",XSOAR_ENVS_INDEX_TEMPLATE)#TODO: currently missing datasource definition in grafana
    ]
    for template_name, template_dict in all_templates:
        print('-'*50)
        print(f"uploading template: {template_name}\n{template_dict}")
        #special exclusion for detections template b/c the index name is similar to what the alias would be, so we skip the alias parameter for it
        if template_name == "detections-template":
            es.indices.put_template(
                name=template_name,
                index_patterns=template_dict['index_patterns'],
                mappings=template_dict['template']['mappings'],
                version=template_dict['version']
            )
        else:
            es.indices.put_template(
                name=template_name,
                aliases=template_dict['template']['aliases'],
                index_patterns=template_dict['index_patterns'],
                mappings=template_dict['template']['mappings'],
                version=template_dict['version']
            )

    print('>> data_manager.utilities.upload_index_templates complete')
    print('-'*50)
    return

def get_file_date_range(filepath:str) -> tuple[datetime,datetime]:
    """Get the minimum and maximum timestamps for a single data file

    Args:
        filepath (str): path to datafile, sent directly to file.open

    Returns:
        tuple[datetime,datetime]: two datetime objects representing the min and max times from the data file
    """
    min_time = datetime.now().timestamp()
    max_time = datetime(1990,1,1).timestamp()
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            #sanity check to ensure datafile has data records in 'hits' key
            try:
                data['hits']['hits']
            except KeyError as error:
                print('>>> ERROR: utilities.get_file_date_range:datafile does not contain usable data')
                print(f'>>> current simulation: {filepath}')
                return min_time,max_time #wont hurt returning these values since the comparisons in calling function use these default values as well

            #loop each found data point in the datafile
            for datapoint in data['hits']['hits']:
                datapoint_timestamp = dateutil_parse(datapoint['_source']['@timestamp']).timestamp()
                if datapoint_timestamp>max_time: max_time = datapoint_timestamp
                elif datapoint_timestamp<min_time: min_time = datapoint_timestamp
    except Exception as e:
        print(f'>>> ERROR:\nfile: {filepath}\ncurrent_min_time: {min_time}\ncurrent_max_time: {max_time}\nerror_msg: {str(e)}')
    return min_time, max_time

def determine_date_range(datafiles:list[str]) -> tuple[datetime,datetime]:
    """Analyzes all provided data files and determines the minimum and maximum timestamps, will use multiprocessing if enabled globally

    Args:
        datafiles (list[str]): list of filepaths to all the simulation data files to examine

    Returns:
        min_time, max_time (tuple(datetime,datetime)): two datetime objects representing the min and max timestamps found in the provided datafiles
    """
    print('-'*50)
    print('>> running data_manager.utilities.determine_date_range')
    min_time = datetime.now().timestamp()
    max_time = datetime(1990,1,1).timestamp()

    #loop through all files, look at the timestamp of each record in each file
    #if timestamp>max_time, then thats our new max timestamp
    #if timestamp<min_tim, then thats our new min timestamp
    if USE_MULTIPROCESSING:
        with Pool(processes=MAX_MULTIPROCESSING_WORKERS) as pool:
            for file_min, file_max in pool.imap(get_file_date_range, datafiles):
                print(f'Got result: {file_min},{file_max}', flush=True)
                if file_min<min_time: min_time = file_min
                if file_max>max_time: max_time = file_max
    else:
        for file in tqdm(datafiles,desc="date range from data files"):
            try:
                file_min, file_max = get_file_date_range(file)
                if file_min<min_time: min_time = file_min
                if file_max>max_time: max_time = file_max
            except Exception as e:
                print(f'>>> ERROR:\nfile: {file}\ncurrent_min_time: {min_time}\ncurrent_max_time: {max_time}\nerror_msg: {str(e)}')

    print('> calculated daterange from given datasets')
    min_time = datetime.fromtimestamp(min_time)
    max_time = datetime.fromtimestamp(max_time)
    print(f'> min timestamp: {datetime.strftime(min_time, MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING)}')
    print(f'> max timestamp: {datetime.strftime(max_time, MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING)}')
    print('-'*50)
    return min_time, max_time
