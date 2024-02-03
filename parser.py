import asyncio

import requests
from bs4 import BeautifulSoup

from db import insert_into_invnn

cookies = {
    '_ym_uid': '1706714880461168533',
    '_ym_d': '1706714880',
    'tmr_lvid': 'acabf49f122557cc2aceb9da82827b3c',
    'tmr_lvidTS': '1706714881820',
    '_ym_isad': '1',
    '_ym_visorc': 'w',
    '_gid': 'GA1.2.622331549.1706714887',
    'sp_v5__parts_per_page': '',
    'sp_v5__contracts__order_by': '',
    'sp_v5__city': '38',
    'tmr_detect': '1%7C1706719502011',
    '_ga_Y06M7L6CME': 'GS1.1.1706714883.1.1.1706719502.58.0.0',
    '_ga': 'GA1.1.1756997368.1706714884',
}

headers = {
    'authority': 'bibinet.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '_ym_uid=1706714880461168533; _ym_d=1706714880; tmr_lvid=acabf49f122557cc2aceb9da82827b3c; tmr_lvidTS=1706714881820; _ym_isad=1; _ym_visorc=w; _gid=GA1.2.622331549.1706714887; sp_v5__parts_per_page=; sp_v5__contracts__order_by=; sp_v5__city=38; tmr_detect=1%7C1706719502011; _ga_Y06M7L6CME=GS1.1.1706714883.1.1.1706719502.58.0.0; _ga=GA1.1.1756997368.1706714884',
    'dnt': '1',
    'referer': 'https://bibinet.ru/part/krasnoyarsk/chevrolet/aveo/bamper/year/2013/?price_to=6000&part_class=used_part&isfr=1',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

params = {
    'price_to': '6000',
    'part_class': 'used_part',
    'isfr': '1',
}

URL = 'https://bibinet.ru/part/krasnoyarsk/chevrolet/aveo/bamper/year/2013/'

import aiohttp


async def fetch(url, params, cookies, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, cookies=cookies, headers=headers) as response:
            return await response.text()


async def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    parent = soup.find('div', {'class': 'list-block-v2'}).find('div')
    parts = parent.find_all('div', {'data-part-invnn': True})

    invvn_values = []
    links = {}

    for part in parts:
        part_invnn = part.get('data-part-invnn')
        invvn_values.append(part_invnn)

        part_url = part.find('a', {'class': 'title'}).attrs['href']
        part_link = f'https://bibinet.ru{part_url}'
        part_price = part.find('div', {'class': 'price-block'}).find('div').text.strip()

        links[part_invnn] = {
            "link": part_link,
            "price": part_price
        }

    return invvn_values, links


async def check_website():
    async with aiohttp.ClientSession() as session:
        html = await fetch(URL, params=params, cookies=cookies, headers=headers)

    with open('result.html', 'w', encoding='utf-8') as file:
        file.write(html)

    invvn_values, links = await parse_html(html)

    inserted_values = await insert_into_invnn(invnn_values=invvn_values)

    links = {key: value for key, value in links.items() if key in inserted_values}
    return links


if __name__ == '__main__':
    asyncio.run(check_website())
