# PyTelegraf
## 整体架构
![image](https://user-images.githubusercontent.com/53639856/227758469-8b8b0c6c-b454-45c0-af0c-9b6e129a2270.png)
## 原理
基于Python38的asyncio包的协程优化
执行流程：input -> agg -> process -> output
热更配置：CONF.update
配置中心：在http服务中动态获取配置
本地配置分级
注意：由于Python协程特性，暂时不支持阻塞代码，否则将会阻塞事件循环。阻塞代码建议绕开CPython的GIL锁，并且使用多线程操作
