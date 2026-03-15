### REGION OF INTEREST
CITYNAME = "vienna"
bounding_box = "16.177959,48.113973,16.586436,48.328019"

### REFERENCE_SYSTEMS
osm_crs = 4326
projected_crs = 32633
dem_crs = 31256
gtfs_crs = 4326

### MODES
private_modes = ['walk', 'bike', 'car']
public_modes = ['bus', 'tram', 'subway', 'train']
modes = private_modes + public_modes

### GTFS TIMETABLES
time_window_start = '07:00:00'
time_window_end = '21:00:00'

# specify correct feed per mode (folder with .txt)
gtfs_path = 'GTFS'
gtfs_folder = {
    'bus': 'wiener_linien',
    'tram': 'wiener_linien',
    'subway': 'wiener_linien',
    'train': 'GTFS_OP_2023_obb'}


### DIGITAL ELEVATION MODEL
dem_path = 'DEM'
dem_folder = {'dem': 'tif_files'}


### TRANSITION COSTS
# Bischoff, J., & Nagel, K., 2017. Integrating explicit parking search into a transport simulation.
car_parking_time = 8  # 8 min

# Henrikki Tenkanen & Tuuli Toivonen ,2020. Longitudinal spatial dataset on travel times and distances by different travel modes in Helsinki Region.
car_reach_length = 180  # 180 m
bike_reach_length = 0  # 0 m, bike parking is usually close by
car_reach_time = 2.5  # 2.5 min
bike_reach_time = 1  # 1.0 min

# Ansari Esfeh, M., et al., 2021. Waiting time and headway modelling for urban transit systems–
# a critical review and proposed approach.
bus_waiting_time = 6.2  # 1/2 headway -> derived from GTFS - Wiener Linien
tram_waiting_time = 4.0  # 1/2 headway -> derived from GTFS - Wiener Linien
subway_waiting_time = 2.0  # 1/2 headway -> derived from GTFS - Wiener Linien
train_waiting_time = 5.9  # 1/2 headway -> derived from GTFS - OEBB


### HIGHWAY TAGS
PATH_TAGS = ["path",
             "steps",
             "bridleway",
             "footway",
             "track",
             "pedestrian"]

ROAD_TAGS = ["living_street",
             "primary",
             "secondary",
             "tertiary",
             "unclassified",
             "residential",
             "service",
             "primary_link",
             "secondary_link",
             "tertiary_link"]

MOTORWAY_TAGS = ["motorway",
                 "motorway_link",
                 "trunk",
                 "trunk_link"]

CYCLE_TAGS = ["cycleway"]

walk_tags = PATH_TAGS + ROAD_TAGS
bike_tags = ROAD_TAGS + CYCLE_TAGS
car_tags = ROAD_TAGS + MOTORWAY_TAGS

pedestrian_only_tags = PATH_TAGS
bike_only_tags = CYCLE_TAGS
car_only_tags = MOTORWAY_TAGS


### MISCELLANEOUS
traffic_light_penalty = 0.5  # 0.5 min (30 sec)


### GRAPH ATTRIBUTES
node_attributes = ['geom', 'proj_geom', 'elevation']
edge_attributes = ['geom', 'proj_geom', 'length', 'time', 'label', 'osm_ids', 'relation_id']


### SPEED VALUES [km/h]
walk_elevation_speed = {
    -15: 5.1,  # -15%
    -10: 5.1,  # -10%
    -5: 5.0,  # -5%
    0: 4.8,  # 0%
    5: 4.6,  # 5%
    10: 4.3,  # 10%
    15: 4.0  # 15%
}
bike_elevation_speed = {
    -7: 27.6,  # -7%
    -6: 26.8,  # -6%
    -5: 25.9,  # -5%
    -4: 25.1,  # -4%
    -3: 24.2,  # -3%
    -2: 23.3,  # -2%
    -1: 22.5,  # -1%
    0: 21.6,  # 0
    1: 20.2,  # 1%
    2: 18.8,  # 2%
    3: 17.3,  # 3%
    4: 15.9,  # 4%
    5: 14.4,  # 5%
    6: 13.0,  # 6%
    7: 11.6  # 7%
}
car_speed_default = 30.0
car_speed_multiplier = 0.75  # (unit-less)


### ROUTING PARAMETERS
number_of_routes = 1000  # number of routes per category

length_bins = [
    [0, 1000], [1000, 2000], [2000, 3000], [3000, 4000], [4000, 5000],
    [5000, 6000], [6000, 7000], [7000, 8000], [8000, 9000], [9000, 10000],
    [10000, 11000], [11000, 12000], [12000, 13000], [13000, 14000], [14000, 15000],
    [15000, 16000], [16000, 17000], [17000, 18000], [18000, 19000], [19000, 20000]]  # length categories


### HUMAN ROUTING PREFERENCES
feasibility_filter_walk = 1500  # 1500 m
feasibility_filter_bike = 5000  # 5000 m
feasibility_filter_car = 800  # 800 m
feasibility_filter_transitions = 8
