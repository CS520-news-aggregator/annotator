import requests
from utils.constants import OLLAMA_HOST

OLLAMA_MODEL = "orca-mini"


def generate_text_from_ollama(prompt: str):
    ollama_url = f"http://{OLLAMA_HOST}:11434/api/generate"

    try:
        response = requests.post(
            ollama_url,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            },
            timeout=5,
        )
    except requests.exceptions.RequestException as e:
        print("Could not generate text from Ollama", e)
        return

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to generate text from Ollama,", response.json())


def add_model_to_ollama():
    ollama_url = f"http://{OLLAMA_HOST}:11434/api/pull"

    try:
        response = requests.post(
            ollama_url,
            json={"name": OLLAMA_MODEL, "stream": False},
            timeout=5,
        )
    except requests.exceptions.RequestException as e:
        print("Could not add model to Ollama", e)
        return

    if response.status_code == 200:
        print("Added model to Ollama")
    else:
        print("Failed to add model to Ollama,", response.json())


def parse_ollama_response(response_json):
    response = response_json["response"]
    import pdb; pdb.set_trace()
