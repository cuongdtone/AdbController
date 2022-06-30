# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 29/06/2022


from utils.db_handler import ConnectDB


db = ConnectDB()

find_result = list(db['messages'].find({
                        'message_type': 'M',
                        'reply_status': False,
                        'reply_date' : {'$gt' : 0},
                        'phone_recipient' : {'$ne' : ''},
                        'account_id' : '0906317392'
                    }, sort=[("created_date", 1)]).limit(5))

for i in find_result:
    print(i)