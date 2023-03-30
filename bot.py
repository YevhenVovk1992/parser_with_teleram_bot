import os
import time
import dotenv

from aiogram import Bot, Dispatcher, executor, types

from db import PostgresDB
from parser_logger import Logger

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
API_TOKEN = os.environ.get('BOT_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
bot_logger = Logger.console_logger()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Get news', callback_data='/get_news'))
    markup.add(types.InlineKeyboardButton('Go to site', url='https://www.tesmanian.com/blogs/tesmanian-blog'))
    await message.reply("Hello!", reply_markup=markup)


@dp.message_handler(commands=['get_news'])
async def get_news(message: types.Message):
    print('start loop...')
    last_article = set()
    while True:
        connect = PostgresDB(os.environ.get('POSTGRES_DB')).db_connect()
        cursor = connect.cursor()
        bot_logger.info('Get article from DB')
        try:
            sql_string = f"""
                            SELECT title, link from article order by created_at desc limit 10;
                            """
            cursor.execute(sql_string)
        except Exception:
            bot_logger.error('Can not connect to DB')
            pass
        article_list = cursor.fetchall()
        connect.close()

        for data in article_list:
            if data[0] in last_article:
                continue
            last_article.add(data[0])
            bot_logger.info(f'Send message: {data[0]}')
            await message.answer(f'{data[0]}\n{data[1]}')
            print('Bot sleep')
            time.sleep(15)
        print('start loop again')
        time.sleep(15)


if __name__ == '__main__':
    bot_logger.info('Start bot')
    executor.start_polling(dp, skip_updates=True)