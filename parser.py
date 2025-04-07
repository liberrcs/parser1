import asyncio
from telethon import *
from telethon.tl.types import *
import logging
import json
import os

#Логирование 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

#Конфиг
API_ID = ''  #API ID
API_HASH = ''  #API Hash
CHANNELS = ['channel_name1', 'channel_name2']  #Каналы для парсинга
OUTPUT_FILE = 'posts.json'  #Файл для сохранения постов

# Создание клиента
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    await client.start()
    
    posts_data = []

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            if isinstance(entity, PeerChannel):
                async for message in client.iter_messages(entity, limit=100):  #Лимит постов 100
                    post = {
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.message,
                        'files': [],
                        'links': [],
                        'views': message.views,
                        'comments': message.reply_to_msg_id is not None
                    }
                    
                    #Сбор файлов
                    if message.media:
                        post['files'].append(str(message.media))
                    
                    #Сбор ссылок
                    if message.entities:
                        for entity in message.entities:
                            if hasattr(entity, 'url'):
                                post['links'].append(entity.url)

                    posts_data.append(post)

        except Exception as e:
            logger.error(f"Ошибка при парсинге канала {channel}: {e}")

    #Сохранение данных в файл при помощи jsona
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=4)

    logger.info(f"Собрано {len(posts_data)} постов из каналов.")

if name == 'main':
    asyncio.run(main())