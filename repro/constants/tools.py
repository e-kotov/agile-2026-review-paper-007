length_bins = [
        [0, 1000], [1000, 2000], [2000, 3000], [3000, 4000], [4000, 5000],
        [5000, 6000], [6000, 7000], [7000, 8000], [8000, 9000], [9000, 10000],
        [10000, 11000], [11000, 12000], [12000, 13000], [13000, 14000], [14000, 15000],
        [15000, 16000], [16000, 17000], [17000, 18000], [18000, 19000], [19000, 20000]
    ]

modes = ['walk', 'bike', 'transition_bike', 'bus', 'transition_bus',
             'tram', 'transition_tram', 'subway', 'transition_subway',
             'train', 'transition_train', 'car', 'transition_car']

modes_without_transition = ['walk', 'bike', 'bus', 'tram', 'subway', 'train'] #, 'car']
PT_modes = ['bus', 'tram', 'subway', 'train']
# mapping of column names to modes
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

column_mapping = {
    'walk_percentage': 'walk',
    'walk_time_perc': 'walk',
    'bike_percentage': 'bike',
    'bike_time_perc': 'bike',
    'transition_bike_percentage': 'transition_bike',
    'car_percentage': 'car',
    'car_time_perc': 'car',
    'transition_car_percentage': 'transition_car',
    'bus_percentage': 'bus',
    'bus_time_perc': 'bus',
    'transition_bus_percentage': 'transition_bus',
    'tram_percentage': 'tram',
    'tram_time_perc': 'tram',
    'transition_tram_percentage': 'transition_tram',
    'subway_percentage': 'subway',
    'subway_time_perc': 'subway',
    'transition_subway_percentage': 'transition_subway',
    'train_percentage': 'train',
    'train_time_perc': 'train',
    'transition_train_percentage': 'transition_train'
}

# set colors for the pie chart
colors_outer = {'Car': '#808080', 'Public Transportation': '#ffbf00', 'Active Modes': '#90ee90'}
# colors_inner = {'car': '#808080', 'walk': "#7a4f83", 'bike': "#6a9646",
#                     'bus': '#faf0be', 'tram': '#fff600','subway': '#ff9f00','train': '#efcc00'}

colors_inner = {
    'walk':  "#9A7FA0",  # lighter muted plum
    'bike':  "#7FAE98",  # lighter desaturated teal
    'bus':   "#F2EAD0",  # very light warm beige
    'tram':  "#E6DC73",  # lighter muted mustard yellow
    'subway':"#E0A36A",  # lighter soft burnt orange
    'train': "#B5A759"   # lighter golden ochre
}

custom_order = ['walk',  'bike', 'transition_bike', 'bus',
                'transition_bus', 'tram', 'transition_tram', 'subway',
                'transition_subway', 'train', 'transition_train',
                'car', 'transition_car']


rename_dict = {
'combo_trans2_walk375_bike1250': 'C1–W375–B1250',
'combo_trans4_walk750_bike2500': 'C2–W750–B2500',
'combo_trans6_walk1125_bike3750': 'C3–W1125–B3750',
'feasibility_filter_bike_1250': 'BikeThreshold_1250',
'feasibility_filter_bike_2500': 'BikeThreshold_2500',
'feasibility_filter_bike_3750' : 'BikeThreshold_3750',
'feasibility_filter_transitions_2': 'TransitionThreshold_1',
'feasibility_filter_transitions_4': 'TransitionThreshold_2',
'feasibility_filter_transitions_6': 'TransitionThreshold_3',
'feasibility_filter_walk_1125': 'WalkThreshold_1125',
'feasibility_filter_walk_750': 'WalkThreshold_750',
'feasibility_filter_walk_375': 'WalkThreshold_375',
'unique_route_nr_filters': 'Baseline Preferences',
'unique_route_nr_nofilters': 'Pure Fastest Path',
}