1. ### 权限验证机制

1. #### 权限验证模型设计

1. 权限类型
   1. 页面权限（**page**）：由前端鉴权。表示用户对于一个页面的访问权限。
   2. 接口权限（**api**）：由后端鉴权。表示用户对于一个接口的访问权限。
   3. 按钮权限（**btn**）：由前端鉴权。表示用户对于一个按钮的可视权限。

> 目前系统设计中仅需要页面、接口权限，如需按钮级别权限可随时引入。

1. 权限码格式

权限码由`权限类型` 、`用户类型`、`权限码`组成，其中权限码由`权限基本码`及`请求方式（权限类型为api时使用）`组成，通过字符“:”进行分割。

**用户类型**是**必不可少**的，用于标记哪些权限是对应用户类型的默认权限，系统在添加用户时会自动添加**默认权限**给**默认角色**，该过程就需要通过权限码中的**用户类型**部分进行判断。用户类型如下：

- **common**：通用模块（管理类模块），默认管理员可访问，教师可被分配权限后访问
- **teacher**：教师用户门户模块，默认管理员、教师可访问，学生不可访问
- **student**：学生用户门户模块，默认仅学生可访问，管理员、教师不可访问

示例：

```Plain
// 1. 使用用户类型的权限码，默认表示可以随意分配给教师或管理员用户
api:common:base:student:get // 表示学生信息管理页面GET请求的接口访问权限
page:common:workbench // 表示教师/管理员系统工作台页面访问权限

// 2. 使用用户类型的权限码，默认表示该页面仅可对应用户类型进行访问
page:teacher:course // 表示教师用户对课程页面的访问权限
```

1. #### 配置后端权限验证

后端需要验证**接口权限**，即**权限码以****`api`****开头**的权限。权限验证框架已搭建完成，仅需在需要权限验证的接口的**`urls.py`**文件中进行配置即可。 

1. 编写好视图函数，并配置好路由文件`urls.py`；
2. 在`urls.py`中需要鉴权的路由后添加`kwargs={PERMISSION_KEY: '你的权限码'}`。仅需替换该代码中的“你的权限码”即可，其他的无需修改。
3. 系统会在接收到请求时，自动校验用户是否拥有权限`api:你的权限码:请求方法`，如：`api:code:get`
4. 当访问的用户所拥有的权限中没有所需的权限码，系统会自动响应：

```JSON
{
    "code":"205",
    "msg":"当前用户无权限访问",
    "data":null
}
```

示例：

```Python
from django.urls import path

import apps.code_dict.views
from apps.code_dict.views import CodeView
from apps.rbac.constants import PERMISSION_KEY

urlpatterns = [
    path('', CodeView.as_view(), kwargs={PERMISSION_KEY: 'code'}), # 需要权限：api:code:get、api:code:post...权限才可访问
    path('/options/<str:type_name>', apps.code_dict.views.get_options, kwargs={PERMISSION_KEY: 'code:options'}),
    path('/type', apps.code_dict.views.get_code_type), # 不配置则不需要鉴权（除登录接口外，其他接口不推荐！！！）
]
```

1. #### 配置Web前端权限验证

当前Web前端需要验证**页面权限**，即**权限码以****`page`****开头**的权限。权限验证框架已搭建完成，仅需在需要权限验证的页面路由，即**`route.ts`**文件中进行配置即可。 

1. 编写好页面文件，并在`route.ts`中配置相应的路由；
2. 添加配置项`perm`，访问该页面所需权限的**完整权限码**，如：`page:teacher:agent`
3. 若需跳过鉴权，则添加`requireAuth: false`配置项**（目前所有不需要鉴权的页面均已配置完成，接下来开发的所有页面默认情况下均不跳过鉴权）**

示例：

```TypeScript
// route.ts
{
    name: "ResourceManage",
    path: "/sys/resource",
    component: () => import("./resource-manage/index.vue"),
    meta: {
        title: "资源管理",
        icon: markRaw(AttachFileFilled),
        perm: ["page:common:base:student"],// 在这里配置完整权限码，可配置多个（如需要）
        order: 1,
    },
    children:[...]
},
```

1. #### 开发过程中的权限添加（**重要！！！**）

在项目正常运行中，不支持用户自行对权限进行管理。权限需要开发人员在项目开发阶段就预添加完成，即在实现每一个页面或接口时，就将对应的权限添加到数据库中，以供系统运行使用，**否则新开发的页面或接口无法被访问！** 系统的权限应由后端同学负责维护：

添加方法：

1. 使用终端工具进入**后端**项目根目录；

```Shell
cd ./edu_ai_agent_server
```

1. 执行权限添加命令

```Shell
# 1. 创建顶级权限
python manage.py add_perm --key page:article --name 文章管理 --type 0 --des 文章页面权限

# 2. 创建子权限
python manage.py add_perm --key api:article.delete --name 删除文章 --type 1 --parent article --des 删除接口文章
```

其中的参数分别为：

| 变量名 | 说明                                           | 数据类型     | 必须 |
| :----- | :--------------------------------------------- | :----------- | :--- |
| key    | 权限码                                         | 字符串       | √    |
| name   | 权限名                                         | 字符串       | √    |
| type   | 权限类型（0-页面权限，1-接口权限，2-按钮权限） | 整型         | √    |
| parent | 父级节点ID或权限码（key），若有则必需。        | 整型或字符串 | ×    |

执行后控制台输出：`已创建 权限：article -> "文章管理"`则表示权限添加成功。