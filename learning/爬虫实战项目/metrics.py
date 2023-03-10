from selenium import webdriver
import pymysql as sql
import time
import random

class metrics(object):
    # 初始化信息
    def __init__(self):
        # mysql登录信息
        self.host='127.0.0.1'
        self.user='root'
        self.password='123456'
        self.chartset='utf8'
        self.database='metrics_db'
        #webdriver初始化
        self.url="https://metrics.torproject.org/rs.html#details/0E300A0942899B995AE08CEF58062BCFEB51EEDF"
        self.driver_path=r"D:\python\chromedriver.exe"
        #获取数据
        self.lable=[]
        self.tip=[]
        self.content=[]
        self.image_f=[]
        self.image_s=[]
        self.time=[]
    #建立数据库
    def set_sqldb(self,sql):
        db = sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
        )
        cursor=db.cursor()
        try:
            cursor.execute("create database metrics_db character set utf8;")
        except:
            pass
        cursor.close()
        db.close()

    #建立mysql数据表
    def set_sqlist(self,sql,list_lable):
        db=sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
            database=self.database
        )
        cursor=db.cursor()
        sql="""drop table if exists `%s`"""%((list_lable))
        cursor.execute(sql)
        if list_lable=='History':
            sql = """
                       create table if not  exists `%s`(id int auto_increment primary key comment'序列号',
                       time VARCHAR(255) not null comment '月份',
                       graph1 longblob comment '图片',
                       graph2 longblob comment '图片');""" % (list_lable)
        else:
            sql="""
                        create table if not  exists `%s`(id int auto_increment primary key comment'序列号',
                        item VARCHAR(255) not null comment '项目名称',
                        value VARCHAR(255) not null comment '内容',
                        notes VARCHAR(255) not null comment '备注');"""%(list_lable)
        cursor.execute(sql)
        cursor.close()
        db.close()

    # 数据转换清洗
    def wash_data(self,wash,flag):
        if flag==0:
            for i in range(len(wash)):
                self.lable.append(wash[i].text)

        a=0
        if flag==1:
            for i in range(len(wash)):
                if(wash[i].text)=='':
                    a+=1
                    if a==2:
                        continue
                self.content.append(wash[i].text)

        b=0
        if flag==2:
            for i in range(len(wash)):
                if(b==0):
                    self.tip.append(wash[i].text)
                if(b!=0):
                    b-=1
                if wash[i].text=='Flags':
                    b=3
                if wash[i].text=='Advertised Bandwidth':
                    b=1
    # 添加图片数据
    def insert_picture_sqldb(self,sql,list_lable):
        db = sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
            database=self.database
        )
        cursor=db.cursor()
        sql="insert into History(time,graph1,graph2)values(%s,%s,%s);"
        for i in range(len(self.time)):
            try:
                # 执行sql语句
                cursor.execute(sql,[self.time[i],self.image_f[i],self.image_s[i]])
                # 数据库执行sql语句
                db.commit()
            except Exception as res:
                # 发生错误时回滚
                db.rollback()
                print("error %s" % res)

        cursor.close()
        db.close()

    #访问网页
    def website_get(self):
        option=webdriver.ChromeOptions()
        option.headless=True
        option.binary_location=r'D:\Google\Chrome\Application\chrome.exe'
        self.driver = webdriver.Chrome(executable_path=self.driver_path,options=option)
        self.driver.get(self.url)
        time.sleep(10)
        # 获取lable
        wash=self.driver.find_elements_by_tag_name('h3')
        metri.wash_data(wash,0)
        #获取tip
        wash=self.driver.find_elements_by_class_name('tip')
        wash.pop(0)
        metri.wash_data(wash,2)
        #获取content
        wash=self.driver.find_elements_by_tag_name('dd')
        metri.wash_data(wash,1)
        #获取image曲线图
        self.image_f.append(self.driver.find_element_by_xpath('//*[@id="bw_month"]').screenshot_as_png)
        self.image_s.append(self.driver.find_element_by_xpath('//*[@id="weights_month"]').screenshot_as_png)
        self.time.append(self.driver.find_element_by_id('history-1m-tab').text)

        self.driver.find_element_by_id('history-6m-tab').click()
        self.image_f.append(self.driver.find_element_by_xpath('//*[@id="bw_months"]').screenshot_as_png)
        self.image_s.append(self.driver.find_element_by_xpath('//*[@id="weights_months"]').screenshot_as_png)
        self.time.append(self.driver.find_element_by_id('history-6m-tab').text)

        self.driver.find_element_by_id('history-1y-tab').click()
        self.image_f.append(self.driver.find_element_by_xpath('//*[@id="bw_year"]').screenshot_as_png)
        self.image_s.append(self.driver.find_element_by_xpath('//*[@id="weights_year"]').screenshot_as_png)
        self.time.append(self.driver.find_element_by_id('history-1y-tab').text)

        self.driver.find_element_by_id('history-5y-tab').click()
        self.image_f.append(self.driver.find_element_by_xpath('//*[@id="bw_years"]').screenshot_as_png)
        self.image_s.append(self.driver.find_element_by_xpath('//*[@id="weights_years"]').screenshot_as_png)
        self.time.append(self.driver.find_element_by_id('history-5y-tab').text)


    # 添加文本数据
    def insert_txt_sqldb(self,sql,list_lable,st1,st2):
        db = sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
            database=self.database
        )
        cursor=db.cursor()
        sql = """insert into `%s`(item,value,notes)values ('%s','%s','%s')""" % ((list_lable), st1, st2, 'null')
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 数据库执行sql语句
            db.commit()
        except Exception as res:
            # 发生错误时回滚
            db.rollback()
            print("error %s" % res)

        cursor.close()
        db.close()
    # 本地存储图片数据
    def extract_picture(self,sql):
        db = sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
            database=self.database
        )
        cursor = db.cursor()
        cursor.execute('select graph1 from History')
        out_1=cursor.fetchall()
        cursor.execute('select graph2 from History')
        out_2=cursor.fetchall()
        for i in range(4):
            with open('pair'+str(i+1)+'_graph_1.png',mode="wb")as f1:
                f1.write(out_1[i][0])
                f1.close()
            time.sleep(random.uniform(2, 3))
            with open('pair'+str(i+1)+'_graph_2.png',mode="wb")as f2:
                f2.write(out_2[i][0])
                f2.close()
            time.sleep(random.uniform(2, 3))
        cursor.close()
        db.close()
    # 存入txt文件
    def save(self):
        db = sql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            charset=self.chartset,
            database=self.database
        )
        cursor = db.cursor()
        cursor.execute('select * from Configuration')
        out_put = cursor.fetchall()
        for a in out_put:
            with open('metrics_1.txt','a') as f:
                f.write(str(a)+'\n')
                f.close()
        cursor.execute('select * from Properties')

        out_put2 = cursor.fetchall()
        for a in out_put2:
            with open('metrics_2.txt', 'a') as f:
                f.write(str(a) + '\n')
                f.close()
        cursor.close()
        db.close()

if __name__=="__main__":
    metri=metrics()
    metri.set_sqldb(sql)
    metri.website_get()
    for i in range(len(metri.lable)):
        metri.set_sqlist(sql,metri.lable[i])
    # 表1
    for i in range(11):
        metri.insert_txt_sqldb(sql,metri.lable[0],metri.tip[i],metri.content[i])
    # 表2
    for i in range(11,len(metri.content)):
        metri.insert_txt_sqldb(sql,metri.lable[1],metri.tip[i],metri.content[i])
    # 表3
    metri.insert_picture_sqldb(sql,metri.lable[2])
    #提取sql图片数据并本地保存
    metri.extract_picture(sql)
    #提取所有数据保存到txt文件
    metri.save()