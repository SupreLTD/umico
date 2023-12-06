import asyncio
from pprint import pprint

from aiohttp import ClientSession
from loguru import logger
from bs4 import BeautifulSoup

from src.config import HEADERS
from src.utils import get_product_links, get_last_page


async def run_parser():

    links = []
    async with ClientSession(headers=HEADERS) as session:
        pagination = await get_last_page(session, 'https://umico.az/ru/merchant/4579-Webmart?from_search=true&event=view_search_tips&query=webmart&choice=Webmart')
        tasks = []
        for i in range(1, pagination + 1):
            url = f'https://umico.az/ru/merchant/4579-Webmart?page={str(i)}&from_search=true&event=view_search_tips&query=webmart&choice=Webmart'
            task = asyncio.create_task(get_product_links(session, url))
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        result = sum(result, [])
        links.extend(result)

asyncio.run(run_parser())
