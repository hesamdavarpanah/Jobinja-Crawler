from argparse import ArgumentParser
from asyncio import run
from csv import writer, QUOTE_ALL

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


async def get_companies(start_scope=1, end_scope=2750):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.chrome}
        summary = []
        for i in range(start_scope, end_scope):
            base_url = f'https://jobinja.ir/company/list/کامپیوتر-فناوری-اطلاعات-و-اینترنت?page={i}'
            async with ClientSession(headers=headers) as session:
                async with session.get(base_url) as response:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                    a_tags = soup.find_all("a", {"class": "c-companyOverview"}, href=True)
                    for a in a_tags:
                        summary.append(a['href'])
        print(f"\33[34mjobinja companies urls has been taken")
        return summary
    except Exception as exception:
        return f"\33[31m{exception}"


async def get_company_details(company_urls, export_file_name="jobinja"):
    try:
        fields = ['company_name', 'date_of_establishment', 'activity', 'number_of_persons', 'website']
        summary = []
        ua = UserAgent()
        headers = {'User-Agent': ua.chrome}
        for company_url in company_urls:
            async with ClientSession(headers=headers) as session:
                async with session.get(company_url) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), 'lxml')
                        header_div_tag = soup.find("div", {"class": "c-companyHeader__info"})
                        item = list(filter(None, header_div_tag.text.split('\n')))
                        item = [x.strip(' ') for x in item]
                        item = [elem for elem in item if elem.strip()]
                        summary.append(item)
        with open(f'./{export_file_name}.csv', 'w+', encoding='utf-8', newline='') as csv_file:
            write = writer(csv_file, quoting=QUOTE_ALL, delimiter=',')
            write.writerow(fields)
            write.writerows(summary)
        return f"\33[32mJobinja crawling is done, use the ./{export_file_name}.csv"
    except Exception as exception:
        return f"\33[31m{exception}"


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='jobinja_data_crawler',
        description='Crawl Companies data for each url')
    parser.add_argument('-s', '--scope', help="end of page you want to get crawl, default is 2750")
    parser.add_argument('-f', '--filename', help="export file name, default is jobinja")
    args = parser.parse_args()
    if args.scope:
        print(run(get_company_details(run(get_companies(args.scope)))))
    else:
        print(run(get_company_details(run(get_companies()))))
