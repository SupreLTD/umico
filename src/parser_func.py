import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm
from pprint import pprint
import asyncpg

# url = 'https://umico.az/ru/merchant/4579-Webmart?from_search=true&event=view_search_tips&query=webmart&choice=Webmart'
url = 'https://umico.az/ru/product/499331-uglovaya-shlifovalnaya-mashina-bosch-gws-26-230-lvi#'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'}
response = requests.get(url, headers=headers, params={})
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
# soup = BeautifulSoup(response.text, 'lxml').find('div', class_='MPProductsListBannersWrapper').find_all('a', href=True)
# soup = BeautifulSoup(response.text, 'lxml').find_all('li', class_='MPProductPagination-PageItem')
# last_page = [i.find('a').text for i in soup][-2]
# links = [f"https://umico.az{i['href']}" for i in soup]
soup = BeautifulSoup(response.text, 'lxml')
title = soup.find('h1', itemprop="name").text
traders = soup.find('div', class_='MPProductOffers').find_all('div', class_='MPProductOffer')
traders = [(i.find('a', class_='NameMerchant').text, i.find('span', class_='MPPrice-RetailPrice').text) for i in traders]
pprint(traders)