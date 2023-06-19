import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import personal_methods

vk_session_group = vk_api.VkApi(
    token='#групповой токен')
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


def get_user_sex_id(user_id, event):
    user_sex_id = personal_methods.get_profile_info_sex(user_id)
    if (user_sex_id == "none") or user_sex_id == 0:
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


def get_user_relation_id(user_id, event):
    user_relation_id = personal_methods.get_profile_info_relation(user_id)
    if (user_relation_id == "none") or user_relation_id == 0:
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


