
import requests

url = "https://maryjoydebaja.onrender.com/hobby"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    print("Student:", data["student"])
    print("Hobby:", data["hobby"])
    print("Description:", data["description"])
    print("Category:", data["Category"])
else:
    print("Request failed.")
    print("Status Code:", response.status_code)
