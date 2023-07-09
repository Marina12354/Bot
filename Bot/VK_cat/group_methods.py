import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import date

from config import com_token
import personal_methods


vk_session_group = vk_api.VkApi(
    token=com_token)
vk_group = vk_session_group.get_api()
longpoll_group = VkLongPoll(vk_session_group)


def message_send(user_id, message=None, attachment=None):
    vk_session_group.method('messages.send',
                            {"user_id": user_id,
                             'message': message,
                             'random_id': get_random_id(),
                             'attachment': attachment
                             }
                            )


def getting_sex(text):
    if text == 'женский':
        return 1
    elif text == 'мужской':
        return 2
    else:
        print('оШибка')
        return 0


def get_relation(text):
    if text == 'холост' or text == 'не замужем' or text == 'не женат':
        return 1
    elif text == 'есть друг' or text == 'есть подруга':
        return 2
    elif text == 'помолвлен' or text == 'помолвлена':
        return 3
    elif text == 'женат' or text == 'замужем':
        return 4
    elif text == 'всё сложно' or text == 'все сложно':
        return 5
    elif text == 'в активном поиске':
        return 6
    elif text == 'влюблён' or text == 'влюблена':
        return 7
    elif text == 'в гражданском браке':
        return 8
    else:
        print('Не указано')
        return 0


def get_user_sex_id(event, user_sex_id):
    if (user_sex_id is None) or user_sex_id == 0:
        message_send(event.user_id, f"Нет поля пол. Введите пол: ")
        for event3 in longpoll_group.listen():
            if event3.type == VkEventType.MESSAGE_NEW and event3.to_me:
                user_sex_id = getting_sex(event3.text)
                if user_sex_id != 0:
                    return user_sex_id
                else:
                    message_send(event.user_id, f"Ошибка поля пол. Введите пол: ")
    else:
        return user_sex_id


def get_user_relation_id(event, user_relation_id):
    if (user_relation_id is None) or user_relation_id == 0:
        message_send(event.user_id, f"Нет поля отношения. Введите семейное положение: ")
        for event2 in longpoll_group.listen():
            if event2.type == VkEventType.MESSAGE_NEW and event2.to_me:
                user_relation_id = get_relation(event2.text)
                if user_relation_id != 0:
                    return user_relation_id
                else:
                    message_send(event.user_id, f"Ошибка поля отношения. Введите семейное положение: ")
    else:
        return user_relation_id


def get_user_city_id(event, user_city_id):
    if (user_city_id is None) or user_city_id == 0:
        message_send(event.user_id, f"Нет поля город. Введите город: ")
        for event4 in longpoll_group.listen():
            if event4.type == VkEventType.MESSAGE_NEW and event4.to_me:
                user_city_id = personal_methods.get_city_id(event4.text)
                if user_city_id != None:
                    return user_city_id
                else:
                    message_send(event.user_id, f"Ошибка поля город. Введите город: ")
    else:
        if type(user_city_id) == dict:
            return user_city_id['id']
        else:
            return user_city_id


def get_user_age(event, user_birthday):
    today = date.today()
    if (user_birthday is None) or (int(len(user_birthday.split('.'))) != 3):
        message_send(event.user_id, f"Нет года рождения. Введите возраст: ")
        for event2 in longpoll_group.listen():
            if event2.type == VkEventType.MESSAGE_NEW and event2.to_me:
                try:
                    age = int(event2.text)
                    if age <= 16:
                        message_send(event2.user_id, f"Слишком мало лет, повторите")
                    elif age >= 100:
                        message_send(event2.user_id, f"Слишком много лет, повторите")
                    else:
                        return age
                except ValueError:
                    message_send(event2.user_id, f"Ошибка ввода возраста, повторите")
    else:
        user_birthday_year = int(user_birthday.split('.')[2])
        age = today.year - user_birthday_year
        return age


def stopper(event):
    message_send(event.user_id, f"Для продолжения наберите '1', для прекращения наберите '2': ")
    for event7 in longpoll_group.listen():
        if event7.type == VkEventType.MESSAGE_NEW and event7.to_me:
            if event7.text.lower() == '2':
                return True
            elif event7.text.lower() == '1':
                break
            else:
                message_send(event7.user_id, f"Неизвестная команда")
                message_send(event7.user_id,
                                       f"Для продолжения наберите '1', для прекращения наберите '2': ")