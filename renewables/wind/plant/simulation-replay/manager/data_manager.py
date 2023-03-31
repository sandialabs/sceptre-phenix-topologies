"""Dashboard Data Manager.

Usage:
    data_manager.py [options] replay <simulation_name>...
    data_manager.py [options] init
    data_manager.py [options] list
    data_manager.py [options] refresh
    data_manager.py [options] (-h | --help)
    data_manager.py [options] --version

Options:             
    -v, --verbose   Show more information like env vars and parsed arguments

Details:
    -h --help       Show this screen.
    --version       Show version.
"""
#file: data_manager.py
#auth: rafer cooley
#desc: manage data for weto-sceptre simulation environment
from time import sleep
from docopt import docopt
import json, re
import utilities
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
from tqdm import tqdm
from copy import deepcopy
from multiprocessing import Pool
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk as esbulk
from variables import *

def list_available_simulations() -> None:
    """Print the available simulations to run. Determined by the folder names containing elasticsearch data in wind_data_final/
    """
    list_simulations = utilities.get_simulations(DOCKER_UPLOADED_PATH,WIND_DATA_FOLDER_NAME)
    print('---Available simulations---')
    for sim in list_simulations:
        print(f'> {sim}')
    print('---------------------------')

def datafile_replay(input_data:tuple[str,datetime], es:Elasticsearch=None) -> tuple[str,int]:
    """Open file and insert data into Elasticsearch. Map this function to the list of filepaths for a requested simulation replay if multiprocessing speeds are desired.

    Args:
        input_data (tuple[str,datetime]): input data that has been zipped to simplify multiprocessing. Tuple contains the datafile filepath(str) and the time difference object(datetime)
        es (Elasticsearch): Elasticsearch client to be used, when using multiproc this should not be passed in and will be created in each process
    Returns:
        tuple[str,int]: tuple of values containing the current filepath(str) and a status value to indicate whether the data insertion was successful (1) or not (-1)
    """
    #unpack tuple into easier values
    filepath=input_data[0]
    time_diff=input_data[1]

    #NOTE: MUST create new client within each multiproc worker
    #src: https://elasticsearch-py.readthedocs.io/en/master/index.html#thread-safety
    if es==None and USE_MULTIPROCESSING: es=Elasticsearch(BASE_ES_URL)

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            #sanity check to ensure datafile has data records in 'hits' key
            try:
                data['hits']['hits']
            except KeyError as error:
                print('>>> ERROR: data_manager.data_replay:datafile does not contain usable data')
                print(f'>>> current simulation: {filepath}')
                return filepath,-1

            #loop each found data point in the datafile
            for datapoint in data['hits']['hits']:
                #build & modify the meta/changeable fields of the datapoint
                datapoint_index = datapoint['_index']
                datapoint_timestamp = dateutil_parse(datapoint['_source']['@timestamp'])
                datapoint_timestamp = datapoint_timestamp + time_diff #offset timestamp to simulate 'recent' experiment results

                #convert to timestamp b/c all other formats cause too many problems
                datapoint['_source']['@timestamp'] = datapoint_timestamp.timestamp()

                #modify index name to be the appropriate YYYY-MM-DD if necessary
                regstring = ".*-[0-9]{4}.[0-9]{2}.[0-9]{2}$" #match a YYYY-MM-DD at end of index name
                if re.match(regstring, datapoint_index):
                    index_name = datapoint_index.split('-')[0]
                    dpt_year = datapoint_timestamp.strftime("%Y")
                    dpt_month = datapoint_timestamp.strftime("%m")
                    dpt_day = datapoint_timestamp.strftime("%d")
                    datapoint_index = f"{index_name}-{dpt_year}.{dpt_month}.{dpt_day}"
                #save modified datapoint to elasticsearch
                try:
                    es.index(index=datapoint_index, document=datapoint['_source'])
                except Exception as e:
                    print('>>> ERROR: data_manager.data_replay:es.index problems indexing data')
                    print(f'>>> current simulation: {filepath}')
                    print(f'>>> datapoint: {datapoint}')
                    print(f'>>> error type: {type(e)}')
                    print(f'>>> error msg: {str(e)}')
                    return filepath,-1
    except Exception as e:
        print(f'>>> ERROR:\nfile: {filepath}\nerror_msg: {str(e)}')
        print(f'>>> current simulation: {filepath}')
        print(f'>>> error type: {type(e)}')
        print(f'>>> error msg: {str(e)}')
        return filepath, -1
    return filepath,0

