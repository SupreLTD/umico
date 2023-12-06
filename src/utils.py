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

async def get_last_page_v2(url:str):
    logger.info('Getting last page....')
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch()
        context = await browser.new_context(extra_http_headers=HEADERS)
        page = await context.new_page()
        result = await page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200

        list_content = await page.query_selector_all('li.MPProductPagination-PageItem')
        last_page = [await k.inner_text() for k in [await i.query_selector('a') for i in list_content]][-2]
        return int(last_page)


# async def get_product_links