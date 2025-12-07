import json
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from model_inference import predict
from logging_utils import log_event
import os

CONNECTION_STRING = os.getenv("EH_CONNECTION_STRING")
EVENTHUB_NAME = os.getenv("EH_NAME")

# ----------------------------------------------------
# Map incoming IoT telemetry to model's 3 real features
# ----------------------------------------------------
def parse_to_model_features(raw):
    return {
        "Tot_PAR_std": raw.get("Tot_PAR_std", raw.get("par_std", 0.0)),
        "CO2air_mean": raw.get("CO2air_mean", raw.get("co2", 0.0)),
        "Cum_irr_mean": raw.get("Cum_irr_mean", raw.get("irrigation", 0.0))
    }

# ----------------------------------------------------
# EventHub callback
# ----------------------------------------------------
async def on_event(partition_context, event):
    try:
        msg = json.loads(event.body_as_str())
        log_event("iot_message_received", message=msg)
    except Exception as e:
        log_event("iot_message_parse_error", error=str(e))
        return

    features = parse_to_model_features(msg)

    try:
        pred = predict(features)
        log_event("iot_prediction", input=features, prediction=pred)
    except Exception as e:
        log_event("iot_prediction_error", input=features, error=str(e))

    await partition_context.update_checkpoint(event)

# ----------------------------------------------------
# Main consumer
# ----------------------------------------------------
async def consumer_main():
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STRING,
        consumer_group="$Default",
        eventhub_name=EVENTHUB_NAME,
    )

    log_event("iot_consumer_started")

    async with client:
        await client.receive(
            on_event=on_event,
            starting_position="-1"
        )

if __name__ == "__main__":
    asyncio.run(consumer_main())

