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
from chat.chatter import Chatter, Two, One, Any, Compare, Join

chatter = Chatter()

hello = "привет", "приветики", "привет!", "ку", "привет"

only_hello = Any(hello, Compare.equals, 0)
has_hello = Any(hello, Compare.inside, 0)
has_hello_last = Any(hello, Compare.inside, 2)

chatter.add(Two(has_hello_last, has_hello, Join.everything), "ты уже здоровался!")
chatter.add(only_hello, "я приветствую тебя!")
chatter.add(has_hello, "я приветствую тебя, но я не понял остальной части предложения!")

chatter.add(One("", Compare.inside, 0), "Я не понял!", "Не понимаю!", "Что?")
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
        class Dialog:
__slots__ = ("condition", "answer")

def __init__(self, condition, *answer):
        self.condition = condition
        self.answer = answer

    def set(self, condition):
        self.condition = condition

    def check(self, chat_data):
        return self.condition.check(chat_data)


class Chatter:
    __slots__ = ("dialogs", )

    def __init__(self):
        self.dialogs = []

    def add(self, *dialog):
        if isinstance(dialog[0], Dialog):
            return self.dialogs.append(dialog)

        return self.dialogs.append(Dialog(*dialog))

    async def parse_message(self, user, chat_data):
        for dialog in self.dialogs:
            if dialog.check(chat_data):
                return choice(dialog.answer)

        return None


class ChatterBot:
    __slots__ = ("chatbot", )

    def __init__(self):
        self.chatbot = ChatBot(
            'Валера',
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            silence_performance_warning=True
        )

        self.chatbot.train("chatterbot.corpus.russian")

    async def parse_message(self, user, chat_data):
        if not user.chatter_id or not self.chatbot.conversation_sessions.get(user.chatter_id):
            user.chatter_id = self.chatbot.conversation_sessions.new().id
            await db.update(user)

        self.chatbot.conversation_sessions.get(user.chatter_id)

        return str(self.chatbot.get_response(chat_data[0], user.chatter_id))

def _get_user_name_from_vk_id(self, user_id):
    request = requests.get("https://vk.com/id"+str(user_id))
    bs = bs4.BeautifulSoup(request.text, "html.parser")
    
    user_name = self._clean_all_tag_from_str(bs.findAll("title")[0])
    
    return user_name.split()[0]


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
        @staticmethod
def _clean_all_tag_from_str(string_line):
    """
    Очистка строки stringLine от тэгов и их содержимых
    :param string_line: Очищаемая строка
    :return: очищенная строка
    """
    result = ""
    not_skip = True
    for i in list(string_line):
        if not_skip:
            if i == "<":
                not_skip = False
            else:
                result += i
        else:
            if i == ">":
                not_skip = True
    
    return result


  