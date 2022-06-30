# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 30/06/2022

import asyncio
import time
from threading import Thread
import inspect
import threading


class YcRTOS:

    def __init__(self):
        self.tasks = [
                      {'task_name': 'vTaskCheckNewMessageZalo', 'timeout': 5},
                      {'task_name': 'vTaskCheckNewNotificationZalo', 'timeout': 5},
                      {'task_name': 'vTaskPostZalo', 'timeout': 5},
                      ]
        self.events = {}
        self.cp_flag = {}
        self.task_timeout = {}
        for task in self.tasks:
            self.events.update({task['task_name']: False})
            self.cp_flag.update({task['task_name']: 0})
            self.task_timeout.update({task['task_name']: task['timeout']})

    def main(self):
        for task in self.tasks:
            a = getattr(YcRTOS, task['task_name'])
            Thread(target=a, args=[self]).start()

    def task_manager(self):
        time.sleep(1)
        while True:
            for task in self.tasks:
                print(task)
                self.set_one_task(task['task_name'])
                self.wait_cp_flag(task['task_name'])
                time.sleep(1)


    def set_one_task(self, event):
        for e in self.events.keys():
            self.events[e] = False
        self.events[event] = True

    def run(self):
        print('start')
        Thread(target=self.task_manager, args=[]).start()
        self.main()

    def wait_event(self, event):
        while True:
            if self.events[event]:
                self.events[event] = False
                time.sleep(0.1)
                break
            time.sleep(0.1)

    def set_cp_flag(self, event):
        self.cp_flag[event] = True
        time.sleep(0.5)
        self.cp_flag[event] = False

    def wait_cp_flag(self, event):
        timeout = 0
        while True:
            if self.cp_flag[event]:
                break
            time.sleep(0.1)
            timeout += 0.1
            if timeout >= self.task_timeout[event]:
                time.sleep(3)
                break

    def vTaskCheckNewMessageZalo(self):
        while True:
            # start task
            self.wait_event(inspect.stack()[0][3])  # key is name function
            self.set_one_task(inspect.stack()[0][3])
            for i in range(1, 4):
                self.wait_event(inspect.stack()[0][3])  # key is name function
                print(f'{inspect.stack()[0][3]} {i} Begin')
                time.sleep(1)
                print(f'{inspect.stack()[0][3]} {i} End')
                print('-'*20)
                self.set_cp_flag(inspect.stack()[0][3])
            self.set_cp_flag(inspect.stack()[0][3])

    def vTaskCheckNewNotificationZalo(self):
        while True:
            # start task
            self.wait_event(inspect.stack()[0][3])  # key is name function
            self.set_one_task(inspect.stack()[0][3])
            for i in range(1, 10):
                self.wait_event(inspect.stack()[0][3])  # key is name function
                print(f'{inspect.stack()[0][3]} {i} Begin')
                time.sleep(1)
                print(f'{inspect.stack()[0][3]} {i} End')
                print('-'*20)
                self.set_cp_flag(inspect.stack()[0][3])
            self.set_cp_flag(inspect.stack()[0][3])

    def vTaskPostZalo(self):
        while True:
            # start task
            self.wait_event(inspect.stack()[0][3])  # key is name function
            self.set_one_task(inspect.stack()[0][3])
            for i in range(1, 10):
                self.wait_event(inspect.stack()[0][3])  # key is name function
                print(f'{inspect.stack()[0][3]} {i} Begin')
                time.sleep(1)
                print(f'{inspect.stack()[0][3]} {i} End')
                print('-'*20)
                self.set_cp_flag(inspect.stack()[0][3])
            self.set_cp_flag(inspect.stack()[0][3])




YcRTOS().run()