> *Update*: [**rework**](https://github.com/Blurgyy/summer2019/tree/master/summer2019_mail)

> <del>*Update*: 以下工作无限期停止更新</del>

***
> - OUC信院新闻邮件推送服务，每 30 分钟检查一次更新 
> - 用 SMTP_SSL (465) 端口发送邮件 
> - （很可能被各大邮箱标记成 spam） 
> - `lang: python3`



*  `mail.py` ：发送邮件 
*  `crawl.py` ：爬取学院新闻 && 判断是否有更新 
*  `*.sec` ：用于代发邮件的邮箱（QQ邮箱）的验证信息 
    *  本处代码中使用的文件名是 `my.sec` （见 `mail.py` 中 `get_auth()`） 
    *  `mail.py` 仅读取 `*.sec` 文件的前两行 
    *  第一行：用于代发邮件的邮箱（QQ邮箱）地址（如123456789@qq.com） 
    *  第二行：QQ邮箱生成的 SMTP 授权码 （形如 `qgevahlsbtcmkelw` 的一串字符）
*  `*.to` ：收件人邮件地址列表，每行一个邮件地址（不限QQ邮箱），本处代码中的文件名是 `.to` （见 `mail.py` 中 `get_to()`） 



