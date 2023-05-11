# Description
武理半自动交电费，只使用requests库，占用低

可以使用crontab挂在服务器上，每天监控电费

当低于某个阈值时会自动提交充电费申请，通过邮箱发送缴费二维码到邮箱中

# Modify Settings
请修改相应的账号密码等数据

![修改数据](https://bucket.pursuecode.cn/upload/2023/05/3.png)

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

