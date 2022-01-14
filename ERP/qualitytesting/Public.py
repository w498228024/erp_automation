
# coding=utf-8
import json
from time import sleep, time
from jsonpath import jsonpath
import requests
from Common.CusMethod import random_str, random_letter, random_code, get_data_time, random_randint, random_time
from Common.ReExecution import NumberCycles
from Common.ReadWriteIni import ReadWrite
from Common.ReadYaml import ReadPublic, ConfigYaml, ReadKeyWorld
from Common.Login import Login
from random import choice


class QualitytestingData:

    purchase_time = ''
    purchase_order = ''
    def __init__(self):
        """
        关于产品模块相关公共数据类接口数据
        """
        self.login = Login
        self.token_key = ConfigYaml('token_key').base_config
        self.token_value = ReadWrite().read_ini_token()
        self.headers = {self.login.content_type_key: self.login.content_json_type_value,
                        self.token_key: self.token_value}

        self.warehouse_name = ConfigYaml('wawarehouse_name').base_config
        self.matching_world = ConfigYaml('matching_world').base_config
        self.channle_name = ConfigYaml('channle_name').base_config

        self.dir = "qualitytesting"
        self.key_world = ReadKeyWorld(catalog="qualitytesting")

    def get_sku_list(self, warehouse_id, index=1):
        '''
        获取仓库数据库sku数据
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="get_sku_list")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['warehouseId'] = warehouse_id
        data['pageIndex'] = index
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data'):
            if r.json().get('data').get('list'):
                return r.json().get('data').get('list')
            else:
                raise ValueError(f"sku数据为空:{r.json().get('data').get('list')}")
        else:
            raise ValueError("获取sku列表【data】字段未获取到")

    def get_purchase_buyer(self):
        '''
        获取采购员
        :param status:
        :param switch:
        :return:
        '''
        buyer = ConfigYaml('login_user').base_config
        public_data = ReadPublic(catalog=self.dir, key="get_purchase_buyer")
        url = self.login.base_url + public_data.public_value("url").format(buyer)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data').get("list"):
            result = jsonpath(r.json(), "$.data.list[0]")
            if result and choice(result):
                return choice(result)
            else:
                raise ValueError(f"jsonpath未提取到{buyer}userName值")
        else:
            raise ValueError(f"未找到采购员:{r.json()}")

    def add_plan(self, wawarehouse_id):
        '''
        添加采购计划
        :param status:
        :param switch:
        :return:
        '''
        sku_info = choice(self.get_sku_list(wawarehouse_id, index=random_randint(1, 10)))
        public_data = ReadPublic(catalog=self.dir, key="add_plan")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data["warehouseId"] = wawarehouse_id
        data["skuCodes"][0]['skuCode'] = sku_info.get("skuCode")
        data["skuCodes"][0]['quantity'] = random_randint(1, 15)
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get("success"):
            raise ValueError(f"创建采购计划失败，失败原因：{r.json()}")

    @NumberCycles(2)
    def purchase_plan_list(self, wawarehouse_id):
        '''
        获取仓库数据库sku数据
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="purchase_plan_list")
        url = self.login.base_url + public_data.public_value("url").format(wawarehouse_id, self.get_purchase_buyer().get("userName"), get_data_time(-7), get_data_time(0))
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data').get('list'):
            return r.json().get('data').get('list')[0]
        else:
            sleep(2)
            self.add_plan(wawarehouse_id)
            return self.purchase_plan_list(wawarehouse_id)

    def get_plan_item_ids(self, plan_id):
        '''
        获取采购子任务item_id
        :param status:
        :param switch: 为true返回采购计划子任务id，为false，返回采购计划采购价格，采购数量是否为0，两者均为0，返回false，二者均不为0，返回true
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="get_plan_item_ids")
        url = self.login.base_url + public_data.public_value("url").format(plan_id)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data').get('list'):
            for item in r.json().get('data').get('list'):
                real_price = item.get("realPrice")     #实际采购单价
                real_purchase_quantity = item.get("realPurchaseQuantity")   #实际采购数量
                supplier_name = item.get("supplierName")    #供应商
                if real_price == 0:
                    self.edit_purchase_price(item.get("id"))

                if real_purchase_quantity == 0:
                    self.edit_purchase_quantity(item.get("id"))

                if supplier_name != "自动化专属供应商":
                    self.edit_purchase_supplier(item.get("id"))

            result = jsonpath(r.json(), "$.data.list[*].id")

            if result:
                return result
            else:
                raise ValueError(f"jsonpath未提取到{plan_id}子任务item_ids值")

        else:
            raise ValueError(f"采购计划{plan_id}子任务列表为空")

    def edit_purchase_price(self, item_id):
        '''
        编辑采购单价
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="edit_purchase_price")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['ids'] = [item_id]
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"编辑采购单价失败:{r.json()}")

    def edit_purchase_quantity(self, item_id):
        '''
        编辑采购数量
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="edit_purchase_quantity")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['ids'] = [item_id]
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"编辑采购数量失败:{r.json()}")

    def edit_purchase_supplier(self, item_id):
        '''
        编辑采购供应
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="edit_purchase_supplier")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data[0]['id'] = item_id
        data[0]['supplierId'] = self.get_supplier_list(status=2).get("id")
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"编辑采购计划供应商失败:{r.json()}")

    def get_supplier_list(self, status=1, *args, **kwargs):
        '''
        获取供应商列表数据
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="get_supplier_list")
        if status == 1:
            url = self.login.base_url + public_data.public_value("url")
        elif status == 2:
            url = self.login.base_url + public_data.public_value("url").format("自动化专属供应商")
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data').get("list"):
            if status == 1:
                return choice(r.json().get('data').get("list"))

            elif status == 2:
                result = jsonpath(r.json(), "$.data.list[?(@.name=='自动化专属供应商')]")
                if result and isinstance(result, list):
                    return choice(result)
                else:
                    raise ValueError(f"jsonpath提取[自动化专属供应商失败]，结果值{r.json()}")
        else:
            raise ValueError(f"获取供应商列表失败{r.json()}")

    def get_shipping_address(self, plan_id):
        '''
        获取物流地址id
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="get_shipping_address")
        url = self.login.base_url + public_data.public_value("url").format(plan_id)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data'):
            result = jsonpath(r.json(), "$.data[0].id")
            if result and choice(result):
                return choice(result)
            else:
                raise ValueError(f"jsonpath未提取到采购计划{plan_id}物流地址")
        else:
            raise ValueError(f"未获取到采购计划{plan_id}物流地址")

    def count_create_offline_purchase_order(self, plan_id, address_id):
        '''
        获取采购计划批次号
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="count_create_offline_purchase_order")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['planItemIds'] = self.get_plan_item_ids(plan_id)
        data['shippingAddressId'] = address_id
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('data').get('batchNo'):
            return r.json().get('data').get('batchNo')
        else:
            raise ValueError(f"采购计划下单提取批次号失败：{r.json()}")

    def batch_offline_purchase_order(self, wawarehouse_id):
        '''
        获取采购计划线下下单
        :return:
        '''
        plan_id = self.purchase_plan_list(wawarehouse_id).get("id")
        address_id = self.get_shipping_address(plan_id)
        public_data = ReadPublic(catalog=self.dir, key="batch_offline_purchase_order")
        url = self.login.base_url + public_data.public_value("url")
        batch_no = self.count_create_offline_purchase_order(plan_id, address_id)
        data = public_data.public_value("bar")
        data['batchNo'] = batch_no
        data['shippingAddressId'] = address_id
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"采购计划线下下单失败：{r.json()}")

    def purchase_order_list(self, wawarehouse_id, status=0, *args, **kwargs):
        '''
        采购单--已下单列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="purchase_order_list")
        url = self.login.base_url + public_data.public_value("url").format(status, wawarehouse_id, self.get_supplier_list(status=2).get("name"))
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]

            else:
                sleep(2)
                self.batch_offline_purchase_order(wawarehouse_id)

            return self.purchase_order_list(wawarehouse_id, status=0)

    def wait_audit_list(self, wawarehouse_id, status=1, *args, **kwargs):
        '''
        采购单--已提交审核列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="purchase_order_list")
        url = self.login.base_url + public_data.public_value("url").format(status, wawarehouse_id,
                                                                           self.get_supplier_list(status=2).get("name"))
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]

            else:
                sleep(2)
                self.submit_wait_audit_info(wawarehouse_id)

            return self.wait_audit_list(wawarehouse_id, status=1)

    def audit_pass_list(self, wawarehouse_id, status=3, *args, **kwargs):
        '''
        采购单--审核通过列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="purchase_order_list")
        url = self.login.base_url + public_data.public_value("url").format(status, wawarehouse_id,
                                                                           self.get_supplier_list(status=2).get("name"))
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.audit_pass(wawarehouse_id)

            return self.audit_pass_list(wawarehouse_id, status=3)

    def purchase_logistics_list(self, wawarehouse_id, status=4, *args, **kwargs):
        '''
        采购单--物流列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="purchase_order_list")
        url = self.login.base_url + public_data.public_value("url").format(status, wawarehouse_id,
                                                                           self.get_supplier_list(status=2).get("name"))
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.purchase_logistics(wawarehouse_id)

            return self.purchase_logistics_list(wawarehouse_id, status=4)
        else:
            raise ValueError(f"获取已下单采购单失败：{r.json()}")

    def submit_wait_audit_info(self, wawarehouse_id):
        '''
        获取采购计划线下下单
        :return:
        '''
        purchase_id = self.purchase_order_list(wawarehouse_id).get("id")
        public_data = ReadPublic(catalog=self.dir, key="submit_wait_audit_info")
        url = self.login.base_url + public_data.public_value("url")
        data = [purchase_id]
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"已下单采购单下单失败：{r.json()}")

    def audit_pass(self, wawarehouse_id):
        '''
        采购单审核通过
        :return:
        '''
        purchase_id = self.wait_audit_list(wawarehouse_id, status=1).get("id")
        public_data = ReadPublic(catalog=self.dir, key="audit_pass")
        url = self.login.base_url + public_data.public_value("url")
        data = [purchase_id]
        r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"待审核采购单提交审核失败：{r.json()}")

    def purchase_logistics(self, wawarehouse_id):
        '''
        已确认采购单录入物流信息
        :return:
        '''
        purchase_id = self.audit_pass_list(wawarehouse_id, status=3).get("id")
        public_data = ReadPublic(catalog=self.dir, key="purchase_logistics")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['logisticsInfos'][0]['logisticsBillNumber'] = random_time()
        data['purchaseOrderId'] = purchase_id
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"已确认采购单添加物流失败：{r.json()}")

    def get_unpack_info(self, wawarehouse_id):
        '''
        获取拆包采购单信息
        :return:
        '''
        purchase_code = self.purchase_logistics_list(wawarehouse_id, status=4).get("purchaseOrderNumber")
        public_data = ReadPublic(catalog=self.dir, key="get_unpack_info")
        url = self.login.base_url + public_data.public_value("url").format(wawarehouse_id, purchase_code)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("purchaseOrderUnpackVos"):
                return r.json().get('data').get("purchaseOrderUnpackVos")
            else:
                raise ValueError(f"采购单信息为空：{r.json()}")
        else:
            raise ValueError(f"获取采购单信息失败：{r.json()}")

    def wms_unpack(self, wawarehouse_id):
        '''
        拆包
        :return:
        '''
        purchase_info = self.get_unpack_info(wawarehouse_id)
        public_data = ReadPublic(catalog=self.dir, key="wms_unpack")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        purchase_code = jsonpath(purchase_info, "$..purchaseOrderNumber")[0]
        data['searchValue'] = purchase_code
        for value in purchase_info:
            data['purchaseOrderId'] = value.get("purchaseOrderId")
            data['purchaseOrderItemId'] = jsonpath(value, "$..purchaseOrderItemId")[0]
            data['unpackQuantity'] = jsonpath(value, "$..notUnpackQuantity")[0]
            r = requests.put(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"采购单拆包异常：{r.json()}")

    def send_to_qa_list(self, wawarehouse_id, *args, **kwargs):
        '''
        待送检列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="send_to_qa_list")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['warehouseId'] = wawarehouse_id
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.wms_unpack(wawarehouse_id)

            return self.send_to_qa_list(wawarehouse_id)
        else:
            raise ValueError(f"未获取到质检数据：{r.json()}")

    def qa_order_list(self, wawarehouse_id, *args, **kwargs):
        '''
        质检单列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="qa_order_list")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['supplierName'] = self.get_supplier_list(status=2).get("name")
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.generate_qa_order(wawarehouse_id)

            return self.qa_order_list(wawarehouse_id)
        else:
            raise ValueError(f"质检单列表获取数据失败：{r.json()}")

    def generate_qa_order(self, warehouse_id):
        '''
        生成质检单
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="generate_qa_order")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        batch_no = self.send_to_qa_list(warehouse_id).get("purchaseBatchNo")
        data['purchaseBatchNos'] = [batch_no]
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"生成质检单失败：{r.json()}")

    def start_check(self, warehouse_id):
        '''
        质检
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="start_check")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        qa_no = self.qa_order_list(warehouse_id).get("qaOrderNumber")
        data['qaOrderNumber'] = qa_no
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"质检失败：{r.json()}")

    def result_save_nopass(self, qa_no, imperfect_quantity, standard_quantity):
        '''
        质检
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="result_save_nopass")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['qaOrderNumber'] = qa_no
        data['imperfectQuantity'] = imperfect_quantity    #不合格数量
        data['standardQuantity'] = standard_quantity   #合格数量
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"质检失败：{r.json()}")

    def result_save(self, warehouse_id):
        '''
        质检不通过
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="result_save")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        qa_info = self.quality_inspection(warehouse_id)
        qa_no = qa_info.get("qaOrderNumber")
        unpack_quantity = int(qa_info.get("unpackQuantity"))
        imperfect_quantity = random_randint(1, unpack_quantity)
        data['qaOrderNumber'] = qa_no
        data['imperfectQuantity'] = imperfect_quantity
        data['standardQuantity'] = unpack_quantity - imperfect_quantity
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if not r.json().get('success'):
            raise ValueError(f"质检不合格检验失败：{r.json()}")

    def quality_inspection(self, wawarehouse_id, *args, **kwargs):
        '''
        质检中列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="quality_inspection")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['supplierName'] = self.get_supplier_list(status=2).get("name")
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.start_check(wawarehouse_id)

            return self.quality_inspection(wawarehouse_id)
        else:
            raise ValueError(f"质检单列表获取数据失败：{r.json()}")

    def quality_inspection_review_list(self, wawarehouse_id, *args, **kwargs):
        '''
        待复核列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="quality_inspection_review_list")
        url = self.login.base_url + public_data.public_value("url")
        data = public_data.public_value("bar")
        data['supplierName'] = self.get_supplier_list(status=2).get("name")
        r = requests.post(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")[0]
            else:
                sleep(2)
                self.result_save(wawarehouse_id)

            return self.quality_inspection_review_list(wawarehouse_id)
        else:
            raise ValueError(f"待复核列表获取数据失败：{r.json()}")

    def imperfect_order(self, qa_code, *args, **kwargs):
        '''
        次品列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="imperfect_order")
        url = self.login.base_url + public_data.public_value("url").format(qa_code)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        if r.json().get('success'):
            if r.json().get('data').get("list"):
                return r.json().get('data').get("list")

        else:
            raise ValueError(f"待复核列表获取数据失败：{r.json()}")

    def get_check_data(self, check_code, *args, **kwargs):
        '''
        质检单列表
        :param status:
        :param switch:
        :return:
        '''
        public_data = ReadPublic(catalog=self.dir, key="get_check_data")
        url = self.login.base_url + public_data.public_value("url").format(check_code)
        data = public_data.public_value("bar")
        r = requests.get(url, headers=self.headers, json=data, stream=True, verify=False)
        data_list = []
        if r.json().get('success'):
            result = jsonpath(r.json(), "$..sizeData.sizeData")
            skuSizeName = choice(jsonpath(r.json(), "$..skuSizeNameAndId.name"))
            if result and isinstance(result, list) and result[0]:
                for value in result[0]:
                    temp = {}
                    temp['sizeId'] = value.get("sizeId")
                    temp['sizeName'] = value.get("sizeName")
                    temp['actualValue'] = ""
                    temp['valid'] = False
                    temp['value'] = jsonpath(value, "$..measurementValue")[0]
                    data_list.append(temp)
                return skuSizeName, data_list
            else:
                return []
        else:
            raise ValueError(f"质检单列表获取数据失败：{r.json()}")

if __name__ == '__main__':
    print(QualitytestingData().batch_offline_purchase_order(8))