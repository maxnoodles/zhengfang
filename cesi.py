import re
from lxml import etree
import requests
import time
import os

class Spider:
    def __init__(self, uid, password, name, kc):
        # 初始参数
        self.CheckCodeUrl = 'CheckCode.aspx'
        # self.PostUrl = 'default2.aspx'
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        self.uid = uid
        self.password = password
        self.name = name.encode('gb2312', 'replace')
        self.kc = kc
        self.url1 = "http://jwc.gdlgxy.com/default4.aspx"
        self.url2 = 'http://jwc.gdlgxy.com/xf_xsqxxxk.aspx?xh='+self.uid+'&xm={}&gnmkdm=N121203'.format(self.name)
        self.code = ''
        self.attempt = 0
        self.MAX_TIME = 50
        self.temp = 0

    def login(self):
        # 访问教务系统
        res = 0
        res = self.session.get(self.url1)
        # except:
        #     print('无法获取网址')
        html = etree.HTML(res.text)

        __VIEWSTATE = html.xpath('//*[@id="form1"]/input/@value')[0]
        # __VIEWSTATE = 'dDwxMTE4MjQwNDc1Ozs+i9laKsPigZHjeuJ/iNx4CF54wKA='
        data = {
            "RadioButtonList1": "学生".encode('gb2312', 'replace'),
            "__VIEWSTATE": __VIEWSTATE,
            "TextBox1": self.uid,
            "TextBox2": self.password,
            # "txtSecretCode": code,
            "Button1": "",
            # "lbLanguage": "",
            # 'hidPdrs':"",
            # 'hidsc':"",
        }
        # 登陆教务系统
        while True:
            try:
                response = self.session.post(self.url1, data=data)
                # print(response.text)
                if 'Object' in response.text:
                    print('登录成功')
                    break
                else:
                    time.sleep(2)
                    print('登录失败')
            except:
                time.sleep(2)
                print('登录失败')


    def getcheckcode(self):
        # 获取验证码并下载到本地
        imgUrl = "http://jwc.gdlgxy.com/CheckCode.aspx"
        imgresponse = self.session.get(imgUrl, stream=True)
        image = imgresponse.content
        DstDir = os.getcwd() + "\\"
        print("保存验证码到：" + DstDir + "code.jpg" + "\n")
        try:
            with open(DstDir + "code.jpg", "wb") as jpg:
                jpg.write(image)
        except IOError:
            print("IO Error\n")
        finally:
            pass
        # 手动输入验证码
        code = input("验证码是：")
        # 构建post数据

    def getViewState(self,page):
        # 从网页中获取viewstate
        return re.search('<input type="hidden" name="__VIEWSTATE" value="(.+?)" />',page.text).group(1)

    def getList(self):
        # 获取全部课程内容
        self.session.headers['Referer'] = self.url2

        while True:
            try:
                res = self.session.get(self.url2)
                view = self.getViewState(res)
                break
            except:
                print('viewstate获取失败')
                time.sleep(2)

        data2 = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'ddl_kcxz': '',
            'ddl_kcgs=': '',
            'ddl_ywyl': '有'.encode('gbk'),
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGridtxtPageSize': '100',
            'ddl_xqbs': '3',
            '__VIEWSTATE': view,
        }
        while True:
            try:
                kecheng = self.session.post(self.url2, data=data2)
                if kecheng.status_code == requests.codes.ok:
                    print('课程表获取成功')
                    break
                else:
                    print('重新获取课程表')
            except:
                print('重新获取课程表')
                time.sleep(1)

        pat = '<tr.+?</tr>'
        pat_code = '<input id=".+?" type="checkbox" name="(.+?)" />'
        pattern = re.compile(pat, re.S)
        codes = re.findall(pattern, kecheng.text)

        flag = 1
        for c in codes:
            a = re.findall(pat_code, c)
            print(a[1])
            if self.kc in c:
                kccode = re.findall(pat_code, c)
                self.code = kccode[0]
                flag = 0
                print(self.code)
                break
        if flag == 1:
            print("没有找到该课程")

    def submit(self):
        self.session.headers['Referer'] = self.url2
        while True:
            try:
                res = self.session.get(self.url2)
                view = self.getViewState(res)
                break
            except:
                print('viewstate获取失败')
                time.sleep(1)

        data2 = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'ddl_kcxz': '',
            'ddl_kcgs': '',
            'ddl_ywyl': '有'.encode('gbk'),
            'ddl_sksj': '',
            'TextBox1': '',
            'Button1': '提交'.encode('gbk'),
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGridtxtPageSize': '100',
            'ddl_xqbs': '3',
            self.code: 'on',
            '__VIEWSTATE': view,
            }
        while True:
            try:
                submitkc = self.session.post(self.url2, data=data2)
                if submitkc.status_code == requests.codes.ok:
                    print('提交成功')
                    break
            except:
                print('提交失败')
                time.sleep(1)
        #'判断选课是否成功'
        pat = '<legend>已选课程</legend><table.+?' + '公共选修课' + '.+?</table>'
        pattern = re.compile(pat, re.S)
        lenth = len(re.findall(pattern, submitkc.text))
        if (lenth == 1):
            exit('选课成功')
        else:
            print('选课错误')


if __name__ == '__main__':
    spider = Spider('1512402602007', 'qq8852077', '陈嘉鑫', '课程名称')
    # spider = Spider('账号', '密码', '真实姓名', '课程名称')
    spider.login()
    spider.getList()
    # spider.submit()
