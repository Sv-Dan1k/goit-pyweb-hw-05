import platform
import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta


class CurrencyRatesFetcher:
    BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='

    def __init__(self, days):
        self.days = days

    async def fetch_rates(self):
        task_list = []
        async with aiohttp.ClientSession() as session:
            for day in range(self.days):
                date = (datetime.now() - timedelta(days=day)).strftime('%d.%m.%Y')
                task_list.append(self.fetch_rate_for_date(session, date))
            results = await asyncio.gather(*task_list)
        return results

    async def fetch_rate_for_date(self, session, date):
        url = self.BASE_URL + date
        try:
            async with session.get(url) as response:
                result = await response.json()
                return self.parse_response(date, result)
        except aiohttp.ClientError as e:
            print(f"Error fetching data for {date}: {e}")
            return {date: 'Error fetching data'}

    def parse_response(self, date, data):
        rates = {'EUR': {}, 'USD': {}}
        for rate in data.get('exchangeRate', []):
            if rate.get('currency') in rates:
                rates[rate['currency']] = {
                    'sale': rate.get('saleRate'),
                    'purchase': rate.get('purchaseRate')
                }
        return {date: rates}


async def main(days):
    fetcher = CurrencyRatesFetcher(days)
    results = await fetcher.fetch_rates()
    print(results)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: py main.py <number_of_days>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
        if days < 1 or days > 10:
            raise ValueError("Number of days must be between 1 and 10.")
    except ValueError as e:
        print(e)
        sys.exit(1)

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(days))
