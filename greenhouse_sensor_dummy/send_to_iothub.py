from azure.iot.device import IoTHubDeviceClient, Message
import time
import json
import random

CONNECTION_STRING = "HostName=group11-iot-hub.azure-devices.net;DeviceId=localTestDevice;SharedAccessKey=F2RiOlMc3NMYmOc3FECwzzZFH0TyrWf7L35Zw9+GuEA="

def generate_features():
    return {
        "Tot_PAR_std": round(random.uniform(5, 25), 2),
        "CO2air_mean": round(random.uniform(350, 900), 2),
        "Cum_irr_mean": round(random.uniform(0.1, 2.0), 2),
        "device": "localTestDevice"
    }

def main():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    print("Sending model-compatible IoT packets every 10 seconds...")

    try:
        while True:
            payload = generate_features()

            msg = Message(json.dumps(payload))
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"

            client.send_message(msg)
            print("Sent:", payload)

            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopped sending.")

    finally:
        client.shutdown()

if __name__ == "__main__":
    main()

