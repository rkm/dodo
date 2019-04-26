import pytest
import time
from requests.exceptions import HTTPError
import pandas as pd

from pydodo import (
    reset_simulation,
    create_aircraft,
    aircraft_position,
    list_route,
    direct_to_waypoint
)
from pydodo.utils import ping_bluebird
from pydodo.list_route import define_waypoint, add_waypoint

# test if can connect to BlueBird
bb_resp = ping_bluebird()


@pytest.mark.skipif(not bb_resp, reason="Can't connect to bluebird")
def test_direct_to_waypoint():
    cmd = reset_simulation()
    assert cmd == True

    aircraft_id = "TST1001"
    type = "B744"
    latitude = 0
    longitude = 0
    heading = 0
    flight_level = 250
    speed = 200

    cmd = create_aircraft(
        aircraft_id=aircraft_id,
        type=type,
        latitude=latitude,
        longitude=longitude,
        heading=heading,
        flight_level=flight_level,
        speed=speed
    )
    assert cmd == True


    position = aircraft_position(aircraft_id)

    # In the returned data frame aircraft_id is uppercase.
    aircraft_id = aircraft_id.upper()
    assert position.loc[aircraft_id]["longitude"] == 0

    wpt_name = "new_waypoint"
    wpt_lat = 45
    wpt_lon = 45
    cmd = define_waypoint(wpt_name, wpt_lat, wpt_lon)
    assert cmd == True

    # Test with an invalid waypoint, it has not been added to flight route yet
    with pytest.raises(HTTPError):
        direct_to_waypoint(aircraft_id=aircraft_id, waypoint_name=wpt_name)

    wpt_alt = 6000
    wpt_spd = 50
    cmd = add_waypoint(aircraft_id=aircraft_id, waypoint_name=wpt_name, altitude=wpt_alt, speed=wpt_spd)
    assert cmd == True

    # Give the command to head to waypoint.
    cmd = direct_to_waypoint(aircraft_id=aircraft_id, waypoint_name=wpt_name)
    assert cmd == True

    # Check that the heading has changed.
    time.sleep(1)
    new_position = aircraft_position(aircraft_id)
    assert new_position.loc[aircraft_id]["longitude"] > longitude

    # access route information
    route = list_route(aircraft_id)
    assert isinstance(route, pd.DataFrame)
    assert len(route.index) == 1
    assert isinstance(route.sim_t, int)
    assert isinstance(route.aircraft_id, str)
    assert route.aircraft_id == aircraft_id
    assert route.iloc[0]["waypoint_name"] == wpt_name.upper()
    assert route.iloc[0]["requested_altitude"] == wpt_alt
    assert route.iloc[0]["requested_speed"] == wpt_spd
    assert route.iloc[0]["current"] == True