def data_replay(simulations:list[str]) -> None:
    """Get data files for provided simulations and, depending on env variables, read data from file to elasticsearch either sequentially or using multiproc 

    Args:
        simulations (list[str]): names of simulations, corresponding to the folder name containing the simulation data. passed from docopt args
    """
    print('-'*50)
    print(f'>> begin data replay, using multiprocessing?[{USE_MULTIPROCESSING}]')
    #get data files
    simulation_datafiles = utilities.get_data_filepaths(DOCKER_UPLOADED_PATH,WIND_DATA_FOLDER_NAME,simulations)
    print(f'all sim files: {simulation_datafiles}')
    #get date ranges
    min_time, max_time = utilities.determine_date_range(simulation_datafiles)
    current_timestamp = datetime.now()
    time_diff = current_timestamp - max_time #replays data with last datapoint occuring at now
    print(f">> calculated time difference: {time_diff}")

    #build zipped list of tuples for sending to worker function
    time_diff_list = [time_diff]*len(simulation_datafiles)
    zipped_datafile_info = list(zip(simulation_datafiles,time_diff_list))

    if USE_MULTIPROCESSING:
        #create pool for worker management
        print('>> creating worker pool for inserting datafiles')
        with Pool(processes=MAX_MULTIPROCESSING_WORKERS) as pool:
            for datafile, runcode in pool.imap(datafile_replay, zipped_datafile_info):
                print(f'> datafile[{datafile}] returned code[{runcode}]', flush=True)
    else: #not using multiprocessing
        #loop through all files, look at the timestamp of each record in each file
        #modify the timestamp according to some rules, then load into elasticsearch
        print('>> looping simulation datafiles')
        es=Elasticsearch(BASE_ES_URL)
        for data_tuple in tqdm(zipped_datafile_info,desc="replay sim datafiles: linear non-multiproc"):
            datafile, runcode = datafile_replay(data_tuple,es)
            print(f'> datafile[{datafile}] returned code[{runcode}]')
    print('>> data replay done')
    print('-'*50)
    return

if __name__ == '__main__':
    args = docopt(__doc__, version=f'Dashboard Data Manager v{DATA_MANAGER_VERSION}')
    print(args)
    if args['--verbose']:
        print('-'*50)
        print('VERBOSE!')
        print('parsed arguments: ',args)
        #just copied these here b/c i didn't know how to dynamically get the variables in variables.py
        print('MASTER_OUTPUT_DATETIME_FORMAT_STRING:',MASTER_OUTPUT_DATETIME_FORMAT_STRING)
        print('MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING:',MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING)
        print('DATA_MANAGER_VERSION:',DATA_MANAGER_VERSION)
        print('BASE_ES_URL:',BASE_ES_URL)
        print('BASE_GRAFANA_URL:',BASE_GRAFANA_URL)
        print('BASE_HEADERS:',BASE_HEADERS)
        print('DOCKER_UPLOADED_PATH:',DOCKER_UPLOADED_PATH)
        print('WIND_DATA_FOLDER_NAME:',WIND_DATA_FOLDER_NAME)
        print('INDEX_DATASOURCE_CLEANING_CSV_PATH:',INDEX_DATASOURCE_CLEANING_CSV_PATH)
        print('MAX_MULTIPROCESSING_WORKERS:',MAX_MULTIPROCESSING_WORKERS)
        print('USE_MULTIPROCESSING:',USE_MULTIPROCESSING)
        print('-'*50)
    if args["init"]:
        es = Elasticsearch(BASE_ES_URL)
        utilities.upload_index_templates(es)
    elif args["list"]:
        list_available_simulations()
    elif args["replay"]:
        data_replay(args["<simulation_name>"])
    elif args["refresh"]:
        es = Elasticsearch(BASE_ES_URL)
        es.indices.delete(index="_all")
    elif args['clean_data']:
        utilities.prepare_dataset()
    else:
        print('no args parsed')
