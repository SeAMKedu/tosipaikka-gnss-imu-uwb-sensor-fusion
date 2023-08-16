LOGFILE = "sensordata.log"

# Kalman filter (KF).
# Variance used in the matrix process noise matrix Q.
KF_Q_VARIANCE = 1e-5
# Standard deviations of the acceleration and position measurements.
KF_STD_ACC = 0.01
KF_STD_POS = 0.02
# Time step in seconds.
KF_DT = 0.1

# MQTT server on Raspberry Pi.
MQTT_HOST = "172.17.128.166"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "fusion"
MQTT_TOPIC_GPS = "sensorfusion/gps"
MQTT_TOPIC_IMU = "sensorfusion/imu"
MQTT_TOPIC_UWB = "sensorfusion/uwb"
MQTT_TOPIC_POS = "sensorfusion/position"
MQTT_CONNECTION_RESULTS = {
    0: "Connection successful",
    1: "Connection refused - incorrect protocol version",
    2: "Connection refused - invalid client identifier",
    3: "Connection refused - server unavailable",
    4: "Connection refused - bad username or password",
    5: "Connection refused - not authorised"
}

# Initial sensor data.
INIT_GPSDATA = {"lat": 0, "lon": 0, "gnssFixOk": 0}
INIT_IMUDATA = {"ax": 0, "ay": 0, "az": 0}
INIT_UWBDATA = {"px": 0, "py": 0, "pz": 0, "uwbFixOk": 0}

# Initial position.
X0 = -4.60
Y0 = -2.10
Z0 = 0.50

# Origin point of the indoor positioning system (IPS).
IPS_ORIGIN_LAT = 62.78910212
IPS_ORIGIN_LON = 22.82212920
IPS_ORIGIN_HMSL = 45521

# Angle offset between IPS and WGS84 coordinate reference systems.
IPS_WGS84_ANGLE_OFFSET = -9.0
