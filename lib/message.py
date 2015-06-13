#coding: utf-8 

class Message(object):
    def __init__(self,text,level):
        self.text = text
        self.level = level

Messages = {'basket_product_present':   Message('Уже в корзине либо в покупках.', 'warning'),
            'basket_product_added':     Message('Товар успешно добавлен в корзину.', 'success'),
            'basket_product_deleted':   Message('Товар был удален.', 'success'),
            'basket_file_unavailable':  Message('Файл временно недоступен либо был удален по истечению времени.', 'error'),

            'cabinet_document_saved' :  Message('Сохранение успешно выполнено.', 'success'),
            'cabinet_document_deleted' :Message('Обьект был удален.', 'success'),
            'cabinet_section_deleted' : Message('Раздел был удален.', 'success'),
            'cabinet_section_added' :   Message('Раздел добавлен.', 'success'),
            'cabinet_section_not_added':Message('Раздел не добавлен.', 'error'),
            'cabinet_section_saved' :   Message('Раздел был переименован.', 'success'),
            'cabinet_section_not_empty':Message('Невозможно удалить, т.к раздел не пустой.', 'error'),
            'cabinet_large_file':       Message('Размер файла превышает допустимое значение.','error'),

            'account_profile_saved' :   Message('Сохранение успешно выполнено.','success'),
            'account_profile_not_saved' :   Message('При сохранении произошла ошибка.','error'),
            'account_large_file' :      Message('Размер файла превышает допустимое значение.','error'),
            'account_password_changed' :Message('Пароль был успешно изменен.','success'),
            'account_email_sended'  :   Message('На ваш email отправлено письмо с сылкой. Следуйте инструкциям в письме.','success'),
            'account_registration_complete': Message('Пользователь был успешно зарегистрирован. Активируйте его с помощью email.','success'),
            'account_registry_closed' : Message('Регистрация временно недоступна. Попробуйте зарегистрироваться позже.','warning'),
            'account_activate_complete':Message('Пользователь был успешно активирован. Теперь вы можете войти.','success'),

            'comment_saved':            Message('Коментарий сохранен.','success'),
}
            
def handle_messages(request):

    message = request.GET.get('message',False)
    
    if message and message in Messages: message = Messages[message]
    else: message = None

    return message



