import requests

def test_n8n_webhook():
    WEBHOOK_URL = "http://localhost:5678/webhook/63af4690-bc8a-4481-be96-18cf5d427225"
    data = {
        "message": "Test task from trial day",
        "source": "Test"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    print(response.json())

# Run this manually
# test_n8n_webhook()
