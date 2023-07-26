import datetime
import vk_api
from vk_api.exceptions import VkException
import sqlite3
from random import choice
from chatterbot import ChatBot
from database import *
LOGIN = '51692659'
PASSWORD = 'NO7RoppGKgstKFKpP4as'

DATABASE_NAME = 'vkinder.db'

class ConditionModel:
    def check(self, chat_data):
        pass


class Searcher(ConditionModel):
    __slots__ = ("conditions",)
    all = True

    def __init__(self, texts: (str, list), compare, i: int):
        if isinstance(texts, str):
            texts = [texts]

        self.conditions = []

        for text in texts:
            self.conditions.append(One(text, compare, i))

    def check(self, chat_data):
        for condition in self.conditions:
            if condition.check(chat_data):
                if not self.all:
                    return True
            else:
                if self.all:
                    return False

        return self.all


class All(Searcher):
    all = True


class Any(Searcher):
    all = False


class One(ConditionModel):
    __slots__ = ("x", )

    def __init__(self, text: str, compare, i: int):
        self.x = i, text, compare

    def check(self, chat_data):
        i, text, compare = self.x

        if len(chat_data) <= i:
            return compare("", text)

        return compare(chat_data[i], text)


class Two(ConditionModel):
    __slots__ = ("x", "y", "compare")

    def __init__(self, x: ConditionModel, y: ConditionModel, compare):
        self.x = x
        self.y = y
        self.compare = compare

    def check(self, chat_data):
        x = self.x.check(chat_data)
        y = self.y.check(chat_data)

        return self.compare(x, y)

class VKinder:
    def __init__(self):
        # Подключение к VK API
        self.vk_session = vk_api.VkApi(LOGIN, PASSWORD)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

        # Подключение к базе данных
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Создание таблиц в базе данных 
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                city TEXT,
                relationship_status TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                url TEXT,
                likes_count INTEGER,
                comments_count INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

def search_users(self, user_id):
        # Поиск пользователей, подходящих требованиям
        user_info = self.get_user_info(user_id)
        if not user_info:
            return None

        self.save_user(user_info)

        search_params = {
            'sex': 1 if user_info['sex'] == 2 else 2,  # Ищем противоположный пол
            'city': user_info['city'],
            'status': user_info['relationship_status'],
            'age_from': user_info['age'] - 5,
            'age_to': user_info['age'] + 5,
            'count': 10,  # Количество пользователей для поиска
            'sort': random.choice([0, 1]),  # Сортировка по рейтингу или случайная
            'has_photo': 1  # Только с фотографией
        }

        try:
            users = self.vk.users.search(**search_params)['items']
            for user in users:
                user_info = {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'age': self.calculate_age(user['bdate']),
                    'city': user.get('city', {}).get('title', 'Unknown'),
                    'relationship_status': self.get_relationship_status(user.get('relation'))
                }
                self.save_user(user_info)

                photos = self.get_random_photos(user['id'])
                if photos:
                    self.save_photos(user['id'], photos)

        except VkException as e:
            print(f'Error occurred while searching users: {str(e)}')
            return None

def get_matches(self):
        # Получение пользователей, совпадающих с требованиями
        self.cursor.execute('SELECT * FROM users')
        users = self.cursor.fetchall()
        for user in users:
            user_id = user[0]
            self.cursor.execute('''
                SELECT *
                FROM photos
                WHERE user_id = ?
                ORDER BY likes_count + comments_count DESC
                LIMIT 3
            ''', (user_id,))
            photos = self.cursor.fetchall()
            print(f'User: {user[1]} {user[2]}')
            for photo in photos:
                print(f'Photo URL: {photo[2]}')

def run(self):
        user_id = input('Enter VK user ID: ')
        self.search_users(user_id)
        self.get_matches()


if __init__ == '__init__':
    vkinder = VKinder()
    vkinder.run()