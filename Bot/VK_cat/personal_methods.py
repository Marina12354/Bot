from datetime import date

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import group_methods
import tdatabase


vk_session_personal = vk_api.VkApi(
    token='#личный токен')
vk_personal = vk_session_personal.get_api()
longpoll_personal = VkLongPoll(vk_session_personal)


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


def get_profile_info_bdate(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'bdate'
                                       })
    if 'bdate' in info[0]:
        return info[0]['bdate']
    else:
        return "none"


def get_profile_info_sex(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'sex'
                                       }
                                      )
    if 'sex' in info[0]:
        return info[0]['sex']
    else:
        return "none"


def get_profile_info_relation(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'relation'
                                       }
                                      )
    if 'relation' in info[0]:
        return info[0]['relation']
    else:
        return "none"


def get_profile_info_first_name(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'first_name'
                                       }
                                      )
    if 'first_name' in info[0]:
        return info[0]['first_name']
    else:
        return ""


def get_profile_info_last_name(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'last_name'
                                       }
                                      )
    if 'last_name' in info[0]:
        return info[0]['last_name']
    else:
        return ""


def get_user_age(user_id, event):
    today = date.today()
    user_birthday = get_profile_info_bdate(user_id)
    if (user_birthday == "none") or (int(len(user_birthday.split('.'))) != 3):
        group_methods.message_send(event.user_id, f"Нет года рождения. Введите возраст: ")
        for event2 in group_methods.longpoll_group.listen():
            if event2.type == VkEventType.MESSAGE_NEW and event2.to_me:
                try:
                    age = int(event2.text)
                    if age <= 15:
                        group_methods.message_send(event2.user_id, f"Слишком мало лет, повторите")
                    elif age >= 100:
                        group_methods.message_send(event2.user_id, f"Слишком много лет, повторите")
                    else:
                        return age
                except ValueError:
                    group_methods.message_send(event2.user_id, f"Ошибка ввода возраста, повторите")
    else:
        user_birthday_year = int(user_birthday.split('.')[2])
        age = today.year - user_birthday_year
        return age


def get_profile_info_id(search_user_name):
    profiles = vk_session_personal.method('users.search', {'q': search_user_name})
    return profiles['items'][0]['id']


def get_city_id(city_name):
    city_name = vk_session_personal.method('database.getCities',
                                           {'country_id': 1, 'q': city_name, 'need_all': 0, 'count': 1})
    if city_name['count'] == 0:
        return "none"
    else:
        return city_name['items'][0]['id']


def get_profile_info_city(user_id):
    info = vk_session_personal.method('users.get',
                                      {"user_id": user_id,
                                       'fields': 'city'
                                       }
                                      )
    if 'city' in info[0]:
        return info[0]['city']
    else:
        return "none"


def get_user_city_id(user_id, event):
    user_city_id = get_profile_info_city(user_id)
    if (user_city_id == "none") or user_city_id == 0:
        group_methods.message_send(event.user_id, f"Нет поля город. Введите город: ")
        for event4 in group_methods.longpoll_group.listen():
            if event4.type == VkEventType.MESSAGE_NEW and event4.to_me:
                user_city_id = get_city_id(event4.text)
                if user_city_id != "none":
                    return user_city_id
                else:
                    group_methods.message_send(event.user_id, f"Ошибка поля город. Введите город: ")
    else:
        return user_city_id


def search_profiles(city_id, age, sex_id, relation_id, event5):
    if sex_id == 1:
        sex_id = 2
    else:
        sex_id = 1

    profiles = vk_session_personal.method('users.search',
                                          {'city_id': city_id,
                                           'age_from': age,
                                           'age_to': age,
                                           'sex': sex_id,
                                           'relation': relation_id,
                                           'count': 10,
                                           'offset': None
                                           })
    profiles = profiles['items']
    for profile in profiles:
        if not profile['is_closed']:
            tdatabase.insert_data(profile['id'])

    tdatabase.cursor.execute("SELECT * FROM users")
    result = []
    for person in tdatabase.cursor.fetchall():
        first_name = get_profile_info_first_name(person[1])
        last_name = get_profile_info_last_name(person[1])
        result.append(
            {'name': first_name + ' ' + last_name,
             'id': person[1]
             })

    for human in result:
        photo_map = photos_get(human['id'])
        group_methods.message_send(event5.user_id, 'Имя : ' +
                              human['name'], attachment=None)
        group_methods.message_send(event5.user_id, 'https://vk.com/id' + str(human['id']),
                              attachment=None)

        for key, value in photo_map:
            photo = key
            likes_comm = value
            group_methods.message_send(event5.user_id,
                                  'Самые популярные: ' + str(likes_comm),
                                  attachment=photo)

        group_methods.message_send(event5.user_id, f"Для продолжения наберите '1', для прекращения наберите '2': ")
        for event7 in group_methods.longpoll_group.listen():
            if event7.type == VkEventType.MESSAGE_NEW and event7.to_me:
                if event7.text.lower() == '2':
                    return
                elif event7.text.lower() == '1':
                    break
                else:
                    group_methods.message_send(event7.user_id, f"Неизвестная команда")
                    group_methods.message_send(event7.user_id,
                                          f"Для продолжения наберите '1', для прекращения наберите '2': ")


def get_data_for_search(event):
    group_methods.message_send(event.user_id, f"Введите имя пользователя или его ID: ")
    for event_name in group_methods.longpoll_group.listen():
        if event_name.type == VkEventType.MESSAGE_NEW and event_name.to_me:
            try:
                search_user_id = int(event_name.text)
            except ValueError:
                search_user_name = event_name.text
                search_user_id = get_profile_info_id(search_user_name)

            user_age = get_user_age(search_user_id, event_name)
            user_sex_id = group_methods.get_user_sex_id(search_user_id, event_name)
            user_relation_id = group_methods.get_user_relation_id(search_user_id, event_name)
            user_city_id = get_user_city_id(search_user_id, event_name)

            search_profiles(user_city_id, user_age, user_sex_id, user_relation_id, event_name)

            return


tdatabase.drop_data()
tdatabase.create_table_users()
