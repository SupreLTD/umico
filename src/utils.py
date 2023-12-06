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
        soup = BeautifulSoup(await response.text(), 'lxml').find('div', class_='MPProductsListBannersWrapper').find_all(
            'a', href=True)
        links = [f"https://umico.az{i['href']}" for i in soup]
        return links


async def get_last_page(session: ClientSession, url: str):
    async with session.get(url) as response:
        logger.info(f'{response.status} | {url}')
        assert response.status == 200
        soup = BeautifulSoup(await response.text(), 'lxml').find_all('li', class_='MPProductPagination-PageItem')
        last_page = [i.find('a').text for i in soup][-2]
        return int(last_page)


async def get_last_page_v2(url: str) -> int:
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=False)
        context = await browser.new_context(
            extra_http_headers=HEADERS,
            ignore_https_errors=True,
        )
        page = await context.new_page()
        await page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["stylesheet", "image", "font"]
            else route.continue_(),
        )
        result = await page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200

        list_content = await page.query_selector_all('li.MPProductPagination-PageItem')
        last_page = [await k.inner_text() for k in [await i.query_selector('a') for i in list_content]][-2]

        return int(last_page)


async def get_browser(playwright):
    browser = await playwright.firefox.launch()
    context = await browser.new_context(extra_http_headers=HEADERS)

    return context


async def get_product_links_v2(context: get_browser, url: str) -> list:
    logger.info('Getting last page....')
    # async with async_playwright() as playwright:
    # browser = await playwright.firefox.launch()
    # context = await browser.new_context(extra_http_headers=HEADERS)
    page = await context.new_page()
    await page.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["stylesheet", "image", "font"]
        else route.continue_(),
    )

    result = await page.goto(url)
    logger.info(f'{url} | {result.status}')
    assert result.status == 200

    list_content = await page.query_selector('div.MPProductsListBannersWrapper')
    links = [await k.get_attribute('href') for k in await list_content.query_selector_all('a')]
    links = [f"https://umico.az{i}" for i in links]

    # await page.close()
    # await context.close()
    # await browser.close()
    print(len(links))


async def get_data(url: str):
    logger.info('Getting last page....')
    async with async_playwright() as playwright:
        browser = await playwright.webkit.launch(headless=False)
        context = await browser.new_context(extra_http_headers=HEADERS)
        page = await context.new_page()
        result = await page.goto(url)
        logger.info(f'{url} | {result.status}')
        assert result.status == 200

        title = await page.query_selector('h1[itemprop="name"]')
        title = await title.inner_text()
        print(title)
        button = await page.wait_for_selector('a:has-text("Цены всех продавцов")')

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
        await page.close()
        await context.close()
        await browser.close()

