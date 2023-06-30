import datetime
import vk_api
from vk_api.exceptions import VkException
import random
import sqlite3

LOGIN = '51692659'
PASSWORD = 'NO7RoppGKgstKFKpP4as'

DATABASE_NAME = 'vkinder.db'

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

    def get_user_info(self, user_id):
        # Получение информации о пользователе из VK
        try:
            user = self.vk.users.get(user_ids=user_id, fields='bdate,city,relation')[0]
            user_info = {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'age': self.calculate_age(user['bdate']),
                'city': user.get('city', {}).get('title', 'Unknown'),
                'relationship_status': self.get_relationship_status(user.get('relation'))
            }
            return user_info
        except VkException as e:
            print(f'Error occurred while getting user info: {str(e)}')
            return None
@staticmethod
def calculate_age(birth_date):
        # Вычисление возраста пользователя на основе его даты рождения
        if birth_date:
            birth_year = int(birth_date.split('.')[-1])
            current_year = datetime.now().year
            age = current_year - birth_year
            return age
        else:
            return None

@staticmethod
def get_relationship_status(status_id):
        # Получение текстового представления семейного положения пользователя
        statuses = {
            1: 'Single',
            2: 'In a relationship',
            3: 'Engaged',
            4: 'Married',
            5: 'It\'s complicated',
            6: 'Actively searching',
            7: 'In love',
            8: 'In a civil union',
            0: 'Unknown'
        }
        return statuses.get(status_id, 'Unknown')

def save_user(self, user_info):
        # Сохранение информации о пользователе в базу данных
        self.cursor.execute('INSERT OR REPLACE INTO users (id, first_name, last_name, age, city, relationship_status) VALUES (?, ?, ?, ?, ?, ?)', (
            user_info['id'],
            user_info['first_name'],
            user_info['last_name'],
            user_info['age'],
            user_info['city'],
            user_info['relationship_status']
        ))
        self.conn.commit()

def get_random_photos(self, user_id):
        # Получение топ-3 популярных фотографий профиля пользователя
        try:
            photos = self.vk.photos.get(owner_id=user_id, album_id='profile', extended=1, count=100)['items']
            photos.sort(key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
            top_photos = photos[:3]
            return top_photos
        except VkException as e:
            print(f'Error occurred while getting user photos: {str(e)}')
            return None

def save_photos(self, user_id, photos):
        # Сохранение информации о фотографиях пользователя в базу данных
        for photo in photos:
            self.cursor.execute('INSERT OR REPLACE INTO photos (id, user_id, url, likes_count, comments_count) VALUES (?, ?, ?, ?, ?)', (
                photo['id'],
                user_id,
                                photo['sizes'][-1]['url'],
                photo['likes']['count'],
                photo['comments']['count']
            ))
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


if __name__ == '__main__':
    vkinder = VKinder()
    vkinder.run()
  