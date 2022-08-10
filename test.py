# -*- coding:utf-8 -*-

import datetime
import os
import time
from urllib import parse
import re
import requests
import json
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from decorators import *
import Spider
import yzm_api


class QuanshibianliSpider(Spider):
    def __init__(self, req_params):
        super().__init__(req_params)
        self.source_cookies = {}
        self.ka_url = 'https://vss.hd123.com/#/login'
        self.delay = 1
        self.page_size = 20
        self.path = r'toexcel.pdf'

    def login(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        with webdriver.Chrome(options=option) as driver:
            try_num = 0
            driver.get(self.ka_url)
            driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[1]/div[2]/form/div[1]/div/div/input').send_keys(
                self.username)
            driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[1]/div[2]/form/div[2]/div/div/input').send_keys(
                self.password)
            driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[2]/form/button').click()
            time.sleep(3)
            if '请输入用户代码' in driver.page_source:
                self.result['login'] = 0
                self.result['errors'].append('用户名或密码无效')
                raise LoginError
            for fuuu in range(25):
                url = driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div[1]/div[2]/div[4]/div[1]/img').get_attribute('src')
                # 字符验证码识别
                cookies = driver.get_cookies()
                self.cookie = ''
                for i in range(len(cookies)):
                    self.cookie += cookies[i]['name'] + '=' + cookies[i]['value']
                    if i != len(cookies) - 1:
                        self.cookie += '; '
                headers = {
                    'authority': 'vss.hd123.com',
                    'pragma': 'no-cache',
                    'cache-control': 'no-cache',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
                    'sec-fetch-dest': 'image',
                    'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'no-cors',
                    'referer': 'https://vss.hd123.com/',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'cookie': ''
                }
                req = requests.get(timeout=200, url=url, headers=headers, verify=False)
                time.sleep(0.3)
                try:
                    yzm_val = yzm_api.yzm(req.content, '全时')
                except Exception:
                    self.result['login'] = 0
                    self.result['errors'].append('验证码接口请求失败')
                    raise LoginError
                else:
                    if type(yzm_val) is dict:
                        self.result['login'] = 0
                        self.result['errors'].append('验证码识别错误信息:{}'.format(str(yzm_val)))
                        raise LoginError
                driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[2]/div[4]/div[1]/div/input').clear()
                driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[2]/div[4]/div[1]/div/input').send_keys(
                    yzm_val)
                driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div[2]/div[4]/button').click()
                time.sleep(1)
                if '验证码不正确' in driver.page_source:
                    try_num += 1
                    time.sleep(2)
                    if try_num > 10:
                        self.result['login'] = 0
                        self.result['errors'].append('输入的验证码有误')
                        raise LoginError
                else:
                    break
            time.sleep(2)
            cookies = driver.get_cookies()
            self.cookie = ''
            for i in range(len(cookies)):
                self.cookie += cookies[i]['name'] + '=' + cookies[i]['value']
                if i != len(cookies) - 1:
                    self.cookie += '; '
            # print(self.cookie)
            # vss_b = self.cookie.split('vssJwt=')[0]
            # vss_a = self.cookie.split('vssJwt=')[-1]
            # self.cookie = 'vssJwt=' + vss_a + '; ' + vss_b
            # self.cookie = self.cookie[:-2]
            # print(self.cookie)



    # 订货单

    def get_order_header(self, current_page='1', stp=''):
        data = dict()
        filters = list()
        if self.req_params["number"]:
            filters.append({"property": "number", "value": self.req_params["number"]})  # 单号
        if self.req_params["srcNumber"]:
            filters.append({"property": "srcNumber", "value": self.req_params["srcNumber"]})  # 来源单号
        if stp:
            filters.append({"property": "receiverName", "value": stp})  # 门店名称
        if self.req_params["createDateB"] != '':
            filters.append({"property": "dateCreated:[,]", "value": [self.req_params["createDateB"] + ' 00:00:00', self.req_params["createDateE"] + ' 23:59:59']})  # 生成日期
        filters.append({"property": "lastModified:[,]", "value": [self.req_params["lastModifiedS"] + ' 00:00:00',
                                                                 self.req_params["lastModifiedE"] + ' 23:59:59']})  # 最后修改时间
        data["fetchParts"] = []
        data["filters"] = filters
        data["sorters"] = [{"property": "number", "direction": "desc"}]
        data["page"] = int(current_page) - 1
        data["pageSize"] = self.page_size
        data = str(data).replace("'", '"').replace(', ', ',').replace(': ', ':').encode('utf-8')
        vss = ''
        for ivss in self.cookie.split('; '):
            if 'vssJwt' in ivss:
                vss = ivss.split('=')[-1]
        headers = {
            'authority': 'vss.hd123.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'trace_id': 'df255b33-0064-4609-b5ea-1c8a8cea0d44',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'content-type': 'application/json',
            'accept': 'application/json',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'vssjwt': vss,
            'origin': 'https://vss.hd123.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://vss.hd123.com/app.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie
        }
        response = requests.post(timeout=200, url='https://vss.hd123.com/vss-web/web/{}/receiveBill/list'.format(self.username[0:4]),
                                 headers=headers, data=data,
                                 verify=False)
        return response.text

    def get_order_line(self, uuid=''):
        headers = {
            'authority': 'vss.hd123.com',
            'content-length': '0',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'trace_id': '064f1cdc-0cf8-4bb4-a114-85ada06d4793',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'content-type': 'application/json',
            'accept': 'application/json',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'vssjwt': self.cookie.split('vssJwt=')[1].split('_uid_')[0].replace(';', ''),
            'origin': 'https://vss.hd123.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://vss.hd123.com/app.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie
        }

        response = requests.post(timeout=200, url=
        'https://vss.hd123.com/vss-web/web/{}/receiveBill/detail/{}'.format(self.username[0:4], uuid),
                                 headers=headers, verify=False)
        return response.text

    def analyze_order_header(self, order_header):
        order_header_data = list()
        json_data = json.loads(order_header)
        records = json_data['records']
        state_dict = {'unconfirm': '未确认', 'confirmed': '已确认', 'invalid': '已作废'}
        for record in records:
            detail = dict()
            detail['单号'] = str(record['number'] or '').strip()
            detail['状态'] = str(state_dict.get(record['state']) or '').strip()
            detail['来源单号'] = str(record['srcNumber'] or '').strip()
            detail['单据类型'] = str(record['type'] or '').strip()
            detail['收货单位'] = str((record['receiverCode'] + ' ' + record['receiver']) or '').strip()
            detail['数量'] = str(record['qty'] or '').strip()
            detail['金额'] = str(record['amount'] or '').strip()
            detail['供应商'] = str((record['vendorId'] + ' ' + record['vendorName']) or '').strip()
            detail['生成日期'] = str(record['dateCreated'] or '').split('T')[0].strip()
            detail['uuid'] = str(record['uuid'] or '').split('T')[0].strip()
            order_header_data.append(detail)
        page_message = dict()
        page_message['current_page'] = int(json_data['page']) + 1
        page_message['total_page'] = int(json_data['pageCount'])
        page_message['total_num'] = int(json_data['recordCount'])
        page_message['current_num'] = len(order_header_data)
        return order_header_data, page_message

    def analyze_order_line(self, order_line):
        js_data = json.loads(order_line)
        data = js_data['data']
        order_line_data = dict()
        order_line_data['来源单据类型'] = data.get('srcType') or ''
        order_line_data['结算单位'] = (data.get('companyCode') or '') + ' ' + (data.get('companyName') or '')
        order_line_data['确认日期'] = (data.get('confirmDate') or '').split('T')[0]
        order_line_data['备注'] = data.get('remark') or ''
        order_line_data['收货仓位'] =  (data.get('warehouseCode') or '') + ' ' + (data.get('warehouse') or '')
        order_line_data['商品详情'] = list()
        lines = data['lines']
        for line in lines:
            detail = dict()
            detail['条码'] = str(line.get('barcode') or '')
            detail['商品名称'] = str(line.get('skuName') or '')
            detail['商品编码'] = str(line.get('skuCode') or '')
            detail['商品类型'] = str(line.get('skuType') or '')
            detail['包装'] = str(line.get('qpcText') or '')
            detail['包装数量'] = str(line.get('qpcQty') or '')
            detail['定货数量'] = str(line.get('ordQty') or '')
            detail['数量'] = str(line.get('qty') or '')
            detail['价格'] = str(line.get('price') or '')
            detail['金额'] = str(line.get('amount') or '')
            detail['单位'] = str(line.get('unit') or '')
            order_line_data['商品详情'].append(detail)
        return order_line_data

    def crawling_order(self):
        if self.req_params['createDateB'].isdigit():
            self.req_params['createDateB'] = time.strftime('%Y-%m-%d',
                                                           time.localtime(
                                                               int(self.req_params['createDateB']) / 1000))
        if self.req_params['createDateE'].isdigit():
            self.req_params['createDateE'] = time.strftime('%Y-%m-%d',
                                                           time.localtime(int(self.req_params['createDateE']) / 1000))
        if self.req_params['lastModifiedS'].isdigit():
            self.req_params['lastModifiedS'] = time.strftime('%Y-%m-%d',
                                                           time.localtime(
                                                               int(self.req_params['lastModifiedS']) / 1000))
        if self.req_params['lastModifiedE'].isdigit():
            self.req_params['lastModifiedE'] = time.strftime('%Y-%m-%d',
                                                           time.localtime(int(self.req_params['lastModifiedE']) / 1000))
        try:
            self.login()
            # self.cookie = 'vssJwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvd25lciI6IjEyMDEyIiwidXNyTmEiOiLlronlvr3mlrDluIzmnJvnmb3luJ3kubPkuJrmnInpmZDlhazlj7giLCJxdWFsaWZpY2F0aW9ucyI6WyJkaXN0cmlidXRvciJdLCJ1c3JDZCI6Ijk5MDcxMjAxMiIsInJlY2VpdmVCaWxsQXVkaXQiOmZhbHNlLCJ1c3JUcCI6InZlbmRvciIsInVzcklkIjoiM2I5YTQ3MjUtZGI0Yi0xMWU4LWEwNmQtMDA4Y2ZhZTU3ODQwIiwibGFuZyI6IlpIIiwiZXhwIjoxNjM0ODgxODQ5LCJpYXQiOjE2MzQ3OTU0NDksInRlbmFudCI6Ijk5MDcifQ.gyLwe3apL9K0LivptvXnjrSTkE7OlK3Y-WKkqPsWLXc; _uid_=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzQ4ODE4NDksIlVTRVJfSUQiOiJ2c3NhZG1pbiIsImlhdCI6MTYzNDc5NTQ0OX0.zRhRapG4f-E8D6qeUJ5A9WcVfCTTodO-JNfhQSOtyYA'
        except LoginError:
            self.result['login'] = 0
            self.result['errors'].append('登录失败')
        else:
            flag = True
            total_num = 0
            for stp in self.sold_to_party:
                current_page = 1
                total_page = -1
                total_num_vds = 0
                warning = 0
                for fuuu in range(25):
                    try:
                        order_header = self.get_order_header(str(current_page), stp['name'])
                        order_header_data, message = self.analyze_order_header(order_header)
                        time.sleep(self.delay)
                    except RequestError:
                        if current_page == total_page:
                            self.result['errors'].append(
                                '供应商{}第{}页抓取失败，丢失1-{}条单据数据'.format(stp['code'], current_page, self.page_size))
                            self.result['info']['lose_min'] += 1
                        else:
                            self.result['errors'].append(
                                '供应商{}第{}页抓取失败，丢失{}条单据数据'.format(stp['code'], current_page, self.page_size))
                            self.result['info']['lose_min'] += self.page_size
                        self.result['info']['lose_max'] += self.page_size
                    except AnalyzeError:
                        if current_page == total_page:
                            self.result['errors'].append(
                                '供应商{}第{}页解析失败，丢失1-{}条单据数据'.format(stp['code'], current_page, self.page_size))
                            self.result['info']['lose_min'] += 1
                        else:
                            self.result['errors'].append(
                                '供应商{}第{}页解析失败，丢失{}条单据数据'.format(stp['code'], current_page, self.page_size))
                            self.result['info']['lose_min'] += self.page_size
                        self.result['info']['lose_max'] += self.page_size
                    else:
                        total_page = max(message['total_page'], total_page)
                        total_num_vds = max(message['total_num'], total_num_vds)
                        self.result['info']['crawling_num'] += message['current_num']
                        for head in order_header_data:
                            order_data = dict(head={}, data={}, code=1, errors='')
                            order_data['head'] = head
                            uuid = head['uuid']
                            try:
                                order_line = self.get_order_line(uuid=uuid)
                                order_line_data = self.analyze_order_line(order_line)
                                time.sleep(self.delay)
                            except RequestError:
                                order_data['code'] = 0
                                order_data['errors'] = '单据行抓取错误'
                            except AnalyzeError:
                                order_data['code'] = 0
                                order_data['errors'] = '单据行解析错误'
                            else:
                                order_data['data'] = order_line_data
                                self.result['info']['succeed'] += 1
                            finally:
                                order_md5 = self.get_md5(order_data)
                                order_data['kms_md5'] = order_md5
                                self.result['form'].append(order_data)
                    finally:
                        if warning == 2:
                            flag = False
                            self.result['info']['lose_min'] -= (warning + 1) * self.page_size
                            self.result['errors'].append('供应商{}前三页抓取失败，自动切换'.format(stp['code']))
                            break
                        if total_page <= 0 or current_page > total_page:
                            warning += 1
                        if current_page >= total_page != -1:
                            break
                        current_page += 1
                total_num += total_num_vds
            self.result['info']['failed'] = self.result['info']['crawling_num'] - self.result['info']['succeed']
            if flag:
                self.result['info']['total_num'] = total_num
                self.result['info']['total_min'] = self.result['info']['crawling_num'] + self.result['info']['lose_min']
                self.result['info']['total_max'] = self.result['info']['crawling_num'] + self.result['info']['lose_max']
            else:
                self.result['info']['lose_max'] = -1
                self.result['info']['total_min'] = self.result['info']['crawling_num']



if __name__ == '__main__':

    req2 = {"kms_all_store": "true", "principal_id": "",
            "sold_to_party" : [{"name": "", "code": ""}], "KMS_path_type": "PRO环境",
            "password": "930705",
            "doc": "验收单", "kms_ip": "", "force": "0", "ka_name": "全时便利",
            "tenantry_id": "46cf3c61e30658e302a30bba71a1c156", "username": "",
            "lastModifiedS": "2021-10-15", "lastModifiedE": "2021-10-20",
            'state': '', 'number': '','vendorName': '', 'warehouse': '','createDateB': '', 'createDateE': '',
            }

    aa = QuanshibianliSpider(req_params=req2)
    aa.crawling_return()
    res = json.dumps(aa.result, ensure_ascii=False)
    print(res)

