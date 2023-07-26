import psycopg2
import sqlalchemy

import vk_api
import datetime

from config_my import comunity_token, acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)
        self.longpoll = vk_api.longpoll.VkLongPoll(self.api)

    def get_profile_info(self, user_id):
        info = self.api.method('users.get', {
            'user_ids': user_id,
            'fields': 'city,bdate,sex,relation,home_town'
        })[0]

        user_info = {
            'name': info['first_name'] + ' ' + info['last_name'],
            'id': info['id'],
            'bdate': info['bdate'] if 'bdate' in info else None,
            'home_town': info['home_town'],
            'sex': info['sex'],
            'city': info['city']['id']
        }

        empty_fields = [key for key, value in user_info.items() if value is None]
        if empty_fields:
            self.request_user_input(empty_fields, user_info)

        return user_info

    def request_user_input(self, fields, user_info):
        for field in fields:
            message = f"Введите значение для поля '{field}': "
            response = self.send_message(message)
            user_input = response['text']

            if field == 'bdate':
                if is_valid_date(user_input):
                    user_info[field] = format_date(user_input)
                else:
                    self.send_message("Некорректный формат даты. Попробуйте снова.")
                    self.request_user_input([field], user_info)
            elif field == 'city':
                city_id = get_city_id(user_input)
                if city_id:
                    user_info[field] = city_id
                else:
                    self.send_message("Город не найден. Попробуйте снова.")
                    self.request_user_input([field], user_info)
            else:
                user_info[field] = user_input

    def send_message(self, message, user_id):
        response = self.api.method('messages.send', {
            'user_id': user_id,
            'random_id': datetime.datetime.now().timestamp(),
            'message': message
        })
        return response

    def search_users(self, params):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        current_year = datetime.datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search', {
            'count': 10,
            'offset': 0,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex,
            'city': city,
            'status': 6,
            'is_closed': False
        })

        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if not user['is_closed']:
                res.append({'id': user['id'], 'name': user['first_name'] + ' ' + user['last_name']})

        return res


def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_date(date_str):
    try:
        date = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        return date.strftime("%Y-%m-%d")
    except ValueError:
        return None


def get_city_id(city_name):
    # Здесь может быть ваша логика получения идентификатора города
    return None





if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(789657038)
    users = bot.search_users(params)
    print(bot.get_photos(users[2]['id']))

    for event in bot.longpoll.listen():
        if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW and event.to_me:
            if event.text:
                message_text = event.text
                user_id = event.user_id

                # Логика обработки сообщения
                if message_text == 'Привет':
                    response_message = "Привет! Как дела?"
                elif message_text == 'Пока':
                    response_message = "Пока! Удачи!"
                else:
                    response_message = "Я не понимаю вашего сообщения."

                # Отправка ответного сообщения
                bot.send_message(response_message, user_id)

