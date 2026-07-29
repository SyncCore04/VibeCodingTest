# 用户管理系统 (User Management System)

前后端分离架构：SpringBoot + MyBatis-Plus 后端 + 原生 HTML/CSS/JS 前端。

---

## 项目结构

```
user-manage/          ← 后端 SpringBoot Maven 工程
├── pom.xml
└── src/main/
    ├── resources/
    │   ├── application.yml      # 数据源 & MyBatis-Plus 配置
    │   └── schema.sql           # 建表 SQL
    └── java/com/example/usermanage/
        ├── UserManageApplication.java        # 启动类
        ├── entity/User.java                  # 实体 (逻辑删除 + JSR校验)
        ├── mapper/UserMapper.java            # Mapper
        ├── service/UserService.java          # Service 接口
        ├── service/impl/UserServiceImpl.java # Service 实现 (分页查询)
        ├── controller/UserController.java    # REST 接口
        ├── config/MyBatisPlusConfig.java     # 分页插件 + 自动填充
        └── common/
            ├── Result.java                   # 统一响应体
            └── GlobalExceptionHandler.java    # 全局异常处理

frontend/             ← 前端静态文件
├── index.html        # 页面结构
├── css/style.css     # 样式
└── js/app.js         # 交互逻辑 (自动检测后端, 无后端时Mock运行)
```

---

## 后端启动

### 1. 环境要求
- JDK 8+
- Maven 3.6+
- MySQL 8.0+

### 2. 创建数据库
```bash
mysql -u root -p < user-manage/src/main/resources/schema.sql
```

### 3. 修改配置
编辑 `user-manage/src/main/resources/application.yml`，修改数据库连接信息：
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/user_manage?...&serverTimezone=Asia/Shanghai
    username: root
    password: 你的密码
```

### 4. 启动
```bash
cd user-manage
mvn spring-boot:run
```
启动后访问 http://localhost:8080/api/users?page=1&size=10 确认接口可用。

---

## 前端运行

### 方式一：直接打开 (Mock模式)
双击 `frontend/index.html` 即可在浏览器中运行。前端会自动检测后端是否可达：
- 后端不可达 → **Mock 模式**（使用内置模拟数据，15条种子数据）
- 后端可达   → **API 模式**（调用真实后端接口）

### 方式二：搭配后端 (API模式)
先启动后端（确保 8080 端口运行），然后双击 `frontend/index.html`。
前端会在 2 秒内自动检测到后端并切换为 API 模式，右上角角标显示 `API`。

### 方式三：Nginx 部署
```nginx
server {
    listen 80;
    root /path/to/frontend;
    index index.html;
    location /api/ {
        proxy_pass http://localhost:8080;
    }
}
```

---

## API 接口

| 方法     | 路径               | 说明       |
| -------- | ------------------ | ---------- |
| GET      | /api/users?page=1&size=10&keyword=xxx | 分页查询 |
| GET      | /api/users/{id}    | 查询单个   |
| POST     | /api/users         | 新增用户   |
| PUT      | /api/users/{id}    | 更新用户   |
| DELETE   | /api/users/{id}    | 逻辑删除   |

统一响应格式：
```json
{ "code": 200, "message": "success", "data": { "records": [...], "total": 15 } }
```

---

## 核心特性

**后端**
- MyBatis-Plus 逻辑删除 (`deleted` 字段)
- 分页插件 (PaginationInnerInterceptor)
- 创建/更新时间自动填充 (MetaObjectHandler)
- JSR-303 参数校验 (用户名非空, 手机号格式 `1[3-9]\d{9}`)
- 全局异常处理 (友好校验错误提示)

**前端**
- 纯原生实现，零外部依赖
- 自动检测后端 API，智能切换 Mock/API 模式
- 客户端校验 (用户名非空, 手机号格式, 邮箱格式)
- 分页、搜索、新增、编辑、删除
- Toast 提示、模态弹窗、键盘 Esc 关闭
- 响应式适配移动端
