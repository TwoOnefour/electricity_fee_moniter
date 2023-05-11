import datetime
import os.path
from email.mime.multipart import MIMEMultipart
import requests
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
from lxml import etree
import base64
from enc import strEnc


class Moniter:
    def __init__(self, kwargs):
        self.sessions = requests.session()
        self.sessions.verify = False
        self.account = kwargs
        self.service = kwargs["service"]
        self.meterId = None
        self.limit_power = kwargs["limit_power"]
        self.amt = kwargs["amt"]
        self.room_info = {}
        self.sender = kwargs["mail_account"]
        self.mail_pwd = kwargs["mail_pwd"]
        self.recv_list = kwargs["recv_list"]
        if os.path.exists(os.path.split(os.path.realpath(__file__))[0] + "/meterId.txt"):
            with open(os.path.split(os.path.realpath(__file__))[0] + "/meterId.txt", "r") as f:
                self.meterId = f.read()

    def whut_login(self, service, username, password):
        self.sessions.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        })
        html = self.sessions.get("http://zhlgd.whut.edu.cn/tpass/login", params={
            "service": service
        })
        etree.HTMLParser(encoding="utf-8")
        # tree = etree.parse(local_file_path)
        tree = etree.HTML(html._content.decode("utf-8"))
        tpass = dict(tree.xpath('//*[@id="lt"]')[0].attrib)["value"]
        des = strEnc(username + password + tpass, "1", "2", "3")
        self.sessions.headers.update({})
        self.sessions.cookies.set(domain="whut.edu.cn", path="/", name="cas_hash", value="")
        # print(tpass)
        result = self.sessions.post(
            url="http://zhlgd.whut.edu.cn/tpass/login",
            params={
                "service": service
            },
            data={
                "rsa": des,
                "ul": len(username),
                "pl": len(password),
                "lt": tpass,
                "execution": "e1s1",
                "_eventId": "submit",
            }, verify=False, allow_redirects=False)
        if result.headers.get("location") is None:
            return False
        return result.headers["location"]

    def pay(self):
        orderno = self.sessions.post("http://cwsf.whut.edu.cn/elePayprojectCreateOrder", data={
            "payAmt": self.amt,  # 默认交1块
            "meterId": self.meterId,  # 只需要这个对得上就可以充钱
            "roomid": 1,
            "room": 1,
            "building": 1,
            "floorid": 1,
            "floor": 1,
            "build": 1,
            "payProjectId": 297,
            "area": 1,
            "dd": "给宿舍交钱啦",
            "areaid": 1,
            "factorycode": "E035"
        }).json()["payOrderTrade"]["orderno"]
        html = self.sessions.post("http://cwsf.whut.edu.cn/onlinePay", data={
            "orderno": orderno,
            "orderamt": self.amt,
            # "mess": "",
            # "start_limittxtime": "",
            "end_limittxtime": "",
            "payType": 26 # 微信
        })
        etree.HTMLParser(encoding="utf-8")
        # tree = etree.parse(local_file_path)
        tree = etree.HTML(html._content.decode("utf-8"))
        code = dict(tree.xpath('/html/body/div[5]/div/div[2]/div[2]/img')[0].attrib)["src"]
        self.send_mail(code)

    def get_build_information(self):
        factory_code = "E035"
        data = {
            "areaid": self.area,
            "factorycode": factory_code
        }
        self.build_dict = {}
        for i in self.sessions.post("http://cwsf.whut.edu.cn/queryBuildList", data=data).json()["buildList"]:
            now = i.split("@")
            self.build_dict[now[1].strip(" ")] = now[0]
            # print(f"{now[1]}\t\t{now[0]}")
            print(f"{now[1]}")

    def get_area_info(self):
        while True:
            print("请输入地区代号")
            print("\n".join(self.sessions.post("http://cwsf.whut.edu.cn/getAreaInfo", data={
                "factorycode": "E035"
            }).json()["areaList"]))
            try:
                self.area = int(input(""))
            except Exception as e:
                print("输入错误，请输入数字")
                continue
            if self.area > 12 or self.area < 0:
                print("输入错误，请输入1-13的数字")
            else:
                self.area = "{:04d}".format(self.area)
                break

    def select_build(self):
        while True:
            self.build = input("请选择你的缴费位置代号，如输入 东1舍 ").strip(" ")
            if self.build_dict.get(self.build):
                self.build = self.build_dict.get(self.build)
                break
            print("选择错误，请确认.ps:括号也要输入")

    def get_floor_list(self):
        while True:
            print("选择楼层或单元")
            floor = self.sessions.post("http://cwsf.whut.edu.cn/queryFloorList", data={
                "areaid": self.area,
                "factorycode": "E035",
                "buildid": self.build
            }).json()["floorList"]
            print(floor)
            self.floor = input().strip(" ")
            try:
                if int(self.floor) < floor[0] or int(self.floor) > floor[-1]:
                    print("输入错误，请重新输入")
                else:
                    break
            except Exception as e:
                print("输入错误，请重新输入")
    def get_room_info(self):
        # print("请输入你的房间号")
        room = self.sessions.post("http://cwsf.whut.edu.cn/getRoomInfo", data={
            "floorid": self.floor,
            "factorycode": "E035",
            "buildid": self.build
        }).json()["roomList"]
        room_dict = {}
        for i in room:
            now = i.split("@")
            room_dict[now[1].split("-")[1]] = now[0]
        print("\n".join(room))
        while True:
            self.room = input("请输入你的房间号").strip(" ")
            if room_dict.get(self.room):
                self.room = room_dict.get(self.room)
                break
            print("选择错误，请确认")

    def query_Room_Elec(self):
        self.meterId = self.sessions.post("http://cwsf.whut.edu.cn/queryRoomElec",data={
            "roomid": self.room,
            "factorycode": "E035"
        }).json()["meterId"]

    def electric_status(self):
        res = self.sessions.post("http://cwsf.whut.edu.cn/queryReserve",data={
            "meterId": self.meterId,
            "factorycode": "E035"
        })
        restext = res.json()
        print("{}\t目前电费：{}".format(str(datetime.datetime.now())[:-7], restext["remainPower"]))
        self.remain_power = restext["remainPower"]
        with open(os.path.split(os.path.realpath(__file__))[0] + "/meterId.txt", "w") as f:
            f.write(self.meterId)

    def send_mail(self, code):
        ret = True
        my_sender = self.sender  # 发件人邮箱账号
        my_pass = self.mail_pwd  # 发件人邮箱密码
        list = self.recv_list # 收件人列表
        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr([my_sender, my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["", ''])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "没电了，请在90秒内扫此码交钱！"  # 邮件的主题，也可以说是标题
            msg.attach(MIMEText('剩余电量为:{}度，请在90秒内扫码交钱，默认交{}块😊'.format(self.remain_power, self.amt), 'plain', 'utf-8'))
            attachment_1 = MIMEText(base64.b64decode(code.split(",")[1]), 'base64', 'utf-8')
            attachment_1['Content-Type'] = 'application/octet-stream'
            attachment_1['Content-Disposition'] = 'attachment;filename="QRcode.png"'
            msg.attach(attachment_1)
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            for i in list:
                server.sendmail(my_sender, i, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception as e:
            ret = False
            print(e)
        return ret

    def run(self):
        url = self.whut_login(self.service, self.account["username"], self.account["password"])
        if not url:
            print("登陆失败，请重新设定账号密码")
            return
        self.sessions.get(url)
        if not self.meterId:
            self.get_area_info()
            self.get_build_information()
            self.select_build()
            self.get_floor_list()
            self.get_room_info()
            self.query_Room_Elec()
        self.electric_status()
        if float(self.remain_power) < self.limit_power:
            self.pay()


if __name__ == "__main__":
    settings = {
        "username": "",  # 武理统一门户登陆账号
        "password": "",  # 武理统一门户登陆密码
        "service": "http://cwsf.whut.edu.cn/casLogin",
        "limit_power": 15,  # 十五度电的时候发二维码和邮件
        "amt": 1,  # 充一块, 注意！ 如果要使用，请先尝试几次再充大额度，最好还是自己上去充
        "mail_account": "",  # 你的邮箱,请使用qq邮箱，如不是qq邮箱需要修改send_mail()方法中的smtp服务器
        "mail_pwd": '',  # 你的邮箱认证码
        "recv_list": [""]  # 群发的list
    }
    my_moniter = Moniter(settings)
    my_moniter.run()
