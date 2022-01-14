import pymysql
from pymysql.connections import Connection
from warnings import filterwarnings
filterwarnings('ignore', category=pymysql.Warning)
import threading
lock = threading.Lock()

class Sql:

    def __init__(self, encoding="utf-8", sqlname="JenKins"):
        '''
        :param sql:  sql语句
        :param db:  数据库名称
        '''
        self.sqlname = sqlname
        self.encoding = encoding
        self.host = "172.28.188.131"
        self.port = 3306
        self.user = "root"
        self.pwd = "123456"
        try:
            self.conn = Connection(host=self.host, user=self.user, password=self.pwd, database=self.sqlname,
                                   port=self.port, charset='utf8')
        except:
            raise ConnectionError("mysql connect error,please check configuration ....")

    def execute_sql(self, sql):
        '''
        执行sql语句
        :return:
        '''
        lock.acquire()
        self.conn.ping(reconnect=True)
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        values = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        lock.release()
        # self.conn.close()
        return values



if __name__=="__main__":
    create_response = "CREATE TABLE IF NOT EXISTS alpha_task(id INTEGER primary key NOT NULL AUTO_INCREMENT,even varchar (100), task_list text(20000000));"
    # create_result = "CREATE TABLE IF NOT EXISTS result(id INTEGER primary key NOT NULL AUTO_INCREMENT,funname varchar (100),totalnumber int default 0,passnumber int default 0, errornumber int default 0,failnumber int default 0,passrate float default 0,errorrate float default 0,failrate float default 0,modular varchar (30));"
    # create_status = "CREATE TABLE IF NOT EXISTS `case_status`(`status_id` INT NOT NULL, version varchar(100),science varchar(100), total_case varchar(100), duration varchar(100), start_time varchar(100), end_time varchar(100), max_time varchar(100), avg_time varchar(100), success_case varchar(100), fail_case varchar(100), report_title varchar(500), PRIMARY KEY ( `status_id` ))ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    # create_history = "CREATE TABLE IF NOT EXISTS case_history(id INTEGER primary key NOT NULL AUTO_INCREMENT,funname varchar (100),describes varchar(1000),priority varchar(50),address varchar(1000),result varchar(30), writer varchar(30),usetime float ,summary text(20000000), status INT NOT NULL , FOREIGN KEY (status) REFERENCES case_status(status_id) on delete cascade on update cascade);"
    insert_startus = "INSERT INTO task(task_name, task_list) VALUES ('jenkins_task', 'ceshi');"
    #
    #
    # sql_sentence = "SELECT id, package_number FROM package WHERE is_confirmed_sku_quantity=0 and warehouse_id=%s and package_number is not null and status=2;" % (
    #     8)
    # data_info = Sql(sql=create_history, switch=False).execute_sql()
    # print(data_info)

    print(Sql().execute_sql(create_response))





