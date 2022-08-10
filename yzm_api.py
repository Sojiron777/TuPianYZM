# from biz_cv.key_account.yzm import *
#
# dict_supermarket = {'宝商': baoshang.predict,
#                     '北国': beiguo.predict,
#                     '华润': huarun.predict,
#                     '人人乐': renrenle.predict,
#                     '山姆': shanmu.predict,
#                     '唐久': tangjiu.predict,
#                     '银座': yinzuo.predict,
#                     '永辉': yonghui.predict,
#                     '祥隆泰': xianglongtai.predict,
#                     '家乐福': carrefour.predict,
#                     '大润发': darunfa.predict,
#                     '全时': quanshi.predict,
#                     '步步高': bubugao.predict,
#                     '农工商': nonggongshang.predict,
#                     '苏果': suguo.predict,
#                     '美宜佳': meiyijia.predict,
#                     '快客': kuaike.predict,
#                     '易站连锁': yizhan.predict,
#                     '舞东风': wudongfeng.predict,
#                     '百世店加': baidianshijia.predict,
#                     '华南喜市多': huananxishiduo.predict,
#                     '中商平价': zhongshangPJ.predict,
#                     '家乐福2': carrefourtwo.predict,
#                     '苏宁': SN.predict,
#                     '重庆百货': chongqinBH.predict,
#                     '家佳源': jiajiayuan.predict,
#                     }
#
#
# def yzm(yzm_data, yzm_name):
#     yzm_text = dict_supermarket[yzm_name](yzm_data)
#     return yzm_text

# 请求接口
# -*- coding: utf-8 -*-
import base64
import json

import requests

storename_name_dict = {'全时': '1012', '苏果': '1015', '家佳源': '1026', '大润发': '1011', '唐久': '1006', '北国': '1002',
                       '舞东风': '1019', '祥隆泰': '1009', '永辉2': '1024', '农工商': '1014', '宝商': '1001', '家乐福': '1010',
                       '华润': '1003', '华南喜市多': '1021', '步步高': '1013', '美宜佳': '1016', '易站连锁': '1018', '快客': '1017',
                       '永辉': '1008', '中商平价': '1022', '人人乐': '1004', '银座': '1007', '山姆': '1005', '百世店加': '1020',
                       '家乐福2': '1023', '重庆百货': '1025', '苏宁': '1027','麻瓜ocr':'1028','浙大同力': '1029',}


def yzm(yzm_data, yzm_name, is_new=0):
    ip = 'http://42.193.1.34'
    if not is_new:
        url = ip + ':5000/Captcha'
        yzm_data = base64.b64encode(yzm_data)
        re = requests.post(url=url, data={'storename': storename_name_dict[yzm_name],
                                          'image': yzm_data,
                                          'words': ''})
        req_json = json.loads(re.text)
        if req_json['code'] == 0:
            yzm_val = req_json['message']
            return yzm_val
        else:
            return req_json
    else:
        url = 'http://192.168.0.183' + ':5001/Captcha'
        params = dict()
        params['params'] = base64.b64encode(yzm_data).decode()
        params = json.dumps(params)
        res = requests.post(url, data=params)
        res = res.json()
        if res['code'] == 0:
            return res
        else:
            return res['mess']