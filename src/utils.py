import asyncio
from aiohttp import ClientSession
from loguru import logger
from bs4 import BeautifulSoup
from tenacity import retry
import re
from playwright.async_api import async_playwright
from src.config import HEADERS

async def get_product_links(session: ClientSession, url: str):
    async with session.get(url) as response:
        logger.info(f'{response.status} | {url}')
        assert response.status == 200
        soup = BeautifulSoup(await response.text(), 'lxml').find('div', class_='MPProductsListBannersWrapper').find_all('a', href=True)
        links = [f"https://umico.az{i['href']}" for i in soup]
        return links


async def get_last_page(session: ClientSession, url: str):
    async with session.get(url) as response:
        logger.info(f'{response.status} | {url}')
        assert response.status == 200
        soup = BeautifulSoup(await response.text(), 'lxml').find_all('li', class_='MPProductPagination-PageItem')
        last_page = [i.find('a').text for i in soup][-2]
        return int(last_page)


