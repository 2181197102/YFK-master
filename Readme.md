## 目录结构

```
YFK-master/
├── app.py                     # app入口
├── config.py                  # 配置文件，与.env文件配合使用
├── .env                       # 本地环境变量，禁止上传
├── db_test_and_init.py        # 数据库测试与初始化文件
├── requirements.txt           # 依赖文件
├── initial_data/              # 新增的初始数据文件夹
│   ├── users.py               # 存放用户初始数据
│   ├── roles.py               # 存放角色初始数据
│   └── ...                    # 其他表的初始数据文件
├── models/
│   └──__init__.py			  # 各个服务的数据库模型注册文件
├──modules/
│	├── auth/
│	│   ├── routes.py              # 认证服务
│	│   ├── decorator.py           # 角色权限装饰器
│	│   └── models.py              # 认证服务的模型
│	├── user_management/
│	│   ├── routes.py              # 用户管理服务
│	│   └── models.py              # 用户管理的模型
│	├── data_management/
│	│   ├── routes.py              # 数据管理服务
│	│   └── models.py              # 数据管理的模型
├── utils/
│   └── extensions.py          # 存放各种扩展（如 db, jwt）的实例
└── venv/
```



## 快速开始

### 1.将项目克隆到本地

```
git clone https://github.com/2181197102/YFK-master.git
```

### 2.配置环境

建议使用conda虚拟环境进行配置，python基础版本：**3.10.18**

安装依赖文件：

```
pip install -r requirements.txt
```

### 3.修改.env文件

在本地该项目的根目录下创建.env文件，**注意，在推送代码时，请勿将.env文件推送至线上仓库**。

修改其中的关键配置信息，如数据库ip，端口，密钥等。

### 4.创建数据库

数据库使用mysql，版本不限制，当前使用的是**8.0.28**

在mysql中创建**medical_system**数据库

### 5.初始化数据库

运行项目根目录下的**db_test_and_init.py**脚本，测试数据库连接情况，并进行表的创建、初始数据的插入

```
python db_test_and_init.py
```

### 6.启动项目

```
python app.py
```



## 服务测试

建议使用postman进行测试

### 1.测试服务是否正常启动

```
请求方法：GET
请求地址：http://127.0.0.1:7878/health

```

正常返回内容：

```
{
  "message": "Medical System API is running",
  "status": "healthy"
}
```

### 2.登录测试

```
请求方法：POST
请求地址：http://127.0.0.1:7878/api/auth/login
```

请求头(Headers)中增加：

```
Name：Content-Type
key：application/json
```

请求体(Body)中选择raw,然后填充内容：

```
{
    "username": "admin",
    "password": "adminpass"
}
```

正常返回内容：

```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0OTgzNzYzMiwianRpIjoiOWU3YzQ0ZmQtMjhmYy00NTBjLWIwMDctYmZkNzE4ZTAzMjViIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDk4Mzc2MzIsImV4cCI6MTc0OTkyNDAzMiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGVfY29kZSI6IkFETUlOIiwiZ3JvdXBfbmFtZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OFx1NmQ0Ylx1OGJkNVx1NTMzYlx1OTY2MiJ9.PFfQjJMaA31xRk-9YOX1wF_koic3BMU74DE9bj7O3-A",
  "user": {
    "age": 30,
    "gender": "M",
    "group_name": "管理员测试医院",
    "id": 1,
    "name": "系统管理员",
    "role_code": "ADMIN",
    "role_name": "管理员",
    "username": "admin"
  }
}
```
