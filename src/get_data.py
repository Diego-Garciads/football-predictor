import requests 
import pandas as pd

API_KEY = "68c5618eae8249d7b235a8697253b1d1"

url = "https://api.football-data.org/v4/competitions/PD/matches"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(url, headers=headers)
data = response.json()

matches = data["matches"]

df = pd.json_normalize(matches)

