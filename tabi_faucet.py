import random
import asyncio

from loguru import logger
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from pyuseragents import random as random_useragent

from config import AMOUNT_PER_ACC, THREADS


logger.add('logger.log', format='{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}')


def random_tor_proxy():
    proxy_auth = str(random.randint(1, 0x7fffffff)) + ':' + \
        str(random.randint(1, 0x7fffffff))
    proxies = f'socks5://{proxy_auth}@localhost:9150'
    return proxies


async def get_connector():
    connector = ProxyConnector.from_url(random_tor_proxy())
    return connector


async def worker():
    while not q.empty():
        try:
            address = await q.get()

            async with ClientSession(
                connector=await get_connector(),
                headers={
                    'User-Agent': random_useragent(),
                }
            ) as client:

                response = await client.post('https://faucet-api.testnet.tabichain.com/api/faucet',
                                             json={
                                                 'address': address
                                             })
                data = await response.json()
                logger.info(f'{address} | Successfully Faucet | {data["message"]}')

        except Exception as error:
            logger.error(f'{address} | Error faucet')
            q.put_nowait(address)


async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(THREADS)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print('Bot Tabi Faucet @flamingoat\n')

    with open('address.txt', 'r') as file:
        addresses = file.read().splitlines()

    q = asyncio.Queue()

    for address in addresses * AMOUNT_PER_ACC:
        q.put_nowait(address)

    asyncio.run(main())
