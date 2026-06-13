import requests

def get_sample_users():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users"
    )

    return response.json()