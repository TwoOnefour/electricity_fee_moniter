# Description
武理半自动交电费，只使用requests库，占用低

可以使用crontab挂在服务器上，每天监控电费

当低于某个阈值时会自动提交充电费申请，通过邮箱发送缴费二维码到邮箱中

# Modify Settings
请修改相应的账号密码等数据

![修改数据](https://bucket.voidval.com/upload/2023/05/3.png)

第一次使用请直接运行
```angular2html
python3 electricity_fee_moniter.py
```

然后根据提示操作，选择对应的房间以后会将信息保存到本地，下一次就不用再选择了

直接运行即可

如果要修改监控的房间，请删除掉本地的meterId.txt
```angular2html
rm -rf meterId.txt
```

然后重新运行

# Usage
">>"为你的输入
```angular2html
[***@TwoOnefour electricity_fee_moniter]# python3 /home/admin/electricity_fee_moniter/electricity_fee_moniter.py
请输入地区代号
0001@学生宿舍马区东院
0002@学生宿舍马区西院
0003@学生宿舍南湖南院
0004@学生宿舍南湖北院
0005@学生宿舍余区
0006@教职工余区
0007@商业网点余区
0008@教职工马区东院
0009@教职工马区西院
0010@商业网点马区东院
0011@商业网点马区西院
0012@商业网点南湖南院
0013@商业网点南湖北院
>>4  
西12舍（原西院12栋）
西13舍（原西院13栋）
北1舍（原学海21栋）
北2舍（原鉴湖9栋）
北3舍（原鉴湖10栋）
北4舍（原鉴湖11栋）
北5舍（原鉴湖12栋）
学海1舍（原学海16栋）
学海2舍（原学海18栋）
学海3舍（原学海20栋）
学海4舍（原学海15栋）
学海5舍（原学海17栋）
学海6舍（原学海19栋）
学海7舍
请选择你的缴费位置代号，如输入 东1舍 西12舍（原西院12栋）
选择楼层或单元
[1, 2, 3, 4, 5, 6]  # 这里是1-6楼的意思
>>2
00002795@西12舍-201
00002796@西12舍-202
00002797@西12舍-203
00002798@西12舍-204
00002799@西12舍-205
00002800@西12舍-206
00002801@西12舍-207
00002802@西12舍-208
00002803@西12舍-209
00002804@西12舍-210
00002805@西12舍-211
00002806@西12舍-212
00002807@西12舍-213
00002808@西12舍-214
00002809@西12舍-215
00002810@西12舍-216
请输入你的房间号>>202
2023-05-11 22:22:59     目前电费：-0.12
```

![结果对应](https://bucket.pursuecode.cn/upload/2023/05/7.png)

可以看到电费是对得上的，-0.12度
# Crontab Example
```angular2html
0 12 * * * python3 /home/admin/electricity_fee_moniter/electricity_fee_moniter.py  > /home/admin/electricity_fee_moniter/running.log 2>&1
```

# Result

发送到邮箱

![最终效果](https://bucket.pursuecode.cn/upload/2023/05/4.png)

修改订单备注

![修改订单备注](https://bucket.pursuecode.cn/upload/2023/05/5.png)

交0.1元

![交钱0.1元，修改订单信息](https://bucket.pursuecode.cn/upload/2023/05/6.png)

不过还是交1块以上吧，好像0.1不会加电费😭

