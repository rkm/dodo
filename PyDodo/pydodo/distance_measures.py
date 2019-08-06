import pandas as pd
import numpy as np
from geopy import distance
from scipy.spatial.distance import euclidean

from .config_param import config_param
from . import request_position
from . import utils

# Default for major (equatorial) radius and flattening are 'WGS-84' values.
major_semiaxis, minor_semiaxis, ellipse_flattening = distance.ELLIPSOIDS['WGS-84']
EARTH_RADIUS = major_semiaxis * 1000 # convert to metres


def geodesic_distance(from_lat, from_lon, to_lat, to_lon, major_semiaxis=EARTH_RADIUS, flattening=ellipse_flattening):
    """
    Get geodesic distance between two (lat, lon) points in metres.

    :param major_semiaxis: Optional, the major (equatorial) radius of the ellipsoid in metres.
    :param ellipse_flattening: Optional, the ellipsoidal flattening.
    """
    utils._validate_latitude(from_lat)
    utils._validate_longitude(from_lon)
    utils._validate_latitude(to_lat)
    utils._validate_longitude(to_lon)
    utils._validate_is_positive(major_semiaxis, 'major_semiaxis')
    utils._validate_is_positive(flattening, 'flattening')

    # For GeoPy need to provide (major_semiaxis, minor_semiaxis, flattening) but
    # only major_semiaxis & flattening vals are used --> ignore minor_semiaxis
    return distance.geodesic(
        (from_lat, from_lon),
        (to_lat, to_lon),
        ellipsoid=(major_semiaxis/1000, minor_semiaxis, flattening) # convert to km
        ).meters


def great_circle_distance(from_lat, from_lon, to_lat, to_lon, radius=EARTH_RADIUS):
    """
    Get great-circle distance between two (lat, lon) points in metres.

    :param radius: Earth radius in metres.
    """
    utils._validate_latitude(from_lat)
    utils._validate_longitude(from_lon)
    utils._validate_latitude(to_lat)
    utils._validate_longitude(to_lon)
    utils._validate_is_positive(radius, 'radius')

    # convert radius to km
    earth_radius_km = radius/1000

    return distance.great_circle(
        (from_lat, from_lon),
        (to_lat, to_lon),
        radius=earth_radius_km
        ).meters


def vertical_distance(from_alt, to_alt):
    """
    Get vertical distance in metres between two altitudes (provided in metres).
    """
    utils._validate_is_positive(from_alt, 'altitude')
    utils._validate_is_positive(to_alt, 'altitude')

    return abs(from_alt - to_alt)


def convert_lat_lon_to_cartesian(lat, lon, alt = 0, radius=EARTH_RADIUS):
    """
    Calculates cartesian coordinates of a point from lat, lon and alt.

    :param alt: altitude in metres.
    :param radius: Earth radius in metres.
    """

    R = radius + alt
    lat_r = np.deg2rad(lat)
    lon_r = np.deg2rad(lon)

    x = R * np.cos(lat_r) * np.cos(lon_r)
    y = R * np.cos(lat_r) * np.sin(lon_r)
    z = R * np.sin(lat_r)

    return (x,y,z)


def euclidean_distance(from_lat, from_lon, from_alt, to_lat, to_lon, to_alt, radius=EARTH_RADIUS):
    """
    Get euclidean distance between two (lat, lon, alt) points in metres.

    :param radius: Earth radius in metres.
    """
    utils._validate_latitude(from_lat)
    utils._validate_longitude(from_lon)
    utils._validate_is_positive(from_alt, 'altitude')
    utils._validate_latitude(to_lat)
    utils._validate_longitude(to_lon)
    utils._validate_is_positive(to_alt, 'altitude')
    utils._validate_is_positive(radius, 'radius')

    from_cartesian = convert_lat_lon_to_cartesian(from_lat, from_lon, from_alt, radius)
    to_cartesian = convert_lat_lon_to_cartesian(to_lat, to_lon, to_alt, radius)

    return euclidean(from_cartesian, to_cartesian)


def get_distance(from_pos, to_pos, measure, radius=EARTH_RADIUS, flattening=ellipse_flattening):
    """
    Get distance (geodesic, great circle, vertical or euclidean) between the positions of a pair of aircraft.

    :param from_pos: A pandas Series holding the from aircraft position data.
    :param to_pos: A pandas Series holding the to aircraft position data.
    :param measure: A string, one of ['geodesic', 'great_circle', 'vertical', 'euclidean'].

    :param radius: Earth radius/major_semiaxis in metres.
    :param flattening: param passed to geodesic_distance.
    """
    if measure == 'geodesic':
        return geodesic_distance(
            from_pos['latitude'],
            from_pos['longitude'],
            to_pos['latitude'],
            to_pos['longitude'],
            major_semiaxis=radius,
            flattening=flattening
        )
    elif measure == 'great_circle':
        return great_circle_distance(
            from_pos['latitude'],
            from_pos['longitude'],
            to_pos['latitude'],
            to_pos['longitude'],
            radius=radius
        )
    elif measure == 'vertical':
        return vertical_distance(
            from_pos['altitude'],
            to_pos['altitude']
        )
    elif measure == 'euclidean':
        return euclidean_distance(
            from_pos['latitude'],
            from_pos['longitude'],
            from_pos['altitude'],
            to_pos['latitude'],
            to_pos['longitude'],
            to_pos['altitude'],
            radius=radius
        )


