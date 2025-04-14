# 登录 PRTS

## 题目描述

普瑞赛斯（Priestess）在 Abyss 中封禁了刀客塔在 PRTS 中的账号，身为刀客塔的你要想尽一切办法登录 PRTS（但是一定要登录刀客塔的账号吗？

> - 本题与注入无关
> - 刀客塔的账号密码
>   - Username: VFTS352
>   - Password: 48399110
> - 不要在意网站壁纸，找不到好看的 PRTS 图了

## 开始做题

首先打开网页是一个登录页面，题目给了登录的账号密码，直接登录

- Username: VFTS352
- Password: 48399110

> 出自明日方舟2025年情人节调查问卷 ByMySide
>
> https://ak.hypergryph.com/bymyside

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414205942700.png)

登录成功后，发现提示被封禁

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414210323271.png)

打开网页控制台，发现图片是通过一个 API 获取的（换言之，不是直接通过静态文件处理的函数进行的），后面接受了一个参数

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414210419237.png)

所以尝试一下，发现存在路径穿越漏洞

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414210538813.png)

可以顺利读取到源码，可以看到有个 `app.config['SECRET_KEY']`，而这个网站从 Cookie 上看很可能用了 JWT（其实你从我的注释都能看出来，我没删掉注释）

所以我们拿着这个 secret 去构造一个新的身份，这里的 secret 为 `klHymUWIA8TmxWDD`

拿着我们 Cookie 里面的 token，可以看到 payload 里面含有 `sub` 这一项，这里写的 doctor

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414210745030.png)

所以我们可以猜测应该就是这里来决定了自己的身份，我们改成普瑞赛斯（priestess）

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414210928046.png)

得到 `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwcmllc3Rlc3MiLCJleHAiOjE3NDQ2MzkzODUsImlhdCI6MTc0NDYzNjE1Mn0.r_FH_PELDTa-SZw4je6sOjv4ZvcLdje-2PYPMUGjKao`

> 注：赛博厨子的 JWT 签名功能会自己添加一个 iat（即 token 签发时间，在本题不影响）
>
> ![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414211017141.png)

拿着新的 token 去改一下 Cookie，然后刷新就会发现我们变成普瑞赛斯了，同时也能得到 flag

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414211055158.png)

因为我用的这个 UI 包的 alert 不能选中，所以建议直接用控制台来复制

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250414211126369.png)

`flag{f8a5b200-3a49-4643-a897-5797f045a30f}`（动态 flag）

## 彩蛋

如果你把 Cookie 里面的 user 也改成 `priestess` 或者直接访问 `/api/get_avatar?username=priestess.png` 的话，能够得到一张赛博女鬼的图

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/get_avatarusername=priestess.png)