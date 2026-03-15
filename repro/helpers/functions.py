import pandas as pd
import logging
import json
import urllib.request
import os
import time
import math
# import shapefile
import sys

from constants.tags import car_tags, ROAD_TAGS, PATH_TAGS
MAXINT = sys.maxsize


def get_urls():
    """
    a function that reads in a list of URLs from a text file, and returns a Python list containing those URLs.
    """
    urls = list(pd.read_csv('urls.txt', header=None)[0])
    return urls


def get_logger():
    """
    sets up a logging instance, and creates a file handler that will write log messages to a file. The logger is then set to the logging level INFO and returned.
    """
    logger = logging.getLogger('logging')
    hdlr = logging.FileHandler(logger.name + '.log', mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger


# def get_shapefile(city_name):
#     """
#      reads in a shapefile using the pyshp library, given the name of the shapefile.
#     """
#     shape = shapefile.Reader(city_name+'/'+city_name+".shp")
#     return shape


def get_config():
    """
    reads in a JSON file called config.json and returns its contents as a Python dictionary.
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as config:
            info = json.loads(config.read())
        return info
    except:
        return {}


def download_or_find_pbf_file(osm_file_name, urls, bbox=False, bbox_data=None):
    """
    It checks if the file with the given name is already downloaded, and if not, attempts to download it from one of the URLs in the list.
    If the file is successfully downloaded, the function returns True, otherwise it returns False.
    :param osm_file_name: the osm file which needs to be checked for download
    :param urls: the list of urls from which the url for downloading the osm file should be taken
    """
    osm_data_directory = './osm_data/'
    if not os.path.exists(osm_data_directory):
        os.makedirs(osm_data_directory)
    dl = False
    if bbox:
        filename = osm_data_directory+osm_file_name+'.osm'
        if not os.path.isfile(filename):
            dl = True
            url = f'https://overpass-api.de/api/map?bbox={bbox_data}'
            urllib.request.urlretrieve(url, filename)
            return dl
    for file in urls:
        filename = osm_data_directory + file.split('/')[-1]
        v = 'latest.osm.pbf'
        val = file.split('/')[-1]
        val = val.split('-')
        val.remove(v)
        val = '-'.join(val)
        if val == osm_file_name:
            print('find url')
            if not os.path.isfile(filename):
                print('started to download')
                dl = True
                urllib.request.urlretrieve(file, filename)
                time.sleep(60)
            break
    return dl


def insert_into_map_vec(dictionary, key, value):
    """
    inserts a value into a dictionary for a given key to generate a dictionary with all matching values in a list
    to a key
    :param dictionary: dictionary with lists as values
    :param key: matching key to value
    :param value: value to insert
    """
    if not key in dictionary:
        dictionary[key] = [value]
    elif not (value in dictionary[key]):
        dictionary[key].append(value)


def sliding_window(input_list):
    """
    Sliding window over a list of size 2
    :param input_list: list
    :return: list with tuples of after sliding window over list
    """
    output_tuple_list = []
    for ij in range(len(input_list)-1):
        output_tuple_list.append(tuple([input_list[ij], input_list[ij+1]]))
    return output_tuple_list


def to_brng(v):
    """
    computes degrees from radians
    :param v: radians value
    :return: degree value
    """
    return (math.degrees(v) + 360) % 360


def haversine_degrees(center_node, node):
    """
    Computes the angle of an edge indicated by two nodes and the south-north meridian
    :param center_node: object of class NodeInfo
    :param node: object of class NodeInfo
    :return: value in degrees
    """
    # As we can't know which way should be considered as the "main way" (i.e., where we align the
    # first of the n outgoing edges), we simply iterate through all of them, and choose the
    # minimal delta overall.
    d_lon = math.radians(node.lon - center_node.lon)
    node_lat = math.radians(node.lat)
    center_node_lat = math.radians(center_node.lat)
    y = math.sin(d_lon) * math.cos(node_lat)
    x = math.cos(center_node_lat) * math.sin(node_lat) - math.sin(center_node_lat) * math.cos(node_lat) * math.cos(
        d_lon)
    return to_brng(math.atan2(y, x))


def compress_lis_ways(lis):
    """
    turn list to a list with unique list items
    :param lis: list
    :return: list with unique list items
    """
    return list(set(lis))


def are_same(set1, set2):
    """
    function to test if two lists contain same objects
    :param set1: list
    :param set2: list
    :return: boolean value implying if the to lists have same values
    """
    diff1 = set(set1) - set(set2)
    diff2 = set(set2) - set(set1)
    return len(diff1) == 0 and len(diff2) == 0


def junction_type(types):
    """
    takes a list of types and returns a string representing the junction type of the road.
    """
    types_str = ''.join(types)
    if len(types) == 0:
        return ""
    elif "Path" in types_str and ("Road" not in types_str and "Car" not in types_str):
        return "Path"
    elif "Path" not in types_str and ("Road" in types_str or "Car" in types_str):
        return "RoadCar"
    elif "Path" in types_str and ("Road" in types_str or "Car" in types_str):
        return "PathRoadCar"
    elif 'bus_stop' in types_str:
        return 'Bus'
    elif 'tram_stop' in types_str:
        return 'Tram'
    elif 'subway_entrance' in types_str:
        return 'Metro'
    elif 'bus' in types_str:
        return 'Bus'
    elif 'tram' in types_str:
        return 'Tram'
    elif 'subway' in types_str:
        return 'Metro'
    elif 'train' in types_str:  # TODO
        return 'Train'


def determine_split_by_type(way_type, junction_type):
    """
    takes in a way_type string and a junction_type string and returns a Boolean indicating whether the way should be split based on the type of junction.
    """
    if way_type in ROAD_TAGS and "PathRoadCar" == junction_type:
        return True
    elif way_type in car_tags and "RoadCar" == junction_type:
        return True
    elif way_type in PATH_TAGS+ROAD_TAGS and "Path" == junction_type:
        return True
    elif junction_type in ['Bus','Train','Metro','Tram']:
        return True
    else:
        return False
