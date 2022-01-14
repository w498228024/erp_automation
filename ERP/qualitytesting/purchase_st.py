# coding=utf-8
import json
import traceback
import requests
import unittest

from jsonpath import jsonpath

from Common.FontColor import outcome
from Common.MyUnit import MyTest
from random import choice
from Common.CusMethod import random_code, random_str, random_randint
from Common.ReadYaml import ConfigYaml,ReadKeyWorld
from Common.DataHandle import ReRun
from ERP.qualitytesting.Public import QualitytestingData
from ERP.warehousenew.management_st import new_wm
qtd = QualitytestingData()



class purchase_qualitytesting(MyTest):

    '''
    采购--质检
    '''

    warehouse_info = choice(new_wm.warehouse_list_new(status=2))
    
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_purchase_qualitytesting(self):
        '''
        质检列表
        '''
        try:
            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            self.url = ConfigYaml("domain_name").base_url + self.url
            self.data['warehouseId'] = warehouse_id
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_generate_qa_order(self):
        '''
        生成质检单
        '''
        try:
            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            batch_no = qtd.send_to_qa_list(warehouse_id).get("purchaseBatchNo")
            self.url = ConfigYaml("domain_name").base_url + self.url
            self.data['purchaseBatchNos'] = [batch_no]
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_qa_order_list(self):
        '''
        质检单_列表
        '''
        try:

            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save(self):
        '''
        开始质检
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_no = qtd.qa_order_list(warehouse_id).get("qaOrderNumber")
            self.url = ConfigYaml("domain_name").base_url + self.url
            self.data['qaOrderNumber'] = qa_no
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save_start(self):
        '''
        质检
        '''
        try:
            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_info = qtd.quality_inspection(warehouse_id)
            qa_no = qa_info.get("qaOrderNumber")
            self.data['qaOrderNumber'] = qa_no
            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save_part(self):
        '''
        质检部分通过，部分次品
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_info = qtd.quality_inspection(warehouse_id)
            qa_no = qa_info.get("qaOrderNumber")
            unpack_quantity = int(qa_info.get("unpackQuantity"))
            imperfect_quantity = random_randint(1, unpack_quantity - 1)
            self.data['qaOrderNumber'] = qa_no
            self.data['imperfectQuantity'] = imperfect_quantity
            self.data['standardQuantity'] = unpack_quantity - imperfect_quantity

            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save_nopass(self):
        '''
        质检不合格
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_info = qtd.quality_inspection(warehouse_id)
            qa_no = qa_info.get("qaOrderNumber")
            unpack_quantity = int(qa_info.get("unpackQuantity"))
            imperfect_quantity = random_randint(1, unpack_quantity)
            self.data['qaOrderNumber'] = qa_no
            self.data['imperfectQuantity'] = imperfect_quantity
            self.data['standardQuantity'] = unpack_quantity - imperfect_quantity

            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save_review(self):
        '''
        质检再次复核
        '''
        try:
            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            self.url = ConfigYaml("domain_name").base_url + self.url
            qa_data = qtd.quality_inspection_review_list(warehouse_id)
            self.data['qaOrderId'] = qa_data.get('id')
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()
            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_result_save_review_nopass(self):
        '''
        质检再次复核--不合格
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_data = qtd.quality_inspection_review_list(warehouse_id)
            self.data['qaOrderId'] = qa_data.get('id')
            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
        
    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_qa_data_check(self):
        '''
        质检次品数据校验，多接口校验，整单合格，次品数量校验
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_info = qtd.quality_inspection(warehouse_id)
            qa_no = qa_info.get("qaOrderNumber")
            unpack_quantity = int(qa_info.get("unpackQuantity"))
            imperfect_quantity = random_randint(1, unpack_quantity - 1)
            standard_quantity = unpack_quantity - imperfect_quantity
            qtd.result_save_nopass(qa_no, imperfect_quantity, standard_quantity)
            self.data['qaOrderNumber'] = qa_no
            self.url = ConfigYaml("domain_name").base_url + self.url
            r = requests.post(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            imperfectQuantity = jsonpath(r.json(), "$..imperfectQuantity")
            if imperfectQuantity and isinstance(imperfectQuantity, list) and imperfectQuantity[0]:
                after_imperfect_quantity = imperfectQuantity[0]    #质检完成列表次品数量
            else:
                after_imperfect_quantity = 0

            imperfect_info = qtd.imperfect_order(qa_no)    #次品列表数据次品数量检验
            imperfect_list_num = jsonpath(imperfect_info, "$..imperfectQuantity")
            if imperfect_list_num and isinstance(imperfect_list_num, list) and imperfect_list_num[0]:
                imperfect_num = imperfect_list_num[0]
            else:
                imperfect_num = 0
            if imperfect_quantity == imperfect_num == after_imperfect_quantity:
                self.result = {"success": True}
            else:
                self.result = {"success": False}

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular

    # @unittest.skipIf(condition, "暂时跳过")
    @ReRun(MyTest.setUp)
    def test_qa_operator(self):
        '''
        变更质检人
        '''
        try:

            warehouse_id = purchase_qualitytesting.warehouse_info.get("id")
            qa_info = qtd.quality_inspection(warehouse_id)
            operator_info = qtd.get_purchase_buyer()
            self.url = ConfigYaml("domain_name").base_url + self.url
            self.data['id'] = qa_info.get("id")
            self.data['qaOperatorId'] = operator_info.get("id")
            self.data['qaOperatorName'] = operator_info.get("userName")
            r = requests.put(self.url, headers=self.headers, json=self.data, stream=True, verify=False)
            self.result = r.json()

            self.time = r.elapsed.total_seconds()
        except:
            self.singular = str(traceback.format_exc())
            outcome('red', self.singular)
            return self.singular
