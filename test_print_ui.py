# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 28/06/2022


import uiautomator2 as u2
import xml.etree.ElementTree as ET
import re


device = u2.connect('127.0.0.1:62001')
xml = device.dump_hierarchy()
print(xml)

# root = ET.ElementTree(ET.fromstring(xml))
# b2tf = root.find(f".//*[@resource-id='{'com.zing.zalo:id/menu_drawer'}']")
# temp = b2tf.attrib['bounds']
# temp = re.findall(r'\d+', temp)
# position = [int(i) for i in temp]
# device.click(position[0] + 1, position[1] + 1)






