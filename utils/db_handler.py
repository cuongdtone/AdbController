import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
import yaml
from .functions import DataItem
import os

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
if rootDir not in sys.path:  # add parent dir to paths
    sys.path.append(rootDir)

config = yaml.load(open("src/config.yaml", 'r', encoding='utf-8'), Loader=yaml.FullLoader)
MONGO_URI = config['MONGO_URI']
MONGO_DB = config['MONGO_DB']

def ConnectDB():
    client = MongoClient()  # MONGO_URI)
    db = client[MONGO_DB]
    return db


class DBHandler:
    def __init__(self):
        self.db = ConnectDB()
        # print(self.db.list_collection_names())

    def get_content(self, contents_code):
        collection = self.db['contents']
        find_results = []
        for content in contents_code:
            find_result = list(collection.find(
                {
                    'content_code': content,
                }
            ))
            find_results.append(find_result[0])
        return find_results


    def get_shedules_message(self, account_id):
        collection = self.db['schedule_texts']
        find_result = list(collection.find(
            {
                "$and": [
                    {'active': True},
                    {'from_date': {'$lte': datetime.now().timestamp()}},
                    {'to_date': {'$gte': datetime.now().timestamp()}},
                    {'from_hour': {'$lte': datetime.now().hour}},
                    {'to_hour': {'$gt': datetime.now().hour}},
                    {"accounts.account_id": account_id}
                ]
            }
        ))
        return find_result
    
    def get_message_logs(self, schedule_code, account_id):
        collection = self.db['message_logs']
        find_result = list(collection.find(
            {
                "$and": [
                    {"schedule_code": schedule_code},
                    {"account_id": account_id},
                ]
            }
        ))
        return find_result

    def get_schedule_texts(self, account_id):
        message_campaigns = self.get_shedules_message(account_id)
        results = []
        for message_campaign in message_campaigns:
            schedule_code = message_campaign['schedule_code']
            frequency_date = message_campaign['frequency_date']
            message_log = self.get_message_logs(schedule_code, account_id)
            contents_code = message_campaign['contents']
            contents_code = [i['content_code'] for i in contents_code]
            content = self.get_content(contents_code)
            data = DataItem({'schedule_code': schedule_code,
                             'schedule_texts': message_campaign,
                             'message_logs': message_log,
                             'content': content})
            results.append(data)
        return results

    def update_message_log(self, schedule_code: str, content_code: str, account_id: str, phone_number: str,
                           isSucc: bool, mess: str):
        '''
        Lưu thông tin message_logs
        '''
        status = 'Failed'
        if isSucc:
            status = 'Successfully'
        if mess == '':
            mess = 'Đã gửi tin nhắn'
        collection = self.db['message_logs']
        collection.insert_one({
            'schedule_code': schedule_code,
            'content_code': content_code,
            'account_id': account_id,
            'send_date': int(datetime.now().timestamp()),
            'phone_number': phone_number,
            'status': status,
            'message': mess
        })
        print(datetime.now(), schedule_code, content_code, account_id, phone_number, status, mess)

    def get_schedule_post(self, account_id, social_networks="Zalo"):
        collection = self.db['schedule_post']
        find_result = list(collection.find(
            {
                "$and": [
                    {'active': True},
                    {'post_date': {'$lt': datetime.now().timestamp()}},
                    {"accounts": {
                        "account_id": account_id,
                        "is_posted": "N",
                        "social_networks": social_networks
                    }}
                ]
            }
        ))
        return find_result

    def update_status_post(self, schedule_code: str, account_id: str, social_networks: str, isSucc: bool=True):
        stt = 'N'
        if isSucc:
            stt = 'S'
        collection = self.db['schedule_post']
        collection.update_one({
            'schedule_code': schedule_code,
            'active': True,
            'accounts': {
                "account_id": account_id,
                "is_posted": 'N',
                'social_networks': social_networks
            },
        }, {
            '$set': {
                'accounts.$.is_posted': stt
            }
        }, upsert=False)

    def insert_new_message(self, message_type: str,
                           account_id: str, image: str,
                           chat_content: list, phone_number: str =None,
                           contact_name: str = None):
        '''
        Args:
            message_type: M - tin nhắn; D: Nhật ký
        '''
        try:
            customer = list(self.db["accounts"].find({
                "account_id": account_id
            }, projection={"customer": 1, "branch": 1}).limit(1))[0]
            if message_type == "D":
                contact_name = "Thông báo nhật ký"

            self.db['messages'].insert_one({
                "message_type": message_type,
                "social_networks": "Zalo",
                "account_id": account_id,
                "customer_code": customer["customer"],
                "image": image,
                "chat_content": chat_content,
                "phone_recipient": phone_number,
                "recipient": contact_name,
                "images": [],
                "created_date": int(datetime.now().timestamp()),
                "created_by": "systems",
                "status": "N",
                "reply_status": False,
                "branch": customer["branch"]
            })
        except Exception as exc:
            _,_, exc_tb = sys.exc_info()
            print("ERROR handler->insert_new_message: %s - Line: %d" % (exc, exc_tb.tb_lineno))

    def get_message_reply(self, account_id):
        '''
        Lấy danh sách tin nhắn trả lời -> Gửi cho khách hàng
        reply_status = N and reply_date > 0 and phone_recipient != ""
        '''
        find_result = list(self.db['messages'].find({
            'message_type': 'M',
            'reply_status': False,
            'reply_date': {'$gt': 0},
            'phone_recipient': {'$ne': ''},
            'account_id': account_id
        }, sort=[("created_date", 1)]).limit(5))
        return find_result

    def update_status_message(self, mess_ids, is_status: bool = True, is_reply_status: bool = False):
        '''
        Cập nhật trạng thái Đã gửi thông báo cho tin nhắn đến (status=S)
        Args:
            mess_ids: list mongo id
        '''
        if is_status:
            # cập nhật trạng thái đã gửi thông báo tới quản lý
            self.db['messages'].update_many({
                '_id': {'$in': mess_ids}
            }, {
                '$set': {
                    'status': 'S'
                }
            })

        elif is_reply_status:
            # cập nhật trạng thái đã trả lời tin nhắn cho khách
            self.db['messages'].update_many({
                '_id': mess_ids
            }, {
                '$set': {
                    'reply_status': True
                }
            })

