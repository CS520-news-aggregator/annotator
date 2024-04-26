from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import requests
from utils.constants import DB_HOST


def subscribe_to_publisher(
    subscriber_ip, subscriber_port, publisher_ip, publisher_port
):
    url = f"http://{publisher_ip}:{publisher_port}/observer/subscribe"

    try:
        response = requests.post(
            url, json={"ip_address": subscriber_ip, "port": subscriber_port}, timeout=5
        )
    except requests.exceptions.RequestException as e:
        print("Could not subscribe to publisher", e)
        return

    if response.status_code == 200:
        print("Subscribed to publisher")
    else:
        print("Failed to subscribe to publisher,", response.json())


def add_data_to_db(endpoint: str, data_model: BaseModel) -> int | str:
    db_url = f"http://{DB_HOST}:8000/{endpoint}"
    encountered_error = False

    try:
        response = requests.post(db_url, json=jsonable_encoder(data_model), timeout=5)
    except requests.exceptions.RequestException:
        print(f"Could not send data to database service due to timeout")
        encountered_error = True
    else:
        if response.status_code != 200:
            print(f"Received status code {response.status_code} from database service")
            encountered_error = True

    return -1 if encountered_error else "Successfully added data to database"


def get_data_from_db(endpoint: str, params: dict = None):
    if params is None:
        params = {}

    db_url = f"http://{DB_HOST}:8000/{endpoint}"
    encountered_error = False

    try:
        response = requests.get(db_url, params=params, timeout=5)
    except requests.exceptions.RequestException:
        print(f"Could not get data from database service due to timeout")
        encountered_error = True
    else:
        if response.status_code != 200:
            print(f"Received status code {response.status_code} from database service")
            encountered_error = True

    resp_json = response.json() if not encountered_error else None
    return resp_json if not encountered_error else None
