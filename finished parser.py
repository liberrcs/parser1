import asyncio
import threading
import tkinter as tk
from tkinter import ttk
import aiosqlite
from telethon import TelegramClient
import json

# Конфиг Telegram API
API_ID = ''  # Введите API_ID
API_HASH = ''  # Введите API_HASH
CHANNELS = ['']  # Введите ваши каналы

DB_PATH = 'posts.db'


client = TelegramClient('session_name', API_ID, API_HASH)


parsing_thread = None
stop_event = threading.Event()

db_lock = asyncio.Lock()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                message_id INTEGER,
                channel TEXT,
                date TEXT,
                text TEXT,
                files TEXT,
                links TEXT,
                views INTEGER,
                comments BOOLEAN
            )
        ''')
        await db.commit()

async def save_post(post):
    async with db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO posts 
                (id, message_id, channel, date, text, files, links, views, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post['id'],
                post['message_id'],
                post['channel'],
                post['date'],
                post['text'],
                json.dumps(post['files']),
                json.dumps(post['links']),
                post['views'],
                post['comments']
            ))
            await db.commit()

async def parse_channels():
    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            if hasattr(entity, 'channel_id') or hasattr(entity, 'chat_id'):
                async for message in client.iter_messages(entity, limit=50):
                    if stop_event.is_set():
                        return  

                    post = {
                        'id': message.id,
                        'message_id': message.id,
                        'channel': channel,
                        'date': message.date.isoformat() if message.date else None,
                        'text': message.message if message.message else '',
                        'files': [],
                        'links': [],
                        'views': getattr(message, 'views', 0),
                        'comments': hasattr(message, 'reply_to_msg_id') and message.reply_to_msg_id is not None
                    }

                    # Файлы и ссылки 
                    if message.media:
                        post['files'].append(str(message.media))
                    if message.entities:
                        for entity in message.entities:
                            if hasattr(entity, 'url'):
                                post['links'].append(entity.url)

                    await save_post(post)
        except Exception as e:
            print(f"Ошибка при парсинге {channel}: {e}")

# Запуск парсинга с блокировками
def start_parsing():
    global parsing_thread

    async def run():
        await init_db()
        while not stop_event.is_set():
            await parse_channels()
            await asyncio.sleep(10)  # интервал между запусками

    def thread_func():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())

    stop_event.clear()
    parsing_thread = threading.Thread(target=thread_func)
    parsing_thread.start()

def stop_parsing():
    stop_event.set()
    if parsing_thread and parsing_thread.is_alive():
        parsing_thread.join()

# Получение данных 
async def fetch_posts():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT * FROM posts ORDER BY date DESC LIMIT 50')
        rows = await cursor.fetchall()
        return rows

# Обновление таблицы 
def update_table(tree):
    rows = asyncio.run(fetch_posts())
    
    # Очистка текущих данных таблицы
    for row in tree.get_children():
        tree.delete(row)

    # Вставка новых данных
    for row in rows:
        tree.insert('', tk.END, values=row)


def create_gui():
    root = tk.Tk()
    root.title("Парсер Telegram каналов")
    root.geometry("900x500")

    frame_controls = ttk.Frame(root)
    frame_controls.pack(pady=10)

    btn_start = ttk.Button(frame_controls, text="Запустить парсинг", command=start_parsing)
    btn_stop = ttk.Button(frame_controls, text="Остановить парсинг", command=stop_parsing)
    btn_refresh = ttk.Button(frame_controls, text="Обновить данные", command=lambda: update_table(tree))

    btn_start.pack(side=tk.LEFT, padx=5)
    btn_stop.pack(side=tk.LEFT, padx=5)
    btn_refresh.pack(side=tk.LEFT, padx=5)

    columns = ('ID', 'Message ID', 'Канал', 'Дата', 'Текст', 'Файлы', 'Ссылки', 'Просмотры', 'Комментарии')
    
    global tree
    tree = ttk.Treeview(root, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=tk.BOTH, expand=True)

    # Первоначальное заполнение таблицы
    update_table(tree)

    root.mainloop()

async def main():
    # Подключение клиента Telegram перед запуском GUI
    await client.start()
    
    await init_db()

if __name__ == '__main__':
    
    asyncio.run(main())

    
    create_gui()
