import asyncio
import re
from asyncinit import asyncinit
from tqdm import tqdm
from loguru import logger

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from src.config import HEADERS


@asyncinit
class Umico:
    browser: Browser
    context: BrowserContext
    page: Page

    async def __init__(self, links: list):
        self.links = links
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        # self.context = await self.browser.new_context(
        #     # ignore_https_errors=True,
        #     extra_http_headers=HEADERS
        # )
        self.page = await self.browser.new_page()
        # await self.page.route(
        #     "**/*",
        #     lambda route: route.abort()
        #     if route.request.resource_type in ["image"]
        #     else route.continue_(),
        # )

    async def get_data(self, url):
        result = await self.page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200

        title = await self.page.locator('h1[itemprop="name"]').text_content()
        # title = await title.inner_text()
        print(title)
        button = await self.page.locator('a:has-text("Цены всех продавцов")').click()

        # await button.click()

        # Находим элемент на странице с помощью селектора CSS или XPath
        elements = await self.page.query_selector_all('div.MPProductOffer')

        # Получаем текст элемента
        for element in elements:
            shop = await element.query_selector('a.NameMerchant')
            shop = await shop.inner_text()
            price = await element.query_selector('span.MPPrice-RetailPrice')
            price = await price.inner_text()
            print(shop, re.sub(r"[^0-9.]", "", price))

    async def parse_price(self):
        for link in tqdm(self.links):
            await self.get_data(link)
async def main():
    a = await Umico(['https://umico.az/ru/product/251795-velosiped-vista-cn-24-zf660-orange-24-oranzhevyy'])
    await a.parse_price()
    await a.page.close()
    await a.browser.close()
asyncio.run(main())