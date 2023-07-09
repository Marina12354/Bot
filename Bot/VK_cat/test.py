from vk_api.longpoll import VkEventType

import group_methods
import personal_methods
import tdatabase


tdatabase.create_table_users()

for event in group_methods.longpoll_group.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text.lower() == 'привет':
            group_methods.message_send(event.user_id, 'Добрый день')
        elif event.text.lower() == 'поиск':
            personal_methods.get_data_for_search(event)
            group_methods.message_send(event.user_id, 'Конец программы. До скорой встречи!')
            break
        elif event.text.lower() == 'выход':
            group_methods.message_send(event.user_id, 'Конец программы. Приходите снова!')
            break
        else:
            group_methods.message_send(event.user_id, 'Неизвестная команда')

tdatabase.cursor.close()
tdatabase.conn.close()