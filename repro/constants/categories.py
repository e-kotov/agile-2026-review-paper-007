# parameters for routing
# parameters for routing

number_of_routes = 1000  # number of routes per category
weight = 'time'
length_bins = [
    [0, 1000], [1000, 2000], [2000, 3000], [3000, 4000], [4000, 5000],
    [5000, 6000], [6000, 7000], [7000, 8000], [8000, 9000], [9000, 10000],
    [10000, 11000], [11000, 12000], [12000, 13000], [13000, 14000], [14000, 15000],
    [15000, 16000], [16000, 17000], [17000, 18000], [18000, 19000], [19000, 20000]
]  # length categories


modes = ['walk', 'bike', 'transition_bike', 'bus', 'transition_bus',
         'tram', 'transition_tram', 'subway', 'transition_subway',
         'train', 'transition_train', 'car', 'transition_car']

mode_groups_1 = {
    'walk': ['walk'],
    'bike': ['bike', 'transition_bike'],
    'bus': ['bus', 'transition_bus'],
    'tram': ['tram', 'transition_tram'],
    'subway': ['subway', 'transition_subway'],
    'train': ['train', 'transition_train'],
    'car': ['car', 'transition_car']
}

mode_groups = {
    'walk': ['walk'],
    'bike': ['bike'],
    'transition_bike': ['transition_bike'],
    'bus': ['bus'],
    'transition_bus': ['transition_bus'],
    'tram': ['tram'],
    'transition_tram': ['transition_tram'],
    'subway': ['subway'],
    'transition_subway': ['transition_subway'],
    'train': ['train'],
    'transition_train': ['transition_train'],
    'car': ['car'],
    'transition_car': ['transition_car']

}

mode_to_column = {
    'walk': 'walk_percentage',
    'bike': 'bike_percentage',
    'transition_bike': 'transition_bike_percentage',
    'bus': 'bus_percentage',
    'transition_bus': 'transition_bus_percentage',
    'tram': 'tram_percentage',
    'transition_tram': 'transition_tram_percentage',
    'subway': 'subway_percentage',
    'transition_subway': 'transition_subway_percentage',
    'train': 'train_percentage',
    'transition_train': 'transition_train_percentage',
    'car': 'car_percentage',
    'transition_car': 'transition_car_percentage'
}

order = ['walk', 'bike', 'bus', 'tram', 'subway', 'train', 'car']

color_mode = {
     'walk': '#7f7f7f',
    'bike': '#66a61e',
    'bus': '#e6ab02',
    'tram': '#fdc086',
    'subway': '#386cb0',
    'train': '#41b6c4',
    'car': "#da4d46",
    'transition_car': '#da4d46',
    'transition_bike' : '#66a61e',
    'transition_tram' : '#fdc086',
    'transition_subway' : '#386cb0',
    'transition_train' : '#41b6c4',
    'transition_bus' : '#e6ab02'
}

custom_order = ['walk',  'bike', 'transition_bike', 'bus', 
                'transition_bus', 'tram', 'transition_tram', 'subway', 
                'transition_subway', 'train', 'transition_train', 
                'car', 'transition_car']

custom_order_walk_pt = ['walk',  'bus', 
                'transition_bus', 'tram', 'transition_tram', 'subway', 
                'transition_subway', 'train', 'transition_train', 
                ]

ranges = ['0-1000', '1000-2000', '2000-3000', '3000-4000', '4000-5000',
          '5000-6000', '6000-7000', '7000-8000', '8000-9000', '9000-10000', '10000-11000',
          '11000-12000', '12000-13000', '13000-14000', '14000-15000', '15000-16000',
          '16000-17000', '17000-18000', '18000-19000', '19000-20000']

columns_to_average = [
    'sum_length_for_time', 'sum_time_for_time',
    'walk_length_perc', 'walk_time_perc', 'bike_length_perc', 'bike_time_perc',
    'transition_bike_length_perc', 'transition_bike_time_perc',
    'bus_length_perc', 'bus_time_perc', 'transition_bus_length_perc',
    'transition_bus_time_perc', 'tram_length_perc', 'tram_time_perc',
    'transition_tram_length_perc', 'transition_tram_time_perc',
    'subway_length_perc', 'subway_time_perc', 'transition_subway_length_perc',
    'transition_subway_time_perc', 'train_length_perc', 'train_time_perc',
    'transition_train_length_perc', 'transition_train_time_perc',
    'car_length_perc', 'car_time_perc', 'transition_car_length_perc',
    'transition_car_time_perc'
]