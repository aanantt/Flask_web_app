from bs4 import BeautifulSoup
import requests
url=requests.get("http://127.0.0.1:5000/get_users")
text=url.json()
print(text)
