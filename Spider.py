# -*- coding:utf-8 -*-
import binascii
import hashlib
import json
import re
import time
import copy
import requests
from Crypto.Cipher import AES



class Spider:
    def __init__(self, req_params):
        req_params = self.empty_string(req_params)
        self.req_params = req_params
        self.username = req_params['username']
        self.password = self.aes_decrypt(req_params['password'])
        self.ka_name = req_params['ka_name']
        self.doc = req_params['doc']
        self.sold_to_party = req_params['sold_to_party']
        self.cookie = ''
        self.result = {'login': 1,
                       'style': req_params.get('style', 'default'),
                       'track_id': req_params.get('track_id', 'default'),
                       'info': {'total_num': -1,
                                'total_min': -1,
                                'total_max': -1,
                                'lose_min': 0,
                                'lose_max': 0,
                                'ditto': 0,
                                'crawling_num': 0,
                                'succeed': 0,
                                'failed': 0},
                       'errors': [],
                       'form': []}

    # 登录
    def login(self):
        pass

    # 订货单
    def get_order_header(self):
        pass

    def get_order_line(self):
        pass

    def analyze_order_header(self, order_header):
        pass


    def analyze_order_line(self, order_line):
        pass

    def crawling_order(self):
        pass




    def crawling(self):
        crawler = {'订货单': self.crawling_order,
                   }
        crawler[self.doc]()

    def get_smscode(self, smsdata):
        status = 0
        sms_code = ''
        head_req = dict()
        head_req['Content-Type'] = 'application/json'

        req = requests.post('http://{}/kms/SmsCodeController/requestSmsCode'.format(str(self.req_params['kms_ip'])),
                            data=json.dumps(smsdata),
                            headers=head_req)
        req_json = req.json()
        if req_json['code'] == 'SUCCESS':
            time.sleep(int(smsdata["expire"]) * 60 - 10)
            req2 = requests.post(
                'http://{}/kms/SmsCodeController/getSmsCode'.format(str(self.req_params['kms_ip'])),
                data=json.dumps(smsdata),
                headers=head_req)
            req2_json = req2.json()
            if req2_json['code'] == 'SUCCESS':
                smsCode = req2_json['data']['smsCode']
                if smsCode:
                    status = 1
                    sms_code = smsCode
        sms_json = {
            'status': status,
            'smscode': sms_code
        }
        return sms_json


    @staticmethod
    def get_md5(result_order):
        m1 = hashlib.md5()
        result_data = result_order['data']
        result_head = result_order['head']
        details_str = ['未交货订单明细', '商品详情', '门店、单品汇总', '商品目录']
        dict_new = dict()
        for detail_str in details_str:
            if detail_str in result_data.keys():
                details = result_data[detail_str]
                dict_new[detail_str] = result_data[detail_str]
                for detail in details:
                    list_detail = list(detail.values())
                    list_detail.sort()
                    list_detail = str(list_detail).encode('utf-8')
                    m1.update(list_detail)
        for i in dict_new.keys():
            result_data.pop(i)
        list_data = list(result_data.values())
        list_data.sort()
        list_data = str(list_data).encode('utf-8')
        list_head = list(result_head.values())
        list_head.sort()
        list_head = str(list_head).encode('utf-8')
        m1.update(list_data)
        m1.update(list_head)
        order_md5 = m1.hexdigest()
        for key, val in dict_new.items():
            result_data[key] = val
        return order_md5

    @staticmethod
    def get_other_md5(result_order):
        def recursive(data):
            if type(data)==type(list()) :
                for i in range(0,len(data)): 
                    data[i]=recursive(data[i])
                    data[i]=str(data[i])
                data.sort()
                return data
            elif type(data)==type(dict()):
                
                data_list=list()
                for d in data: 
                    data[d]=recursive(data[d])
                    data_list.append(str(d)+':'+str(data[d]))
                data_list.sort()
                data=data_list
                return data
            else :
                return data
        result_cp=copy.deepcopy(result_order)

        result_data=recursive(result_cp)
        # print(str(result_data))
        md5=hashlib.md5()
        md5.update(str(result_data).encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def empty_string(req_params):
        res = copy.deepcopy(req_params)
        if 'kmsTransorderType' in req_params.keys():
            for k, v in req_params.items():
                if k == 'kmsTransorderType':
                    res[k.replace('kmsTrans', '')] = v
        if 'kmsTransstartTime' in req_params.keys():
            for k, v in req_params.items():
                if k == 'kmsTransstartTime':
                    res[k.replace('kmsTrans', '')] = v
        if 'kmsTransendTime' in req_params.keys():
            for k, v in req_params.items():
                if k == 'kmsTransendTime':
                    res[k.replace('kmsTrans', '')] = v
        if 'kmsTransid' in req_params.keys():
            for k, v in req_params.items():
                if k == 'kmsTransid':
                    res[k.replace('kmsTrans', '')] = v
        if 'kms-all/0-1' in res.values():
            for k, v in res.items():
                if v == 'kms-all/0-1':
                    res[k] = ''
        return res

    @staticmethod
    def get_content_length(data):
        if type(data) == dict:
            length = len(data.keys()) * 2 - 1
            total = ''.join(list(data.keys()) + list(data.values()))
            length += len(total)
            length = max(length, 0)
        elif type(data) == bytes:
            length = len(data)
        else:
            raise TypeError("expected 'dict' or 'str',got '{}'".format(type(data).__name__))
        return str(length)

    @staticmethod
    def aes_decrypt(password):
        try:
            key = 'v3DRk/QisHTNZWwp'.encode('utf-8')
            iv = key
            mode = AES.MODE_CBC
            cryptos = AES.new(key, mode, iv)
            password_str = password.encode('utf-8')
            plain_text = cryptos.decrypt(binascii.a2b_hex(password_str))
            des_password = bytes.decode(plain_text)
            des_password = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', des_password)
        except ValueError:
            des_password = password
        return des_password

    @staticmethod
    def img_bytes2array(img_bytes):
        # 调用验证码接口时改函数注释掉
        # from io import BytesIO
        # from PIL import Image
        # import cv2
        # import numpy as np
        # f = BytesIO()
        # f.write(img_bytes)
        # img_pil = Image.open(f)
        # img_arr = np.asarray(img_pil)
        # if len(img_arr.shape) > 2:
        #     img_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
        # return img_arr
        return img_bytes

    def write_result(self):
        pass

    def proxy_pool(self, method='http'):
        ip_res = ''
        proxy_dict = {
            'http': ['106.35.174.19:4345', '122.6.200.191:4310', '60.173.24.223:4376', '114.99.1.65:4331',
                     '49.70.107.218:4345', '175.174.184.184:4367', '49.69.201.92:4332', '110.230.215.123:4320',
                     '183.165.27.233:4345', '49.70.64.15:4345']
        }
        headers_s = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        for ip_port in proxy_dict[method]:
            proxies = {"http": "http://" + ip_port, "https": "https://" + ip_port}
            try:
                if method == 'http':
                    request = requests.get('http://www.baidu.com/', headers=headers_s, proxies=proxies)
                else:
                    request = requests.get('https://www.baidu.com/', headers=headers_s, proxies=proxies)
            except:
                continue
            if request.status_code == 200:
                ip_res = ip_port
                break
        return ip_res
