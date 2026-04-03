import requests

def test_route():
    url = "http://127.0.0.1:8000/api/auth/forgot-password"
    data = {"email": "test@example.com"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    test_route()
