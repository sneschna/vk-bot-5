import vk_api
from config_my import comunity_token, acces_token
from data_store import DataStore
import datetime

class BotInterface():
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.offset = 0
        self.count = 10
        self.data_store = DataStore()

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        user_city = None  # Переменная для хранения введенного города
        user_age = None  # Переменная для хранения введенного возраста
        users = None  # Переменная для хранения результатов поиска пользователей

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    if not users:
                        self.offset += self.count
                        users = self.api.search_users(self.params, self.offset - self.count, self.count)
                        if not users:
                            self.message_send(event.user_id, 'нет доступных анкет')
                    else:
                        profile = users.pop()
                        if not self.data_store.check_profile_in_database(profile):
                            self.data_store.add_profile(profile)
                            self.message_send(event.user_id, 'профиль добавлен в базу данных')

                            # Get top 3 photos for the matched user
                            photos = self.api.get_photos(profile['id'])[:3]
                            if photos:
                                photo_info = "\n".join(
                                    [f"Photo ID: {photo['id']}\nLikes: {photo['likes']}\nComments: {photo['comments']}"
                                     for photo in photos])
                                self.message_send(event.user_id,
                                                  f"Топ-3 популярных фотографии профиля:\n{photo_info}\nСсылка на профиль: https://vk.com/id{profile['id']}")
                            else:
                                self.message_send(event.user_id, 'У данного пользователя нет фотографий.')
                        else:
                            self.message_send(event.user_id, 'профиль уже просмотрен')
                elif command == 'город':
                    self.message_send(event.user_id,
                                      'Вы должны ввести город после команды "город" в формате: город <название города>. Например: город Москва')
                elif command.startswith('город '):
                    city = command.split('город ')[1]
                    user_city = city  # Сохраняем введенный город в переменной user_city
                    self.message_send(event.user_id, f'Вы ввели город: {user_city}')
                elif command.startswith('возраст '):
                    age_str = command.split('возраст ')[1]
                    if age_str.isdigit():
                        user_age = int(age_str)  # Сохраняем введенный возраст в переменную user_age
                        self.message_send(event.user_id, f'Вы ввели возраст: {user_age}')
                    else:
                        self.message_send(event.user_id,
                                          'Некорректный формат возраста. Пожалуйста, введите возраст в виде целого числа.')
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')

    def message_send(self, user_id, message):
        response = self.interface.method('messages.send', {
            'user_id': user_id,
            'random_id': random.randint(1, 2147483647),
            'message': message
        })

    def close_database(self):
        self.data_store.close_database()


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
    bot.close_database()
