import json
import threading
import time

import numpy as np
import paho.mqtt.client as mqtt

import config
from  kalman import KalmanFilter
import geotools


class SensorFusion:
    """
    Sensor fusion class.

    Use combined measurement data from the GNSS, IMU, and UWB sensors
    to compute the position.

    :param object client: An instance of the MQTT Client.

    """
    def __init__(self, client: mqtt.Client) -> None:
        self.client = client
    
        self.gpsdata = config.INIT_GPSDATA
        self.imudata = config.INIT_IMUDATA
        self.uwbdata = config.INIT_UWBDATA
        
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()

        self.kf = KalmanFilter(config.X0, config.Y0, config.Z0, config.KF_DT)
        
        self.loop_run = True


    def set_gpsdata(self, data: dict):
        """Write GPS data."""

        self.lock1.acquire()
        self.gpsdata = data
        self.lock1.release()


    def get_gpsdata(self) -> dict:
        """Read GPS data."""

        self.lock1.acquire()
        data = self.gpsdata
        self.lock1.release()
        return data


    def set_imudata(self, data: dict):
        """Write IMU data."""

        self.lock2.acquire()
        self.imudata = data
        self.lock2.release()


    def get_imudata(self) -> dict:
        """Read IMU data."""

        self.lock2.acquire()
        data = self.imudata
        self.lock2.release()
        return data


    def set_uwbdata(self, data: dict):
        """Write UWB data."""

        self.lock3.acquire()
        self.uwbdata = data
        self.lock3.release()


    def get_uwbdata(self) -> dict:
        """Read UWB data."""

        self.lock3.acquire()
        data = self.uwbdata
        self.lock3.release()
        return data


    def loop_stop(self):
        """Stop computing the position."""
        
        self.loop_run = False


    def compute_position(self):
        """
        Use combined sensor data to compute the position.
        """
        logfile = open(config.LOGFILE, "w")

        while self.loop_run:
            # Get the sensor data.
            gpsdata = self.get_gpsdata()
            imudata = self.get_imudata()
            uwbdata = self.get_uwbdata()

            # Acceleration data.
            ax = imudata.get("ax", 0)
            ay = imudata.get("ay", 0)
            az = imudata.get("az", 0)

            # Use either UWB position data or GNSS position data.
            uwb_fix_ok = uwbdata.get("uwbFixOk", 0)
            gps_fix_ok = gpsdata.get("gnssFixOk", 0)
            
            px, py, pz = (0, 0, 0)
            positioning_system = "NA"

            # UWB anchors are within range -> use UWB position data.
            if uwb_fix_ok == 1:
                positioning_system = "UWB"
                px = uwbdata.get("px", config.X0)
                py = uwbdata.get("py", config.Y0)
                pz = uwbdata.get("pz", config.Z0)

            # UWB anchors are out of range -> use GPS position data.
            elif gps_fix_ok == 1:
                positioning_system = "GPS"
                lat2 = gpsdata.get("lat", config.IPS_ORIGIN_LAT)
                lon2 = gpsdata.get("lon", config.IPS_ORIGIN_LON)
                hmsl = gpsdata.get("hMSL", config.IPS_ORIGIN_HMSL)
                px, py, pz = geotools.compute_xyz(lat2, lon2, hmsl)
            
            # Use position from the Kalman filter.
            else:
                positioning_system = "EKF"
                px = self.kf.x[0]
                py = self.kf.x[2]
                pz = self.kf.x[4]

            # Use Kalman filter to compute the position.
            z = np.array([px, ax, py, ay, pz, az]).T
            self.kf.predict()
            self.kf.update(z)

            # Position as latitude and longitude.
            lat, lon = geotools.compute_lat_lon(self.kf.x[0], self.kf.x[2])

            data = {
                "ts": time.time_ns() // 1_000_000,
                "ps": positioning_system,
                "name": "fusion",
                "lat": lat,
                "lon": lon,
                "ekf": {
                    "px": round(self.kf.x[0], 2),
                    "ax": round(self.kf.x[1], 3),
                    "py": round(self.kf.x[2], 2),
                    "ay": round(self.kf.x[3], 3),
                    "pz": round(self.kf.x[4], 2),
                    "az": round(self.kf.x[5], 3),
                },
                "meas": {
                    "gps": {
                        "lat": gpsdata["lat"],
                        "lon": gpsdata["lon"],
                        "numSV": gpsdata.get("numSV", 0),
                        "hMSL": gpsdata.get("hMSL", 0),
                        "hAcc": gpsdata.get("hAcc", 0),
                        "vAcc": gpsdata.get("vAcc", 0),
                    },
                    "imu": {
                        "ax": imudata["ax"],
                        "ay": imudata["ay"],
                        "az": imudata["az"],
                    },
                    "uwb": {
                        "px": uwbdata["px"],
                        "py": uwbdata["py"],
                        "pz": uwbdata["pz"]
                    },
                }
            }
            print(data)
            
            position = json.dumps(data)
            logfile.write(f"{position}\n")
            self.client.publish(config.MQTT_TOPIC_POS, position)
            
            time.sleep(config.KF_DT)
