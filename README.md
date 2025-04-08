# Telegram Channel Post Scraper

Этот проект представляет собой скрипт на Python, который использует библиотеку Telethon для сбора постов из указанных Telegram-каналов и сохранения их в формате JSON.

## Установка

1. Убедитесь, что у вас установлен Python 3.7 или выше.
2. Установите необходимые библиотеки с помощью pip:

   ```bash
   pip install telethon
   pip install telethon.tl.types
   pip install logging
   pip install json
   pip install os

### Настройка 
Можете найти API_ID и API_HASH на сайте "https://my.telegram.org/auth".

API_ID = 'ваш_api_id'

API_HASH = 'ваш_api_hash'

CHANNELS = ['channel_name1', 'channel_name2'] Укажите каналы, из которых вы хотите собирать посты.

OUTPUT_FILE = 'posts.json' "Укажите имя файла для сохранения постов"
