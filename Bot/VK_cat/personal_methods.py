import vk_api
from vk_api import ApiError
from vk_api.longpoll import VkLongPoll, VkEventType

import group_methods
import tdatabase
from config import access_token

vk_session_personal = vk_api.VkApi(
    token=access_token)
vk_personal = vk_session_personal.get_api()
longpoll_personal = VkLongPoll(vk_session_personal)


class User_info():
    def __init__(self):
        self.bdate = None
        self.sex = None
        self.relation = None
        self.city = None
        self.first_name = ""
        self.last_name = ""

        self.user_id = 0
        self.user_age = 0
        self.user_sex_id = 0
        self.user_relation_id = 0
        self.user_city_id = 0

    def get_profile_info(self, event_name, user_id):
        info, = vk_session_personal.method('users.get',
                                           {"user_id": user_id,
                                            'fields': 'bdate, sex, relation, city'
                                            })
        self.bdate = info['bdate'] if 'bdate' in info else None
        self.sex = info['sex'] if 'sex' in info else None
        self.relation = info['relation'] if 'relation' in info else None
        self.city = info['city'] if 'city' in info else None
        self.first_name = info['first_name'] if 'first_name' in info else ""
        self.last_name = info['last_name'] if 'last_name' in info else ""

        self.user_id = user_id
        self.user_age = group_methods.get_user_age(event_name, self.bdate)
        self.user_sex_id = group_methods.get_user_sex_id(event_name, self.sex)
        self.user_relation_id = group_methods.get_user_relation_id(event_name, self.relation)
        self.user_city_id = group_methods.get_user_city_id(event_name, self.city)


class Profiles_info():
    profiles_data = []
    max_users_count = 5
    offset = 0

    def show_profile_photo(self, human, event):
        photo_map = self.photos_get(human['id'])
        group_methods.message_send(event.user_id, 'Имя : ' +
                                   human['name'], attachment=None)
        group_methods.message_send(event.user_id, 'https://vk.com/id' + str(human['id']),
                                   attachment=None)

        for key, value in photo_map:
            photo = key
            likes_comm = value
            group_methods.message_send(event.user_id,
                                       'Самые популярные: ' + str(likes_comm),
                                       attachment=photo)

    def start(self, user_info, event):
        self.search_profiles(user_info)
        while self.profiles_data:
            profile = self.profiles_data.pop()
            #          Пропускаем анкету
            if self.check_user(int(user_info.user_id), int(profile['id'])):
                print("Есть уже такая анкета")
            #          Новую анкету вносим и показываем
            else:
                tdatabase.insert_data(user_info.user_id, profile['id'])
                self.show_profile_photo(profile, event)
                #              Выходим, если вернулось True на согласие для выхода
                if group_methods.stopper(event):
                    return
            #          Ищем следующую партию
            if not (self.profiles_data):
                self.offset += self.max_users_count
                self.search_profiles(user_info)

    def photos_get(self, user_id):
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

    def search_profiles(self, user_info):
        try:
            users = vk_session_personal.method('users.search',
                                               {'city_id': user_info.user_city_id,
                                                'age_from': user_info.user_age - 3,
                                                'age_to': user_info.user_age + 3,
                                                'sex': 2 if user_info.user_sex_id == 1 else 1,
                                                'relation': user_info.user_relation_id,
                                                'count': self.max_users_count,
                                                'offset': self.offset,
                                                'has_photo': True,
                                                })
        except ApiError as err:
            users = []
            print(f'error = {err}')

        self.profiles_data = [{'name': item['first_name'] + ' ' + item['last_name'],
                               'id': item['id']
                               } for item in users['items'] if item['is_closed'] is False
                              ]

        return self.profiles_data

    def check_user(self, user_owner_id, user_finded_id):
        finded_persons = tdatabase.find_data(user_owner_id)
        for person in finded_persons:
            if int(person) == int(user_finded_id):
                return True
        return False


def get_profile_info_id(search_user_name):
    profiles = vk_session_personal.method('users.search', {'q': search_user_name})
    return profiles['items'][0]['id']


def get_city_id(city_name):
    city_name = vk_session_personal.method('database.getCities',
                                           {'country_id': 1, 'q': city_name, 'need_all': 0, 'count': 1})
    if city_name['count'] == 0:
        return None
    else:
        return city_name['items'][0]['id']


def get_data_for_search(event):
    group_methods.message_send(event.user_id, f"Введите имя пользователя или его ID: ")
    for event_name in group_methods.longpoll_group.listen():
        if event_name.type == VkEventType.MESSAGE_NEW and event_name.to_me:
            try:
                search_user_id = int(event_name.text)
            except ValueError:
                search_user_name = event_name.text
                search_user_id = get_profile_info_id(search_user_name)

            user_info = User_info()
            user_info.get_profile_info(event_name, search_user_id)

            profiles_info = Profiles_info()
            profiles_info.start(user_info, event_name)

            return
