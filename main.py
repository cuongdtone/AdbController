# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 28/06/2022

from utils.rtos import YcRTOS
from utils.emulator import get_and_check_app_u2devices


class Main:

    def __init__(self):
        self.devices = get_and_check_app_u2devices()

    def run_all_device(self):
        for device in self.devices:
            try:
                controller = YcRTOS(device)
                thread = controller.run()
            except Exception as e:
                print(e)
                print(f'Device {device.serial} cannot initial')


if __name__ == '__main__':
    Main().run_all_device()

    # vTask:
    """
    id name                      build  test
    1  chiến dịch nhắn tin       (ok)   (ok)
    2  kiểm tra tin nhắn mới     (ok)   (ok)
    3  trả lời tin nhắn          (ok)   (ok)
    4  đăng bài                  (ok)   (ok)
    5  kiểm tra thông báo        (ok)   (ok)

    YcRTOS thực hiện các tác vụ theo mức độ ưu tiên
    """