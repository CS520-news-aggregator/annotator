import requests


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
