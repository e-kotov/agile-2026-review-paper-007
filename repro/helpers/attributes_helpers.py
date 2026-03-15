"""Helper functions to compute attributes."""
import os.path

import numpy as np
import pandas as pd

from constants.speeds import walk_elevation_speed, bike_elevation_speed


def get_walk_speed(elevation):
    """
    Calculates the speed required for walking based on the slope [%] of the terrain.
    The slope is rounded to [-15, -10, -5, 0, 5, 10, 15] and the corresponding value from
    the dictionary walk_elevation_speed is returned. (see constants/speeds.py)
    """

    if isinstance(elevation, list):
        speeds = []
        for element in elevation:
            element = np.tan(np.radians(element)) * 100  # convert element from degrees to slope [%]
            element = 5 * round(element/5)  # round to nearest slope value (in steps of 5)
            if element < -15:
                # every slope steeper than -15% is rounded to -15%
                speeds.append(walk_elevation_speed[-15])
            elif element > 15:
                # every slope steeper than 15% in rounded to 15%
                speeds.append(walk_elevation_speed[15])
            else:
                speeds.append(walk_elevation_speed[element])
        return speeds
    else:
        elevation = np.tan(np.radians(elevation)) * 100  # convert elevation from degrees to slope [%]
        elevation = 5 * round(elevation / 5)  # round to nearest slope value (in steps of 5)
        if elevation < -15:
            # every slope steeper than -15% is rounded to -15%
            return walk_elevation_speed[-15]
        elif elevation > 15:
            # every slope steeper than 15% in rounded to 15%
            return walk_elevation_speed[15]
        else:
            return walk_elevation_speed[elevation]


def get_bike_speed(elevation):
    """
    Calculates the speed required for biking based on the slope [%] of the terrain.
    The slope is rounded to the nearest integer and the corresponding value from
    the dictionary bike_elevation_speed is returned. (see constants/speeds.py)
    """
    if isinstance(elevation, list):
        speeds = []
        for element in elevation:
            element = np.tan(np.radians(element)) * 100  # convert element from degrees to slope [%]
            element = round(element)  # round to nearest slope value
            if element < -7:
                # every additional 1% of downhill, mean speed increased by 0.86 km/h (Parkin J. and Rotheram J., 2010)
                temp = bike_elevation_speed[-7]
                speeds.append(temp + (-element - 7) * 0.86)
            elif element > 7:
                if element > 12:
                    # set the speed to walking for highest slope (= pushing the bike)
                    temp = walk_elevation_speed[15]
                    speeds.append(temp)
                else:
                    # every additional 1% of uphill, mean speed reduced by 1.44 km/h (Parkin J. and Rotheram J., 2010)
                    temp = bike_elevation_speed[7]
                    speeds.append(temp - (element - 7) * 1.44)
            else:
                speeds.append(bike_elevation_speed[element])
        return speeds
    else:
        elevation = np.tan(np.radians(elevation)) * 100  # convert element from degrees to slope [%]
        elevation = round(elevation)  # round to nearest slope value
        if elevation < -7:
            # every additional 1% of downhill, mean speed increased by 0.86 km/h (Parkin J. and Rotheram J., 2010)
            temp = bike_elevation_speed[-7]
            speed = temp + (-elevation - 7) * 0.86
            return speed
        elif elevation > 7:
            if elevation > 12:
                # set the speed to walking for highest slope (= pushing the bike)
                temp = walk_elevation_speed[15]
                speed = temp
            else:
                # every additional 1% of uphill, mean speed reduced by 1.44 km/h (Parkin J. and Rotheram J., 2010)
                temp = bike_elevation_speed[7]
                speed = temp - (elevation - 7) * 1.44
            return speed
        else:
            return bike_elevation_speed[elevation]


def time_to_timedelta(time_str):
    hour, minute, second = map(int, time_str.split(':'))
    return pd.Timedelta(hours=hour, minutes=minute, seconds=second)


def standardize_stop_names(name):
    name = name.lower()
    name = name.replace(' ', ' ')
    name = name.replace('-', ' ')
    name = name.replace(',', ' ')
    name = name.replace('/', ' ')
    name = name.replace('str.', 'straße')
    name = name.replace('bhf.', 'bahnhof')
    name = name.replace('hbf.', 'hauptbahnhof')
    name = name.replace('pl.', 'platz')
    name = name.replace('g.', 'gasse')
    name = name.replace('kh.', 'krankenhaus')
    name = name.replace('st.', 'sankt')
    name = name.replace('ó', 'o')
    name = name.replace('é', 'e')
    name = name.replace('á', 'a')
    name = name.replace('ß', 'ss')
    name = name.replace('&', ' und ')
    name = name.replace('.', ' ')
    if name.startswith('wien '):
        name = name.replace('wien ', '')
    if name.startswith('bahnhof ') or name.endswith(' bahnhof'):
        name = name.replace('bahnhof', '')
    name = ' '.join(name.split())
    name = name.split(' ')
    name.sort()
    if 's+u' in name:
        name.remove('s+u')
    if 's' in name:
        name.remove('s')
    if 'u' in name:
        name.remove('u')
    name = ' '.join(name)
    return name


