import requests

api_url = "http://127.0.0.1:8000"

# song_name = "Jesus Paid It All"
song_names = ["Jesus Paid It All", "SkyWay", "In Da Club"]

response = requests.post(f"{api_url}/recommendations/", json={"song_names": song_names})

if response.status_code == 200:
    recommendations = response.json()["recommendations"]
    print("recommendations:")
    for recommendation in recommendations:
        print(f"{recommendation['name']} - {recommendation['artists']}")

else:
    print("Something went wrong.")
