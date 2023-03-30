import datetime
import json
import os
import time

from dotenv import load_dotenv
from requests_html import HTMLSession
from bs4 import BeautifulSoup

from parser_logger import Logger
from db import PostgresDB


DOMAIN = 'www.tesmanian.com'
URL_BLOG = 'https://www.tesmanian.com/blogs/tesmanian-blog'
logger = Logger.console_logger()


class GetNews:
    def __init__(self):
        self.session = HTMLSession()
        self.news_array = {}

    def get_page(self, url):
        r = self.session.get(url)
        if r.status_code == 200:
            r.html.render(sleep=1, keep_page=True, scrolldown=1)
            html_page = r.text
            return html_page

    def _reload_session(self):
        self.session.close()
        self.session = HTMLSession()

    def _get_paginator(self, html_page):
        soup = BeautifulSoup(html_page, 'html.parser')
        how_many_page = soup.find('span', class_='pagination__current')
        paginator_range = int(how_many_page.text.split('/')[1])
        return paginator_range

    def _parse_page(self, html_page, domain, presence_check=False):
        new_title = {}
        soup = BeautifulSoup(html_page, 'html.parser')
        links = soup.find_all('blog-post-card')
        for ln in links:
            name = ln.find('p').text.strip().replace("'", "`")
            href = ln.find('a')['href'].strip()
            if presence_check:
                if name in self.news_array:
                    continue
                else:
                    new_title[name] = domain + href
            logger.info(f'Add the article - {name}')
            self.news_array[name] = domain + href
        if new_title:
            return new_title

    def _get_page_and_parse(self, url, domain, presence_check=False):
        success = 0
        titles = None
        while success < 3:
            try:
                first_page = self.get_page(url)
            except Exception:
                success += 1
                logger.error(f'Try get page again: {url}')
                self._reload_session()
                continue
            else:
                titles = self._parse_page(first_page, domain, presence_check=presence_check)
                success += 3
        return titles

    def get_all_news(self, url, domain, paginator_page=None):
        paginator = '?page='
        logger.info('Parser all article to db')
        first_page = self.get_page(url)
        max_paginator_page = paginator_page if paginator_page is not None else self._get_paginator(first_page)
        for page in range(max_paginator_page, 0, -1):
            logger.info(f'Get page: {page}')
            self._get_page_and_parse(url + paginator + str(page), domain)
        return self.news_array

    def save_to_db(self, new_list=None):
        if new_list is None:
            new_list = self.news_array
        logger.info('Connect to the database to save articles')
        connect = PostgresDB(os.environ.get('POSTGRES_DB')).db_connect()
        cursor = connect.cursor()
        for title, link in new_list.items():
            try:
                sql_string = f"""
                INSERT into article(title, link) values ('{title}', '{link}');
                """
                cursor.execute(sql_string)
            except Exception as msg:
                logger.error(msg)
                continue
            else:
                connect.commit()
        connect.close()

    def up_to_date(self, path, create=False):
        status = {
            'up_to_date': True,
            'date': str(datetime.datetime.now())
            }
        json_path = path + '/service.json'
        if create:
            with open(json_path, 'w') as file:
                json_object = json.dumps(status, indent=4)
                file.write(json_object)
                logger.info('service.json was created')
        if not os.path.exists(json_path):
            logger.info('service.json is missing')
            return False
        with open(json_path, 'r') as file:
            json_object = json.load(file)
            return json_object.get('up_to_date', False)

    def update_buffer_from_db(self):
        logger.info('Connect to the database to select articles')
        connect = PostgresDB(os.environ.get('POSTGRES_DB')).db_connect()
        cursor = connect.cursor()
        try:
            sql_string = f"""
                    SELECT title, link from article;
                    """
            cursor.execute(sql_string)
        except Exception as msg:
            logger.error(msg)
            pass
        for data in cursor.fetchall():
            self.news_array[data[0]] = data[1]
        connect.close()

    def write_latest_news_task(self, url, domain):
        print('Check a new article...')
        titles_are_exist = self._get_page_and_parse(url, domain, presence_check=True)
        if titles_are_exist:
            self.save_to_db(new_list=titles_are_exist)
            logger.info('Save new article')


def loop_news():
    base_dir = os.path.dirname(__file__)
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path)
    parser = GetNews()
    if not parser.up_to_date(base_dir):
        parser.get_all_news(URL_BLOG, DOMAIN)
        parser.save_to_db()
        parser.up_to_date(base_dir, create=True)
    parser.update_buffer_from_db()
    while True:
        parser.write_latest_news_task(URL_BLOG, DOMAIN)
        time.sleep(15)


def main():
    loop_news()


if __name__ == "__main__":
    main()