def update_public_transport_with_timetable(name, stops, data_osm, path):
    # GTFS reference: https://gtfs.org/schedule/reference/

    if name in ['bus', 'tram', 'subway']:
        operator = 'wiener_linien'
    elif name in ['train']:
        operator = 'GTFS_OP_2023_obb'
    else:
        operator = ''
        print('Check mode of transport!')

    # read files
    gtfs_times = pd.read_csv(os.path.join(path, operator, 'stop_times.txt'))
    gtfs_stops = pd.read_csv(os.path.join(path, operator, 'stops.txt'))
    gtfs_trips = pd.read_csv(os.path.join(path, operator, 'trips.txt'))
    gtfs_routes = pd.read_csv(os.path.join(path, operator, 'routes.txt'))

    matched_manually = pd.DataFrame(
        [['Breitenlee, Arnikaweg', 'Breitenleer Straße/Arnikaweg'],
         ['Breitenlee, Spargelfeldstraße', 'Breitenleer Straße/Spargelfeldstraße'],
         ['Breitenlee, Ziegelhofstraße', 'Breitenleer Straße/Ziegelhofstraße'],
         ['Neu Breitenlee', 'Neubreitenlee'],
         ['Spargelfeldstraße', 'Oberfeldgasse/Spargelfeldstr.'],
         ['Quellenstraße/Knöllgasse', 'Knöllgasse'],
         ['Davidgasse/Knöllgasse', 'Davidgasse'],
         ['Hadersdorf, Hauptstraße', 'Hadersdorfer, Hauptstraße'],
         ['Etrichstraße, Hoefftgasse', 'Hoefftgasse'],
         ['Basler Gasse', 'Siebenhirten, Basler Gasse'],
         ['Nußdorfer Friedhof', 'Nußdorf Friedhof'],
         ['Breitenseer Straße, Braillegasse', 'Braillegasse'],
         ['Lützowgasse', 'Linzer Str./Lützowgasse'],
         ['Zehetnergasse', 'Linzer Straße/Zehetnergasse'],
         ['Unter St. Veit, Verbindungsbahn', 'Verbindungsbahn'],
         ['Frachtenbahnhof Lobau', 'Frachtenbahnhof Lobau Hafen'],
         ['Altmannsdorfer Straße', 'Breitenfurter Straße/Altmannsdorfer Straße'],
         ['Märzstraße', 'Johnstraße/Märzstraße'],
         ['Neukagran', 'Neu-Kagran'],
         ['Dampfkraftwerk', 'Dampfkraftwerk Donaustadt'],
         ['Herbeckstraße', 'Gersthof, Herbeckstraße'],
         ['Oberdorfstraße', 'Aspern, Oberdorfstraße'],
         ['Aspern, Zachgasse', 'Zachgasse'],
         ['Alsegger Straße, Czartoriskygasse', 'Alsegger Straße/Czartoryskigasse'],
         ['Lederergasse/Josefstädter Straße', 'Lederergasse'],
         ['Ameisbachzeile, Hanuschkrankenhaus', 'Ameisbachzeile'],
         ['Hanuschkrankenhaus', 'Hanusch-Krankenhaus'],
         ['Pensionistenwohnhaus Prater', 'Pensionisten-Wohnhaus Prater'],
         ['Raxstraße, Betriebsgarage', 'Betriebshof Raxstraße'],
         ['Laaer Berg Kurpark Nordeingang', 'Kurpark Nordeingang'],
         ['Laaer Berg Kurpark Nordosteingang', 'Kurpark Nordosteingang'],
         ['Pensionistenwohnhaus Laaerberg', 'Pensionisten-Wohnhaus Laaer Berg'],
         ['Angermayrgasse', 'Angermayergasse'],
         ['Kleingartenverein Alsrückenweg', 'KGV Alsrückenweg'],
         ['Wien Mitte', 'Wien Mitte-Landstraße'],
         ['Wien Hbf', 'Wien Hauptbahnhof'],
         ['Wien Franz-Josefs-Bf', 'Wien Franz-Josefs-Bahnhof'],
         ['Flughafen Wien', 'Flughafen Wien Bahnhof'],
         ['Purkersdorf Zentrum', 'Purkersdorf Zentrum Bahnhof'],
         ['Unter Tullnerbach', 'Untertullnerbach Bahnhof'],
         ['Tullnerbach-Pressbaum', 'Tullnerbach-Pressbaum Bahnhof'],
         ['Wien Hbf Autoreisezug', 'Wien Hauptbahnhof Autoreisezug'],
         ['Siebenbrunn-Leopoldsdorf', 'Siebenbrunn-Leopoldsdorf Bahnhof']], columns=['osm_name', 'timetable_name'])

    if name == 'bus':
        ref = 3
    elif name == 'tram':
        ref = 0
    elif name == 'subway':
        ref = 1
    elif name == 'train':
        ref = 2
    else:
        ref = 9999

    # filter routes by type
    gtfs_routes_filtered = gtfs_routes[gtfs_routes.route_type == ref]

    # get trips of those filtered routes
    gtfs_trips_filtered = gtfs_trips[gtfs_trips.route_id.isin(gtfs_routes_filtered.route_id.values)]

    # get times of those filtered trips
    gtfs_times_filtered = gtfs_times[gtfs_times.trip_id.isin(gtfs_trips_filtered.trip_id.values)]

    # get stops of those filtered times
    gtfs_stops_filtered = gtfs_stops[gtfs_stops.stop_id.isin(gtfs_times_filtered.stop_id.values)]

    # standardize stop names to simplify matching
    gtfs_stops_filtered['mod_stop_name'] = gtfs_stops_filtered['stop_name'].apply(standardize_stop_names)

    # merged dataframe
    merged_df = gtfs_times_filtered.merge(gtfs_stops_filtered[['stop_id', 'stop_name']], on='stop_id', how='left')
    merged_df.sort_values(['trip_id', 'stop_sequence'], inplace=True)

    count = 0
    minutes = []
    new_times = []
    non_matched_segments = []
    for _, data in data_osm.iterrows():
        try:
            u_name = stops[stops.osm_id == data.osm_id1].tags.values[0].get('name')
            v_name = stops[stops.osm_id == data.osm_id2].tags.values[0].get('name')
        except:
            new_times.append(0)
            continue

        if u_name is None or v_name is None:
            new_times.append(0)
            non_matched_segments.append([u_name, v_name])
            continue

        stations_found = False

        if u_name in gtfs_stops_filtered.stop_name.values and v_name in gtfs_stops_filtered.stop_name.values:
            count += 1
            stations_found = True
        elif u_name in gtfs_stops_filtered.stop_name.values and v_name in matched_manually.osm_name.values:
            count += 1
            v_name = matched_manually[matched_manually.osm_name == v_name].timetable_name.iloc[0]
            stations_found = True
        elif u_name in matched_manually.osm_name.values and v_name in gtfs_stops_filtered.stop_name.values:
            u_name = matched_manually[matched_manually.osm_name == u_name].timetable_name.iloc[0]
            count += 1
            stations_found = True
        elif u_name in matched_manually.osm_name.values and v_name in matched_manually.osm_name.values:
            count += 1
            u_name = matched_manually[matched_manually.osm_name == u_name].timetable_name.iloc[0]
            v_name = matched_manually[matched_manually.osm_name == v_name].timetable_name.iloc[0]
            stations_found = True
        else:
            mod_u_name = standardize_stop_names(u_name)
            mod_v_name = standardize_stop_names(v_name)
            if mod_u_name in gtfs_stops_filtered.mod_stop_name.values and mod_v_name in gtfs_stops_filtered.mod_stop_name.values:
                count += 1
                stations_found = True
                u_name = gtfs_stops_filtered[gtfs_stops_filtered.mod_stop_name == mod_u_name].stop_name.iloc[0]
                v_name = gtfs_stops_filtered[gtfs_stops_filtered.mod_stop_name == mod_v_name].stop_name.iloc[0]
            else:
                new_times.append(0)
                non_matched_segments.append([u_name, v_name])
                # print(data.relation_name, u_name, '-', mod_u_name, '---',  v_name, '-', mod_v_name)

        if stations_found:
            # get times at both stations start and end
            start_times = merged_df.loc[merged_df['stop_name'] == u_name,
            ['trip_id', 'departure_time', 'stop_sequence']].drop_duplicates()
            end_times = merged_df.loc[merged_df['stop_name'] == v_name,
            ['trip_id', 'departure_time', 'stop_sequence']].drop_duplicates()

            # merge the start and end times based on the route_type and trip_id
            times_merged = start_times.merge(end_times, on=['trip_id'], suffixes=('_start', '_end'))

            # filter trips where the stop_sequence for start_station is less than the stop_sequence for end_station
            times_merged = times_merged[times_merged['stop_sequence_start'] < times_merged['stop_sequence_end']]

            # calculate the travel time between the start and end stations for each trip group
            times_merged['travel_time'] = times_merged['departure_time_end'].apply(time_to_timedelta) - times_merged[
                'departure_time_start'].apply(time_to_timedelta)

            if len(times_merged) > 0:
                mean_time_sec = times_merged.travel_time.mean().total_seconds()
                minutes.append(mean_time_sec/60)
                new_times.append(mean_time_sec/60)
            else:
                new_times.append(0)
                non_matched_segments.append([u_name, v_name])

    data_osm['time'] = new_times
    idx = np.where(data_osm['time'] == 0)[0]
    data_osm.loc[idx, 'time'] = np.mean(minutes)

    return data_osm['time']
