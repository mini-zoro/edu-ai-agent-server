# AAServer - Django REST API 服务器

## 项目简介

AAServer 是一个基于 Django 和 Django REST Framework 构建的 REST API 服务器，主要用于用户认证和权限管理系统。该项目采用现代化的 Web 开发技术栈，提供安全可靠的用户管理功能。

## 功能特性

- 🔐 **用户认证系统** - 基于 Token 的身份验证
- 👥 **多角色用户管理** - 支持管理员、教师、学生三种用户类型
- 🛡️ **安全机制** - 密码加盐存储，逻辑删除
- 🌐 **RESTful API** - 标准的 REST API 接口
- 📱 **跨平台支持** - 支持 Web 和移动端应用
- 🗄️ **数据库支持** - 支持 MySQL 数据库
- ⚡ **高性能** - 集成 Redis 缓存

## 技术栈

- **后端框架**: Django 5.2.4
- **API 框架**: Django REST Framework 3.16.0
- **数据库**: MySQL
- **缓存**: Redis
- **认证方式**: Token Authentication
- **Python 版本**: 3.13+

## 项目结构

```
AAServer/
├── AAServer/                 # Django 项目主配置
│   ├── __init__.py
│   ├── asgi.py              # ASGI 配置
│   ├── settings.py           # Django 设置
│   ├── urls.py              # 主 URL 配置
│   ├── utils.py             # 工具函数
│   └── wsgi.py              # WSGI 配置
├── authentication/           # 用户认证应用
│   ├── __init__.py
│   ├── admin.py             # 管理后台配置
│   ├── apps.py              # 应用配置
│   ├── migrations/          # 数据库迁移文件
│   ├── models.py            # 数据模型
│   ├── tests.py             # 测试文件
│   └── views.py             # 视图函数
├── find_null.py             # 工具脚本
├── manage.py                # Django 管理脚本
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明文档
```

## 安装说明

### 环境要求

- Python 3.13+
- MySQL 5.7+
- Redis 6.0+

### 安装步骤

1. **克隆项目**

   ```bash
   git clone <repository-url>
   cd AAServer
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**

   - 创建 MySQL 数据库
   - 修改 `AAServer/settings.py` 中的数据库配置

5. **运行数据库迁移**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **创建超级用户**

   ```bash
   python manage.py createsuperuser
   ```

7. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```
