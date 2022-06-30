# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 27/06/2022

import xml.etree.ElementTree as ET
import time
import re
from utils.db_handler import DBHandler
import os


class AdbController():
    def __init__(self, device, account_id='', init_acc=True):
        self.device = device
        self.account_id = account_id
        self.db_handler = DBHandler()

        self.displayHeight = self.device.info['displayHeight']
        self.displayWidth = self.device.info['displayWidth']
        self.list_position = {'Tin nhắn': [69, 1246],
                              'Nhật ký': [457, 1246],
                              'Cá nhân': [600, 1246]
                              }
        if init_acc:
            self.go_home()
            if self.account_id == '':
                self.get_account_id_zalo()
                print(self.account_id)

    def go_home(self):
        time_last = time.time()
        while True:
            if self.check_athomezalo():
                self.device.click(self.list_position['Tin nhắn'][0]+1, self.list_position['Tin nhắn'][1]+1)
                break
            if time.time() - time_last > 2:
                self.open_zalo()
                time.sleep(3)
                assert self.check_athomezalo(), 'Maybe not logged in zalo'
                break
            self.device.press('back')
            time.sleep(0.1)

    def open_zalo(self):
        self.device.press("home")
        self.device.session("com.zing.zalo")
        time.sleep(5)
        self.switch_tab('Cá nhân')
        time.sleep(1)

    def check_athomezalo(self):
        xml = self.device.dump_hierarchy()
        # print(xml)
        root = ET.ElementTree(ET.fromstring(xml))
        package = root.find(f".//*[@package='{'com.zing.zalo'}']")
        home = root.find(f".//*[@text='{'Tìm kiếm'}']")
        if package is not None and home is not None:
            return True
        else:
            return False

    def get_account_id_zalo(self):
        time.sleep(1)
        self.switch_tab('Cá nhân')
        time.sleep(1)
        self.click_button('Tài khoản và bảo mật')
        time.sleep(1)
        xml = self.device.dump_hierarchy()
        root = ET.ElementTree(ET.fromstring(xml))
        b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/tv_phone_number'}']")
        phone = b2tf.attrib['text'].split(')')[-1].strip()
        phone = '0' + phone.replace(" ", "")
        self.account_id = phone


    def click_button(self, button):
        try:
            self.device(text=button).click()
            return 1
        except:
            return 0
    def click_icon(self, icon):
        try:
            position = self.find_icon_position(icon)
            self.device.click(position[0] + 1, position[1] + 1)
            return 1
        except:
            return 0

    def switch_tab(self, tab): #tab Tin nhắn, Nhật ký
        self.device.click(self.list_position[tab][0] + 20, self.list_position[tab][1] + 10)

    def add_frient(self, phone_number):
        self.go_home()
        self.click_button(button='Tìm kiếm')
        time.sleep(0.5)
        self.device(text="Tìm kiếm").set_text(phone_number)
        time.sleep(1)
        self.device.press('enter')
        time.sleep(1)
        self.change_name_zalo(phone_number)
        have = self.find_contain_text('đã trở thành bạn bè')
        if have is not None:
            return True, 'mới đồng ý kết bạn'
        have = self.find_contain_text('Lời mời kết bạn đã được gửi đi')
        if have is not None:
            return False, 'chưa đồng ý kết bạn'
        have = self.find_contain_text('Đã gửi lời mời kết bạn')
        if have is not None:
            return False, 'chưa đồng ý kết bạn'
        have = self.find_text_position('Kết bạn')
        # print(have)
        if have is not None:
            self.click_button('Kết bạn')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/btnSendInvitation')
            time.sleep(1)
            return False, 'đã gửi lời mời'
        have = self.find_contain_text('đã đồng ý kết bạn')
        if have is not None:
            return True, 'mới đồng ý kết bạn'
        have = self.find_text_position('KẾT BẠN')
        if have is not None:
            self.click_icon('com.zing.zalo:id/btn_send_friend_request')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/btnSendInvitation')
            time.sleep(1)
            return False, 'đã gửi lời mời'
        have = self.find_contain_text('Kết bạn')
        if have is not None:
            self.click_icon('com.zing.zalo:id/tv_function_privacy')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/btnSendInvitation')
            time.sleep(1)
            return False, 'đã gửi lời mời'
        have = self.find_contain_text('Số điện thoại chưa đăng ký tài khoản')
        if have is not None:
            return False, 'không tìm thấy tài khoản'
        have = self.find_contain_text('tìm kiếm quá số lần cho phép')
        if have is not None:
            return False, 'không thể tìm kiếm'
        return True, 'đã kết bạn'

    def change_name_zalo(self, phone='0367016167'):
        try:
            time.sleep(0.5)
            xml = self.device.dump_hierarchy()
            root = ET.ElementTree(ET.fromstring(xml))
            b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/action_bar_title'}']")
            if b2tf is not None:
                name = b2tf.attrib['text']
                if len(name.split('~'))>1:
                    return True
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/menu_drawer')
            time.sleep(1)
            xml = self.device.dump_hierarchy()
            root = ET.ElementTree(ET.fromstring(xml))
            b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/action_bar_title'}']")
            if b2tf is not None:
                name = b2tf.attrib['text']
                if len(name.split('~'))>1:
                    self.click_icon('com.zing.zalo:id/icn_header_close')
                    time.sleep(1)
                    self.device.press('back')
                    return True
            time.sleep(0.5)
            position = self.find_contain_text('Đổi tên gợi nhớ')
            self.device.click(position[0][0]+10, position[0][1]+10)
            time.sleep(0.5)
            self.device(text='LƯU').wait(timeout=3.0)
            new_name = f'{phone} ~ {name}'
            self.device.clear_text()
            time.sleep(0.01)
            self.device(focused=True).set_text(new_name)
            time.sleep(0.1)
            self.device(text='LƯU').click()
            time.sleep(1)
            self.device.press('back')
            time.sleep(0.5)
            return True
        except Exception as e:
            return False
            print(e)
            print('[Khong the doi ten]')

    def send_message(self, phone, message, images=None, go_home=False):
        if go_home:
            self.go_home()
            self.click_button(button='Tìm kiếm')
            time.sleep(0.5)
            self.device(text="Tìm kiếm").set_text(phone)
            time.sleep(0.5)
            have = self.find_text_position('Liên hệ (1)')
            if have is None:
                have = self.find_contain_text('Tìm bạn qua số điện thoại')
            if have is not None:
                self.device.press('enter')
                time.sleep(0.7)

        self.device.clear_text()
        time.sleep(0.7)
        self.device(focused=True).set_text(message)
        time.sleep(0.7)
        self.click_icon('com.zing.zalo:id/reply_delete_button')
        time.sleep(0.7)
        self.click_icon('com.zing.zalo:id/new_chat_input_btn_chat_send')
        time.sleep(0.7)
        self.click_icon('com.zing.zalo:id/new_chat_input_btn_attach')
        for image in images:
            self.device(text='Tài liệu').wait(timeout=3.0)
            self.click_button('Tài liệu')
            time.sleep(0.7)
            last = time.time()
            while time.time() - last < 2:
                p = self.find_contain_text(image)
                if p is not None:
                    break
                self.device.swipe_points([(50, int(self.displayHeight / 2)), (50, 2)], 0.05)
            if p is None:
                check = self.download_img(image)
                print(check)
                if check is False:
                    print('Not Found Image')
                    self.device.press('back')
                    continue
                time.sleep(0.5)
                self.device.press('back')
                self.device(text='Tài liệu').wait(timeout=3.0)
                self.click_button('Tài liệu')
                p = self.find_contain_text(image)
            try:
                p = p[0]
                self.device.click(p[0] + 1, p[1] + 1)
                time.sleep(0.7)
                self.click_icon('com.zing.zalo:id/btn_send_multi_selected_files')
                time.sleep(0.7)
                self.click_icon('com.zing.zalo:id/button1')
            except:
                pass

    def download_img(self, img):
        try:
            self.device.push(f'src/imgs/{img}', "/sdcard/")
            return True
        except:
            return False

    def find_text_position(self, text='Zalo'):
        xml = self.device.dump_hierarchy()
        # print(xml)
        root = ET.ElementTree(ET.fromstring(xml))
        b2tf = root.find(f".//*[@text='{text}']")
        if b2tf is None:
            return None
        try:
            temp = b2tf.attrib['bounds']
            temp = re.findall(r'\d+', temp)
            return [int(i) for i in temp]
        except:
            return None

    def find_icon_position(self, text='com.zing.zalo:id/menu_drawer'):
        xml = self.device.dump_hierarchy()
        # print(xml)
        root = ET.ElementTree(ET.fromstring(xml))
        b2tf = root.find(f".//*[@resource-id='{text}']")
        if b2tf is None:
            return None
        try:
            temp = b2tf.attrib['bounds']
            temp = re.findall(r'\d+', temp)
            return [int(i) for i in temp]
        except:
            return None

    def find_contain_text(self, text):
        xml = self.device.dump_hierarchy()
        root = ET.ElementTree(ET.fromstring(xml))
        list_p = []
        for i in root.iter():
            node = i.attrib
            if 'text' in node.keys():
                text_node = node['text']
                if text_node.count(text):
                    position = node['bounds']
                    position = re.findall(r'\d+', position)
                    list_p.append([int(i) for i in position])
        return None if list_p==[] else list_p

    def check_new_message(self):
        self.go_home()
        self.device(scrollable=True).scroll.vert.toBeginning(steps=10, max_swipes=10)
        time.sleep(0.1)
        list_new_chat = []
        while True:
            xml = self.device.dump_hierarchy()
            root = ET.ElementTree(ET.fromstring(xml))
            b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/numnotification'}']")
            if b2tf is not None:
                if not b2tf.attrib['text'][0].isdigit():
                    break
            else:
                break
            for i in root.iter():
                node = i.attrib
                if 'text' in node.keys():
                    try:
                        text_node = node['text']
                        if len(text_node.split('\n')) >= 5: #todo: set 5 to check new message
                            position = node['bounds']
                            position = re.findall(r'\d+', position)
                            position = [int(i) for i in position]
                            self.device.click(position[0]+1, position[1]+1)
                            time.sleep(0.1)
                            # chat list:
                            chat = self.get_chat()
                            self.device.press('back')
                            list_new_chat.append(chat)
                            time.sleep(0.3)
                            while True:
                                if self.find_text_position('Tìm kiếm') is not None:
                                    break
                                self.device.press('back')
                    except Exception as e:
                        print(e)
                        self.device.press('back')
                        pass
            xml = self.device.dump_hierarchy()
            root = ET.ElementTree(ET.fromstring(xml))
            b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/numnotification'}']")
            if b2tf is not None:
                if not b2tf.attrib['text'][0].isdigit():
                    break
            else:
                break
            time.sleep(1)
            self.go_home()
            time.sleep(0.5)
            self.device.swipe(50, int(self.displayHeight / 1.2), 50, 2, 0.05)
        return list_new_chat

    def get_chat(self):
        time.sleep(1)
        xml = self.device.dump_hierarchy()
        root = ET.ElementTree(ET.fromstring(xml))
        name_des = root.find(f".//*[@resource-id='com.zing.zalo:id/action_bar_title']")
        name_des = name_des.attrib['text']
        img = f"{self.account_id}_{int(time.time())}_message.jpg"
        self.device.screenshot(os.path.join("src/screenshots/", img))
        chatlist = root.find(f".//*[@resource-id='com.zing.zalo:id/chatlinelist']")
        chat = []
        for node in chatlist:
            # print(node.attrib)
            position = node.attrib['bounds']
            position = re.findall(r'\d+', position)
            position = [int(i) for i in position]
            x = int(self.displayWidth/2)
            self.device.swipe(x, position[1], 20, position[1], 0.05)
            xml = self.device.dump_hierarchy()
            root_temp = ET.ElementTree(ET.fromstring(xml))
            name = root_temp.find(f".//*[@resource-id='com.zing.zalo:id/reply_name']")
            try:
                name = name.attrib['text']
                if name != name_des:
                    name = 'I'
            except:
                continue
            chat.append({name: node.attrib['text'].strip('\n')})
            self.click_icon('com.zing.zalo:id/reply_delete_button')
            time.sleep(0.1)
        return {'nickname': name_des, 'chat': chat, 'img': img}

    def clear_gallery(self):
        self.device.session('com.android.gallery3d')
        time.sleep(0.5)
        self.device.press('menu')
        time.sleep(0.5)
        self.click_button('Làm mới')
        time.sleep(0.5)
        self.device.press('menu')
        time.sleep(0.5)
        self.click_button('Chọn album')
        time.sleep(0.5)
        self.click_icon('com.android.gallery3d:id/selection_menu')
        time.sleep(0.5)
        self.click_button('Chọn tất cả')
        time.sleep(0.5)
        self.click_icon('com.android.gallery3d:id/action_delete')
        time.sleep(0.5)
        self.click_icon('android:id/button1')
        time.sleep(1)

    def post_status(self, text, images):
        # prepare image
        try:
            self.clear_gallery()
            for image in images:
                ret = self.download_img(image)
                if ret is False:
                    return False # no images
                time.sleep(0.2)
            # Post
            self.go_home()
            time.sleep(2)
            self.switch_tab('Nhật ký')
            time.sleep(1)
            self.device(scrollable=True).scroll.vert.toBeginning(steps=10, max_swipes=10)
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/lv_media_store')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/etDesc')
            time.sleep(1)
            self.device(focused=True).set_text(text)
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/btn_post_attach_photo')
            time.sleep(1)
            list_photo_click = [[418, 995], [650, 995], [182, 1250], [413, 1250], [650, 1250]]
            for i in list_photo_click:
                self.device.click(i[0], i[1])
                time.sleep(0.5)
            time.sleep(0.5)
            self.click_icon('com.zing.zalo:id/landing_page_tv_select')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/landing_page_btn_done')
            time.sleep(1)
            self.click_icon('com.zing.zalo:id/menu_done')
            time.sleep(1)
            return True
        except:
            return False

    def check_new_notifications(self):
        self.go_home()
        time.sleep(0.3)
        self.switch_tab('Nhật ký')
        time.sleep(0.5)
        p = self.find_icon_position('com.zing.zalo:id/ic_newNotifyFeed')
        if p is not None:
            self.click_icon('com.zing.zalo:id/imgButtonNewNotificationList')
            time.sleep(5)
            path_save = f"{self.account_id}_{int(time.time())}_noti.jpg"
            self.device.screenshot(os.path.join("src/screenshots/", path_save))
            time.sleep(0.5)
            return True, path_save
        else:
            return False, None

    def print_ui(self):
        xml = self.device.dump_hierarchy()
        print(xml)
