# Defining tags

# "highway" tags that are used for analysis.
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

PUBLIC_TRANSPORT_TAGS_RELATIONS = ['bus',
                                   'tram',
                                   'subway',
                                   'train',
                                   'light_rail']

CYCLE_TAGS = ["cycleway"]

walk_tags = PATH_TAGS + ROAD_TAGS
bike_tags = ROAD_TAGS + CYCLE_TAGS
car_tags = ROAD_TAGS + MOTORWAY_TAGS

pedestrian_only_tags = PATH_TAGS
bike_only_tags = CYCLE_TAGS
car_only_tags = MOTORWAY_TAGS
