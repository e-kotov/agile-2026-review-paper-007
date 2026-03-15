# transition costs

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
