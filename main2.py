
# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 28/06/2022

from utils.ycrtos import YcRTOS
from utils.emulator import get_and_check_app_u2devices
from threading import Thread


class Main:

    def __init__(self):
        self.devices = get_and_check_app_u2devices()
        print(self.devices)

    def run_all_device(self):
        for device in self.devices:
            try:
                controller = YcRTOS(device)
                thread = controller.run()
                Thread(target=thread, args=[]).start()
            except Exception as e:
                print(e)
                print(f'Device {device.serial} cannot initial')
            print('h')


if __name__ == '__main__':
    Main().run_all_device()

    # vTask:
    """
    1 chiến dịch nhắn tin       (ok) 
    2 kiểm tra tin nhắn mới     (ok) (ok)
    3 trả lời tin nhắn          (ok) (ok)
    4 đăng bài                  (ok) (ok)
    5 kiểm tra thông báo        (ok) (ok)

    YcRTOS thực hiện các tác vụ theo mức độ ưu tiên
    """



