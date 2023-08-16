from geographiclib.geodesic import Geodesic
import numpy as np

import config


def compute_lat_lon(px: float, py: float) -> tuple:
    """
    Compute the position in the global WGS84 coordinate reference system.

    :param float px: X position in the local coordinate reference system.
    :param float py: Y position in the local coordinate reference system.
    :return: Latitude and longitude values.
    :rtype: tuple.

    """
    # The origin of the indoor positioning system (IPS).
    lat1 = config.IPS_ORIGIN_LAT
    lon1 = config.IPS_ORIGIN_LON

    # Angle with respect to the positive X axis of the IPS.
    angle = np.rad2deg(np.arctan2(py, px))
    # Angle with respect to the vertical axis of the WGS84
    # reference system, -180.0..+180.0.
    azimuth = 90.0 - angle - np.abs(config.IPS_WGS84_ANGLE_OFFSET)
    if azimuth > 180.0:
        azimuth = azimuth - 360.0

    # Distance between the origin and point (px,py).
    distance = np.sqrt(np.power(px, 2) + np.power(py, 2))
    
    # Solve a direct geodesic problem.
    solution = Geodesic.WGS84.Direct(lat1, lon1, azimuth, distance)
    latitude = round(solution["lat2"], 9)
    longitude = round(solution["lon2"], 9)

    return (latitude, longitude)


def compute_xyz(lat2: float, lon2: float, height: float) -> tuple:
    """
    Compute the position in the local coordinate reference system.

    :param float lat2: Latitude.
    :param float lon2: Longitude.
    :param float height: Height.
    :return: Position as (px, py, pz).
    :rtype: tuple.

    """
    # The origin of the indoor positioning system (IPS).
    lat1 = config.IPS_ORIGIN_LAT
    lon1 = config.IPS_ORIGIN_LON
    hmsl = config.IPS_ORIGIN_HMSL

    # Solve an inverse geodesic problem.
    solution = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
    distance = solution["s12"]
    azimuth = solution["azi1"]

    # Angle with respect to the positive X axis of the IPS.
    angle = np.deg2rad(90.0 - azimuth - np.abs(config.IPS_WGS84_ANGLE_OFFSET))

    # Compute XYZ coordinates.
    px = distance * np.cos(angle)
    py = distance * np.sin(angle)
    pz = height - hmsl

    return (px, py, pz)
