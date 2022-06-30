# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 28/06/2022

""" Multi task in one thread """

import asyncio
import time
from datetime import datetime
from threading import Thread
import xml.etree.ElementTree as ET
from .adb_controller import AdbController
from .api_handler import download_image, upload_image_from_path


class YcRTOS(AdbController):

    def __init__(self, device, account_id=''):
        AdbController.__init__(self, device, account_id)
        self.tasks = [
                      {'task_name': 'vTaskCheckNewMessageZalo', 'time': 2},
                      {'task_name': 'vTaskCheckNewNotificationZalo', 'time': 2},
                      {'task_name': 'vTaskPostZalo', 'time': 2},
                      {'task_name': 'vTaskMessageCampaignZalo', 'time': 2},
                      {'task_name': 'vTaskReplyMessageZalo', 'time': 2},
                      ]
        self.loop = asyncio.new_event_loop()
        # create flag events
        self.events = {}
        for task in self.tasks:
            self.events.update({task['task_name']: asyncio.Event(loop=self.loop)})
        print('init complete')

    def task_manager(self):
        time.sleep(1)
        while True:
            for task in self.tasks:
                try:
                    if task['task_name'] == 'vTaskMessageCampaignZalo':
                        now_hour = datetime.now().hour
                        if now_hour > self.to_hour or now_hour < self.from_hour:
                            continue
                    self.set_one_task(task['task_name'])
                    time.sleep(task['time'])
                except Exception as e:
                    print(e)
                    pass

    async def main(self):
        tasks = []
        for task in self.tasks:
            a = getattr(YcRTOS, task['task_name'])
            task = asyncio.create_task(a(self))
            tasks.append(task)
        await asyncio.gather(*tasks)

    def set_one_task(self, event):
        for e in self.events.values():
            e.clear()
        self.events[event].set()

    def run(self):
        print('start')
        self.set_one_task(self.tasks[0]['task_name'])
        Thread(target=self.task_manager, args=[]).start()
        self.loop.run_until_complete(self.main())

    # define vTask here

    async def vTaskCheckNewMessageZalo(self):
        while True:
            await self.events['vTaskCheckNewMessageZalo'].wait()  # key is name function
            try:
                # start task
                # print('vTaskCheckNewMessageZalo: Start')
                chats = self.check_new_message()
                for chat in chats:
                    nickname = chat['nickname']
                    chat_content = chat['chat']
                    img = chat['img']

                    if len(nickname.split('~'))>1:
                        phone_number = nickname.split('~')[0].strip()
                        contact_name = nickname.split('~')[1].strip()
                    else:
                        phone_number = None
                        contact_name = nickname
                    upload_image_from_path(img, self.account_id)
                    self.db_handler.insert_new_message('M', self.account_id,
                                                       image=img,
                                                       chat_content=chat_content,
                                                       phone_number=phone_number,
                                                       contact_name=contact_name)

                # print(chats)
                time.sleep(0.5)
                # print('vTaskCheckNewMessageZalo: End')
                # print()
                # end task
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)

    async def vTaskCheckNewNotificationZalo(self):
        while True:
            await self.events['vTaskCheckNewNotificationZalo'].wait()  # key is name function
            try:
                # start task
                # print('vTaskCheckNewNotificationZalo: Start')
                ret, path = self.check_new_notifications()
                if ret:
                    upload_image_from_path(path, self.account_id)
                    self.db_handler.insert_new_message('D', self.account_id,
                                                       image=path,
                                                       chat_content=None,
                                                       phone_number=None,
                                                       contact_name=None
                                                       )

                time.sleep(0.5)
                # print('vTaskCheckNewNotificationZalo: End')
                # print()
                # end task
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)

    async def vTaskPostZalo(self):
        while True:
            await self.events['vTaskPostZalo'].wait()
            try:
                # print('vTaskPostZalo: Start')
                post_campaign = self.db_handler.get_schedule_post(self.account_id)
                for post in post_campaign:
                    content = post['content']
                    imgs = post['medias']
                    download_image(imgs)
                    ret = self.post_status(content, imgs)
                    if ret:  # update status -> db
                        accounts = post['accounts']
                        log = list(filter(lambda posted: posted['account_id'] == self.account_id,
                                          accounts))[0]
                        self.db_handler.update_status_post(post['schedule_code'], self.account_id,
                                                           log['social_networks'], True)
                        pass
                    time.sleep(0.5)
                # print('vTaskPostZalo: End')
                # print()
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)

    async def vTaskReplyMessageZalo(self):
        while True:
            await self.events['vTaskReplyMessageZalo'].wait()  # key is name function
            try:
                # start task
                # print('vTaskReplyMessageZalo: Start')
                reply_messages = self.db_handler.get_message_reply(self.account_id)
                for message in reply_messages:
                    await self.events['vTaskReplyMessageZalo'].wait()  # key is name function
                    try:
                        # print('vTaskReplyMessageZalo: Start')
                        if message['social_networks'] == 'Zalo':
                            # prepare
                            phone_number = message['phone_recipient']
                            images = message['images']
                            content = message['reply']
                            download_image(images)
                            # rep
                            self.send_message(phone_number, content, images, go_home=True)
                            # update status
                            self.db_handler.update_status_message(mess_ids=message['_id'],
                                                                  is_reply_status=True,
                                                                  is_status=False)
                        time.sleep(0.5)
                        # print('vTaskReplyMessageZalo: End')
                        # print()
                    except Exception as e:
                        # print(e)
                        pass
                    await asyncio.sleep(1)
                time.sleep(0.5)
                # print('vTaskReplyMessageZalo: End')
                # print()
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)

    async def vTaskMessageCampaignZalo(self):
        while True:
            self.from_hour = 8
            self.to_hour = 20
            await self.events['vTaskMessageCampaignZalo'].wait()  # key is name function
            try:
                # start task
                message_campaigns = self.db_handler.get_schedule_texts(self.account_id)
                for message_campaign in message_campaigns:
                    phone_numbers = message_campaign.schedule_texts['phone_numbers']
                    content = message_campaign.content
                    self.from_hour = message_campaign.schedule_texts['from_hour']
                    self.to_hour = message_campaign.schedule_texts['to_hour']
                    frequency_date = message_campaign.schedule_texts['frequency_date']
                    for phone in phone_numbers:
                        await self.events['vTaskMessageCampaignZalo'].wait()  # key is name function
                        try:
                            # print('vTaskMessageCampaignZalo: Start')
                            isFriend, status = self.add_frient(phone['phone_number'])
                            if isFriend:
                                xml = self.device.dump_hierarchy()
                                root = ET.ElementTree(ET.fromstring(xml))
                                name_des = root.find(f".//*[@resource-id='com.zing.zalo:id/action_bar_title']")
                                name_des = name_des.attrib['text']

                                # get message
                                x = int(self.displayWidth / 2)
                                self.device.swipe(x, 1124, 20, 1124, 0.05)
                                xml = self.device.dump_hierarchy()
                                root_temp = ET.ElementTree(ET.fromstring(xml))
                                name = root_temp.find(f".//*[@resource-id='com.zing.zalo:id/reply_name']")
                                self.click_icon('com.zing.zalo:id/reply_delete_button')
                                if name is not None:
                                    name = name.attrib['text']
                                    if name == name_des:
                                        # print('have new message')
                                        chat = self.get_chat()
                                        # insert chat to db
                                        nickname = chat['nickname']
                                        chat_content = chat['chat']
                                        img = chat['img']

                                        if len(nickname.split('~')) > 1:
                                            phone_number = nickname.split('~')[0].strip()
                                            contact_name = nickname.split('~')[1].strip()
                                        else:
                                            phone_number = None
                                            contact_name = nickname
                                        upload_image_from_path(img, self.account_id)
                                        self.db_handler.insert_new_message('M', self.account_id,
                                                                           image=img,
                                                                           chat_content=chat_content,
                                                                           phone_number=phone_number,
                                                                           contact_name=contact_name)
                                        # continue
                                # No new message -> check log
                                log = list(filter(lambda phone_log: phone_log['phone_number'] == phone['phone_number'],
                                                  message_campaign.message_logs))
                                log = log[-1] if len(log) > 0 else None
                                # # print(log)
                                if log is None:
                                    # sent first message
                                    text = content[0]['content']
                                    imgs = content[0]['images']
                                    download_image(imgs)
                                    content_code = content[0]['content_code']
                                    self.send_message(phone['phone_number'], text, imgs)
                                    success = True
                                    status = 'Đã gửi tin nhắn'
                                else:
                                    # sent message after log
                                    send_date = datetime.fromtimestamp(log['send_date'])
                                    if (datetime.now() - send_date).days < frequency_date:
                                        # print('Mới gửi')
                                        continue
                                    else:
                                        # # print('10 day')
                                        # # print(log['content_code'])
                                        i = next((i for i, item in enumerate(content) if
                                                  item["content_code"] == log['content_code']), None)
                                        if log['status'] == 'Failed':
                                            # print('gửi lại vì chưa thành công')
                                            content_code = content[i]['content_code']
                                            text = content[i]['content']
                                            imgs = content[i]['images']
                                            download_image(imgs)
                                            self.send_message(phone['phone_number'], text, imgs)
                                            success = True
                                            status = 'Đã gửi tin nhắn'
                                        elif i + 1 < len(content) and log['status'] == 'Successfully':
                                            # gửi tiếp content tiếp theo
                                            content_code = content[i + 1]['content_code']
                                            text = content[i + 1]['content']
                                            imgs = content[i + 1]['images']
                                            download_image(imgs)
                                            self.send_message(phone['phone_number'], text, imgs)
                                            success = True
                                            status = 'Đã gửi tin nhắn'
                                        else:
                                            # hết chiến dịch với phone này
                                            continue
                                # print(phone['phone_number'], content_code, success, status)
                                self.db_handler.update_message_log(message_campaign.schedule_code,
                                                                   content_code,
                                                                   self.account_id,
                                                                   phone['phone_number'],
                                                                   success,
                                                                   status
                                                                   )


                                pass
                            # print('vTaskMessageCampaignZalo: End')
                            # print()
                        except Exception as e:
                            # print(e)
                            pass
                        await asyncio.sleep(1)
                    time.sleep(0.5)
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)
