import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

vk_session_group = vk_api.VkApi(
    token='#групповой токен')
vk_group = vk_session_group.get_api()
longpoll_group = VkLongPoll(vk_session_group)

vk_session_personal = vk_api.VkApi(
    token='#личный токен')
vk_personal = vk_session_personal.get_api()
longpoll_personal = VkLongPoll(vk_session_personal)


def message_send(user_id, message=None, attachment=None):
    vk_session_group.method('messages.send',
                            {"user_id": user_id,
                             'message': message,
                             'random_id': get_random_id(),
                             'attachment': attachment
                             }
                            )


def get_city_id(city_name):
    city_name = vk_session_personal.method('database.getCities',
                                           {'country_id': 1, 'q': city_name, 'need_all': 0, 'count': 1})
    return city_name['items'][0]['id']


def getting_sex(text):
    if text == 'женский':
        return 1
    elif text == 'мужской':
        return 2
    else:
        print('оШибка')


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
        print('ОШибка')


def photos_get(user_id):
    photos = vk_session_personal.method('photos.get',
                                     {'album_id': 'profile',
                                      'owner_id': user_id,
                                      'extended': 1
                                      }
                                        )

    photo_map = {}
    for photo in photos['items']:
        photo_id = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])
        photo_map[photo_id] = photo['likes']['count'] + photo['comments']['count']

    sorted_photo_map = sorted(photo_map.items(), key=lambda x: -x[1])
    dict(sorted_photo_map)
    photo_map = sorted_photo_map[:3]

    return photo_map



for event in longpoll_group.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text.lower() == 'привет':
            message_send(event.user_id, 'Бодрый день')
        elif event.text.lower() == 'поиск':
            message_send(event.user_id, f"Введите возраст: ")
            for event2 in longpoll_group.listen():
                if event2.type == VkEventType.MESSAGE_NEW and event2.to_me:
                    try:
                        age = int(event2.text)
                        message_send(event.user_id, f"Введите город: ")
                        for event3 in longpoll_group.listen():
                            if event3.type == VkEventType.MESSAGE_NEW and event3.to_me:
                                city_id = get_city_id(event3.text)
                                message_send(event.user_id, f"Введите пол: ")
                                for event4 in longpoll_group.listen():
                                    if event4.type == VkEventType.MESSAGE_NEW and event4.to_me:
                                        sex_id = getting_sex(event4.text)
                                        message_send(event.user_id, f"Введите ваше семейное положение: ")
                                        for event5 in longpoll_group.listen():
                                            if event5.type == VkEventType.MESSAGE_NEW and event5.to_me:
                                                relation_id = get_relation(event5.text)
                                                profiles = vk_session_personal.method('users.search',
                                                                                      {'city_id': city_id,
                                                                                       'age_from': age,
                                                                                       'age_to': age,
                                                                                       'sex': sex_id,
                                                                                       'relation': relation_id,
                                                                                       'count': 3,
                                                                                       'offset': None
                                                                                       })
                                                profiles = profiles['items']
                                                result = []
                                                for profile in profiles:
                                                    if not profile['is_closed']:
                                                        result.append(
                                                            {'name': profile['first_name'] + ' ' + profile['last_name'],
                                                             'id': profile['id']
                                                             })
                                                print(result)
                                                for human in result:
                                                    photo_map = photos_get(human['id'])
                                                    message_send(event5.user_id, 'Имя : ' +
                                                                 human['name'], attachment=None)
                                                    message_send(event5.user_id, 'https://vk.com/id' + str(human['id']),
                                                                 attachment=None)


                                                    for key, value in photo_map:
                                                        photo = key
                                                        likes_comm = value
                                                        message_send(event5.user_id, 'Самые популярные: ' + str(likes_comm),
                                                                     attachment=photo)
                                                break
                                        break
                        break
                    except ValueError:
                        message_send(event2.user_id, 'Ошибка ввода')
                        break
        else:
            message_send(event.user_id, 'неизвестная команда')
