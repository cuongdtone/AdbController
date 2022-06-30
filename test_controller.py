# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 29/06/2022


import uiautomator2 as u2
from utils.adb_controller import AdbController
import xml.etree.ElementTree as ET
import re


device = u2.connect('127.0.0.1:62001')

device = AdbController(device, init_acc=False)

device.post_status('aaa', images=['1c8f45d2b3a14c0f8f3928cd47592a41.jpg', '2a03bf645cbd44709ff458842eca5863.jpg'])
