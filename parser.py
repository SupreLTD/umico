import asyncio
import re

from aiohttp import ClientSession
from loguru import logger
from playwright.async_api import async_playwright

from config import HEADERS
from utils import get_product_links, get_last_page
from play_parser import Umico



async def get_shops_data(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, timeout=60000)
        context = await browser.new_context()
        page = await context.new_page()
        # await page.route(
        #     "**/*",
        #     lambda route: route.abort()
        #     if route.request.resource_type in ["image"]
        #     else route.continue_(),
        # )
        result = await page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200
        await page.set_extra_http_headers(headers=HEADERS)
        title = await page.query_selector('h1[itemprop="name"]')
        title = await title.inner_text()
        print(title)
        # await page.locator('a:has-text("Цены всех продавцов")').click()
        try:
            button = await page.query_selector('a:has-text("Цены всех продавцов")')
            await button.click()
            # Находим элемент на странице с помощью селектора CSS или XPath
            elements = await page.query_selector_all('div.MPProductOffer')

            # Получаем текст элемента
            for element in elements:
                shop = await element.query_selector('a.NameMerchant')
                shop = await shop.inner_text()
                price = await element.query_selector('span.MPPrice-RetailPrice')
                price = await price.inner_text()
                print(shop, re.sub(r"[^0-9.]", "", price))
        except:
            pass
        await browser.close()


async def run_parser():
    links = []
    async with ClientSession(headers=HEADERS) as session:
        pagination = await get_last_page(session,
                                         'https://umico.az/ru/merchant/4579-Webmart?from_search=true&event=view_search_tips&query=webmart&choice=Webmart')
        logger.info(f'find {pagination} pages')
        tasks = []
        for i in range(1, pagination + 1):
            url = f'https://umico.az/ru/merchant/4579-Webmart?page={str(i)}&from_search=true&event=view_search_tips&query=webmart&choice=Webmart'
            task = asyncio.create_task(get_product_links(session, url))
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        result = sum(result, [])
        links.extend(result)
    # for i in links:
    #     await get_shops_data(i)
    umico_price = await Umico(links)
    await umico_price.parse_price()
    await umico_price.browser.close()
    await umico_price.playwright.stop()

asyncio.run(run_parser())
