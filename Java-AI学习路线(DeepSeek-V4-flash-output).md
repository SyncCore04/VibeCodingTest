# AI 时代 Java 后端学习路线（含 B 站视频）

> 适合：零基础或有一定编程基础，想走 Java 后端 + AI 应用开发方向
> 预估：每天 4-6 小时，零基础约 8-12 个月到可求职水平；有基础可压缩到 4-6 个月

## 一、学习策略

1. Java 基础是底盘，AI 框架只是外壳，不要跳过基础直接学 Spring AI / LangChain4j。
2. 用 AI 当教练和结对伙伴：让它解释报错、Review 你的代码、出测试题、设计练习，但核心代码要自己写。
3. 每学完一个阶段，做一个能写进简历的小项目，比只看视频有用得多。
4. 主线：Java 基础 → 数据库 → Spring Boot → 工程化 → 并发/JVM → 微服务 → AI 应用。

## 二、阶段路线

### 阶段 1：Java 基础（2-3 个月）

学习内容：语法、面向对象、集合、异常、泛型、反射、注解、Lambda/Stream、IO/NIO、多线程基础。

B 站视频：

- [黑马程序员 Java 零基础视频教程（上部）](https://www.bilibili.com/video/BV17F411T7Ao/)
- [黑马程序员 2026 版 AI+Java 零基础全套（可当主线）](https://www.bilibili.com/video/BV1TJxCzSEEZ/)
- [尚硅谷 Java 入门视频教程](https://www.bilibili.com/video/BV1Kb411W75N/)
- [尚硅谷 2024 最新 Java 入门视频教程（上部）](https://www.bilibili.com/video/BV1YT4y1H7YM/)

作业：完成一个学生管理系统或图书管理系统，从控制台版逐步升级到 JDBC 版；力扣简单题刷 50 道以上。

### 阶段 2：数据库（4-6 周）

学习内容：MySQL 建表设计、索引、事务、锁、SQL 优化、主从复制；JDBC → MyBatis / MyBatis-Plus → Spring Data JPA；Redis 缓存、分布式锁、黑马点评实战。

B 站视频：

- [尚硅谷 MySQL 数据库入门到大牛](https://www.bilibili.com/video/BV1iq4y1u7vj/)
- [尚硅谷 5 天上手 MySQL 视频教程](https://www.bilibili.com/video/BV1Cm421373b/)
- [黑马程序员 MybatisPlus 全套视频教程](https://www.bilibili.com/video/BV1Xu411A7tL/)
- [黑马程序员 Redis 入门到实战教程（黑马点评项目）](https://www.bilibili.com/video/BV1cr4y1671t/)

作业：为阶段 1 的项目加上 MySQL 持久化，再做 Redis 缓存和简单的分布式锁。

### 阶段 3：Spring 与 Web 开发（2-3 个月）

学习内容：HTTP/REST、Servlet/Tomcat 了解即可；Spring 核心 IoC/AOP；Spring Boot 3 自动配置；统一异常、参数校验、JWT 登录鉴权；前端学到能看懂 Vue 基础即可。

B 站视频：

- [黑马程序员 SpringBoot3 + Vue3 全套视频教程](https://www.bilibili.com/video/BV14z4y1N7pg/)
- [SpringBoot3 视频教程从入门到项目实战](https://www.bilibili.com/video/BV1Km4y1k7bn/)
- [尚硅谷 Spring 框架源码级讲解（按需看）](https://www.bilibili.com/video/BV1Vf4y127N5/)

作业：做一个后台管理系统，包含用户/角色/权限、CRUD、Redis 缓存、统一异常处理。

### 阶段 4：工程化与部署（3-4 周）

学习内容：Maven/Gradle、Git、Linux 常用命令、Docker、Nginx、CI/CD。

B 站视频：

- [黑马程序员 Git 全套教程](https://www.bilibili.com/video/BV1MU4y1Y7h5/)
- [黑马程序员 Docker 容器化技术教程](https://www.bilibili.com/video/BV1CJ411T7BK/)
- [Docker 实战教程，docker 入门到大神](https://www.bilibili.com/video/BV1gr4y1U7CY/)

作业：把阶段 3 的项目用 Docker 部署到云服务器，并用 GitHub Actions 或 Gitee Go 配置一条简单流水线。

### 阶段 5：并发、JVM、算法（持续 4-6 周）

学习内容：JUC、线程池、AQS、锁；JVM 内存模型、GC、调优、OOM 排查；数据结构与算法系统过一遍。

B 站视频：

- [黑马程序员 JUC 并发编程全套教程](https://www.bilibili.com/video/BV16J411h7Rd/)
- [尚硅谷 JVM 全套教程](https://www.bilibili.com/video/BV1PJ411n7xZ/)
- [黑马程序员数据结构与算法教程](https://www.bilibili.com/video/BV1Cz411B7qd/)
- [尚硅谷数据结构与算法（Java）](https://www.bilibili.com/video/BV1E4411H73v/)

作业：手写线程池、生产者消费者；用 jstack/jmap 分析一次 OOM；算法每天 1-2 道题。

### 阶段 6：微服务与分布式（2-3 个月）

学习内容：Spring Cloud Alibaba（Nacos、Gateway、OpenFeign、Sentinel、Seata）；消息队列 RocketMQ；Elasticsearch 搜索；分布式锁、幂等、分布式事务、链路追踪。

B 站视频：

- [尚硅谷 SpringCloud + SpringCloudAlibaba 微服务教程](https://www.bilibili.com/video/BV18E411x7eT/)
- [尚硅谷 SpringCloud 入门到大牛](https://www.bilibili.com/video/BV1UJc2ezEFU/)
- [尚硅谷 Java 项目《尚品甄选》](https://www.bilibili.com/video/BV1NF411S7DS/)
- [黑马程序员 RocketMQ 系统精讲](https://www.bilibili.com/video/BV1L4411y7mn/)
- [黑马 Elasticsearch 实战教程](https://www.bilibili.com/video/BV1Dv421v7QZ/)

作业：完成一个商城或订单类的微服务项目，覆盖注册发现、网关、熔断限流、消息异步、搜索。

### 阶段 7：AI 时代 Java 新能力（2 个月入门，之后持续迭代）

学习顺序：

1. 大模型基础：Token、Prompt、Function Calling、流式输出 SSE、幻觉与上下文窗口。
2. Java AI 框架：先学 Spring AI 或 LangChain4j 其中一个，再补另一个。
3. RAG：Embedding、向量数据库（Milvus / Qdrant / pgvector）、文档切分、召回与重排。
4. Agent / MCP：工具调用、Agent 编排、MCP 协议。
5. AI 工程化：API Key 管理、缓存、限流、成本控制、可观测、内容安全。
6. 实战项目：知识库问答、AI 客服、代码评审 Agent、报表生成。

B 站视频：

- [超浓缩 Spring AI 基础教程](https://www.bilibili.com/video/BV1wb3XzeERN/)
- [LangChain4J 教程，入门到精通](https://www.bilibili.com/video/BV1mX3NzrEu6/)
- [LangChain4j 实战教程（保姆级，代码开源）](https://www.bilibili.com/video/BV1X4GGziEyr/)
- [2026 最新版 LangChain4j 零基础入门到项目实战](https://www.bilibili.com/video/BV1tdum6kEyq/)
- [Java 后端转大模型应用开发：LangChain + LangGraph RAG Agent 实战](https://www.bilibili.com/video/BV1K4ub6UEAQ/)

练习建议：

- 用 DeepSeek / OpenAI / Qwen 的 OpenAI 兼容接口，写一个 Spring Boot 流式聊天接口。
- 做一个基于 Spring AI 或 LangChain4j 的知识库问答系统。
- 做一个 Function Calling / MCP 工具，例如查天气、查库存、执行代码。
- 再做一个 Agent：自动生成周报、Review 代码、处理工单。

### 阶段 8：项目与求职（1-2 个月打磨）

- 简历放两个项目：1 个微服务业务项目 + 1 个 AI 应用项目。
- 八股文按 Java 并发、JVM、MySQL、Redis、Spring、分布式顺序复习。
- 算法坚持每天 1-2 道，面试前总量达到 150-200 道。
- 准备系统设计题：高并发下单、RAG 问答架构、AI Agent 架构。
- 把学习笔记和项目总结写成博客，面试时是很好的加分项。

## 三、AI 时代避坑建议

- 不要只学 AI 框架不学后端基础，Spring AI / LangChain4j 底层还是 Java、HTTP、JSON、线程池。
- 不要只看视频不动手，每个视频结束后都要写对应 demo。
- 用 AI 辅助而不是代写，核心代码、项目架构和排查问题的能力才是竞争力。
- 关注官方更新：Spring AI、LangChain4j、MCP 协议、Java LTS（21/25）、虚拟线程、GraalVM。

## 四、快速路线图

Java 基础 → MySQL/Redis → Spring Boot → 工程化部署 → 并发/JVM/算法 → 微服务 → Spring AI / LangChain4j + RAG + Agent → 项目打磨与求职。
