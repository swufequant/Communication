# author='lwz'
# coding:utf-8
# !/usr/bin/env python3
import unittest
from Send_msg import Receiver
from Send_msg import translate_msg
import json


class Test_Send_msg(unittest.TestCase):
    def setUp(self):
        # 测试前准备环境的搭建(setUp)
        print('setUp', self.__dict__['_testMethodName'], '\n')
        url = "http://sw.sgytec.com/wxapi/api.php?action=sendwx"
        files = ['6_1']
        users = {'gda': 'o8LXhwthhRUFzlKQxtjV1-qVoTlg',
                 '000': 'o8LXhwqQ9nq9cqdodS5utLlXVkzM',
                 'lyj': 'o8LXhwgflHajJDVY9Piu_hRkFGBo',
                 'zyb': 'o8LXhwsag78sIXWQgghdGY_3uVrU'}
        users = {'gda': 'o8LXhwthhRUFzlKQxtjV1-qVoTlg'}
        self.rev = Receiver(url=url, files=files, users=users)

    def tearDown(self):
        # 以及测试后环境的还原(tearDown)
        print('\ntearDown', self.__dict__['_testMethodName'], '\n')

    def test_send_msg(self):
        msgs = [{"code": "600057", "name": "象屿股份", "price": "8.48",
                    "time": "11:23:57", "strategy_name": "5_1"},
                {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "6_1"}]
        # self.rev.send_msg(msgs)

    def test_get_msg(self):
        msgs = [{"code": "600057", "name": "象屿股份", "price": "8.48",
                    "time": "11:23:57", "strategy_name": "5_1"},
                {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "6_1"},
                {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "6_1"},
                {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "6_1"},
                {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "6_1"}]
        self.rev.send_msg(msgs)

    def test_msg_generator(self):
        change_dict = {"keyword1": 'msg_generator'}
        b = self.rev.msg_generator(change_dict)
        ans = {'comm': {'openid': '',
                        'remark': '交易所行情数据提示， 三交易日后数据失效',
                        'first': '大单买入 中国中期 代码 000996 价格 16.60',
                        'keyword2': '15:34:01',
                        'keyword1': 'msg_generator',
                        'tourl': ''}}

        self.assertDictEqual(b, ans)
        print(b)

    def test_translate_msg(self):
        msg = "600057,象屿股份,8.48,11:23:57,5_1\n"
        true_ans = [{"code": "600057", "name": "象屿股份", "price": "8.48",
                    "time": "11:23:57", "strategy_name": "5_1"}]
        ans = translate_msg(msg)
        self.assertEqual(ans, true_ans)

    def test_translate_msgs(self):
        msg = "600057,象屿股份,8.48,11:23:57,5_1\n"\
              "000971,高升控股,15.6,14:33:45,4_1\n"
        true_ans = [{"code": "600057", "name": "象屿股份", "price": "8.48",
                    "time": "11:23:57", "strategy_name": "5_1"},
                    {"code": "000971", "name": "高升控股", "price": "15.6",
                    "time": "14:33:45", "strategy_name": "4_1"}]
        ans = translate_msg(msg)
        print(ans)
        self.assertEqual(ans, true_ans)


if __name__ == '__main__':
    unittest.main()
