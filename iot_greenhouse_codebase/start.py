import multiprocessing
import asyncio
import uvicorn

from server import app
from iot_consumer import consumer_main

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_consumer():
    asyncio.run(consumer_main())

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # required in containers
    api_proc = multiprocessing.Process(target=run_api)
    consumer_proc = multiprocessing.Process(target=run_consumer)

    api_proc.start()
    consumer_proc.start()

    api_proc.join()
    consumer_proc.join()

