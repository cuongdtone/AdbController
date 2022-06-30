# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 28/06/2022

from ppadb.client import Client as AdbClient
import uiautomator2 as u2

def get_devices(host="127.0.0.1", port=5037):
    client = AdbClient(host=host, port=port)
    list_serial = []
    for device in client.devices():
        list_serial.append(device.serial)
    return list_serial

def get_and_check_app_u2devices(host="127.0.0.1", port=5037, app='src/Zalo.apk'):
    client = AdbClient(host=host, port=port)
    devices = []
    for device in client.devices():
        device = u2.connect(device.serial)
        devices.append(device)
        if 'com.zing.zalo' not in device.app_list():
            print('Installing ...')
            device.app_install(app)
    return devices











