import re
from asyncinit import asyncinit
from tqdm import tqdm
from loguru import logger

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


@asyncinit
class Umico:
    browser: Browser
    context: BrowserContext
    page: Page

    async def __init__(self, links: list):
        self.links = links
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context(
            ignore_https_errors=True,
        )
        self.page = await self.context.new_page()
        await self.page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["stylesheet", "image", "font"]
            else route.continue_(),
        )

    async def get_data(self, url):
        result = await self.page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200

        title = await self.page.query_selector('h1[itemprop="name"]')
        title = await title.inner_text()
        print(title)
        button = await self.page.wait_for_selector('a:has-text("Цены всех продавцов")')

        await button.click()

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


