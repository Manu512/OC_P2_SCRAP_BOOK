# coding: utf8
import requests
from bs4 import BeautifulSoup

url = 'http://books.toscrape.com/'

response = requests.get(url)

if response.ok: #Si Page bien charge => On passe a la suite