def get_pos_df(from_aircraft_id, to_aircraft_id):
    """
    Get position for all unique aircraft listed in from_aircraft_id & to_aircraft_id.
    Altitude is returned in feet by all_positions() so convert it to metres.

    :param from_aircraft_id: A list of strings of aircraft IDs.
    :param to_aircraft_id: A list of strings of aircraft IDs.
    :returm: A dataframe of current positions (aircraft_id are row indexes), NaN if requested aircraft ID does not exist.
    """
    utils._validate_id_list(from_aircraft_id)
    utils._validate_id_list(to_aircraft_id)

    ids = list(set(from_aircraft_id + to_aircraft_id))

    all_pos = request_position.all_positions()
    pos_df = all_pos.reindex(ids)

    SCALE_FEET_TO_METRES = 0.3048
    pos_df.loc[:, "altitude"] = SCALE_FEET_TO_METRES * pos_df["altitude"]

    return pos_df


def get_separation(from_aircraft_id, to_aircraft_id, measure, radius=EARTH_RADIUS, flattening=ellipse_flattening):
    """
    Get separation (geodesic, great circle, vertical or euclidean) betweel all pairs of "from" and "to" aircraft.

    :param from_aircraft_id: A string or list of strings of aircraft IDs.
    :param to_aircraft_id: An optional string or list of strings of aircraft IDs.
    :param measure: A string, one of ['geodesic', 'great_circle', 'vertical', 'euclidean'].

    :param radius: Earth radius/major_semiaxis in metres.
    :param radius: param passed to geodesic_distance.

    :return : A dataframe with separation between all from_aircraft_id and to_aircraft_id pairs of aircraft.
    """
    assert measure in ['geodesic', 'great_circle', 'vertical', 'euclidean'], 'Invalid value {} for measure'.format(measure)
    if to_aircraft_id == None:
        to_aircraft_id = from_aircraft_id.copy()
    if not isinstance(from_aircraft_id, list): from_aircraft_id = [ from_aircraft_id ]
    if not isinstance(to_aircraft_id, list): to_aircraft_id = [ to_aircraft_id ]

    pos_df = get_pos_df(from_aircraft_id, to_aircraft_id)

    all_distances = []
    for from_id in from_aircraft_id:
        distances = [
            get_distance(pos_df.loc[from_id], pos_df.loc[to_id], measure=measure, radius=radius, flattening=flattening)
            if not (pos_df.loc[from_id].isnull().any() or pos_df.loc[to_id].isnull().any())
            else np.nan
            for to_id in to_aircraft_id
        ]
        all_distances.append(distances)

    return pd.DataFrame(
        all_distances,
        columns = to_aircraft_id,
        index = from_aircraft_id
    )


def geodesic_separation(from_aircraft_id, to_aircraft_id=None, major_semiaxis=EARTH_RADIUS, flattening=ellipse_flattening):
    """
    Get geodesic separation in metres between the positions of all from_aircraft_id and to_aircraft_id pairs of aircraft.
    """
    return get_separation(from_aircraft_id, to_aircraft_id, measure='geodesic', radius=major_semiaxis, flattening=flattening)


def great_circle_separation(from_aircraft_id, to_aircraft_id=None, radius=EARTH_RADIUS):
    """
    Get great circle separation in metres between the positions of all from_aircraft_id and to_aircraft_id pairs of aircraft.
    """
    return get_separation(from_aircraft_id, to_aircraft_id, measure='great_circle', radius=radius)


def vertical_separation(from_aircraft_id, to_aircraft_id=None):
    """
    Get vertical separation in metres between the positions of all from_aircraft_id and to_aircraft_id pairs of aircraft.
    """
    return get_separation(from_aircraft_id, to_aircraft_id, measure='vertical')


def euclidean_separation(from_aircraft_id, to_aircraft_id=None, radius=EARTH_RADIUS):
    """
    Get euclidean separation in metres between the positions of all from_aircraft_id and to_aircraft_id pairs of aircraft.
    """
    return get_separation(from_aircraft_id, to_aircraft_id, measure='euclidean', radius=radius)
