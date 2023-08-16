import json
from threading import Thread

import paho.mqtt.client as mqtt

import config
from sensorfusion import SensorFusion


def on_connect(client: mqtt.Client, userdata, flags, rc: int):
    """
    Called when client connects to the server.

    :param object client: MQTT client instance.
    :param Any userdata: User data that was set in user_data_set().
    :param dict flags: Response flags sent by the broker.
    :param int rc: Connection result.
    :raise: ConnectionError if the server is unreachable.

    """
    print(f"MQTT: {config.MQTT_CONNECTION_RESULTS[rc]}")
    if rc == 0:
        client.subscribe(config.MQTT_TOPIC_GPS)
        client.subscribe(config.MQTT_TOPIC_IMU)
        client.subscribe(config.MQTT_TOPIC_UWB)
    else:
        raise ConnectionError(f"Return code: {rc}")


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    """
    Called when client receives a message from a topic it has subsribed to.

    :param object client: MQTT client instance.
    :param Any userdata: User data that was set in user_data_set().
    :param object message: MQTTMessage instance.

    """
    sensordata = json.loads(message.payload.decode())
    userdata[message.topic](sensordata)  # datahandlerMethod(sensordata)


def main():
    client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    fusion = SensorFusion(client)
    thread = Thread(target=fusion.compute_position)
    
    # Methods for handling the sensor data: {<mqttTopic>: <method>, ...}.
    # Will be used in the on_message() callback.
    datahandlers = {
        config.MQTT_TOPIC_GPS: fusion.set_gpsdata,
        config.MQTT_TOPIC_IMU: fusion.set_imudata,
        config.MQTT_TOPIC_UWB: fusion.set_uwbdata
    }

    client.user_data_set(datahandlers)
    client.connect(host=config.MQTT_HOST, port=config.MQTT_PORT)
    thread.start()
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        fusion.loop_stop()
        client.loop_stop()

    thread.join()
    client.disconnect()


if __name__ == "__main__":
    main()
