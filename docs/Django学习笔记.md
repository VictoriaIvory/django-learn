# Django 学习笔记（零基础版）

> 配合项目 `django-learn` 阅读。每一条概念都能在项目里找到对应文件，
> 建议边看边打开对应文件对照。

---

## 1. 一次请求的完整旅程

在浏览器输入 `http://127.0.0.1:8000/polls/1/` 后发生了什么？

```text
浏览器
  │  ① 发送 HTTP GET /polls/1/
  ▼
Django 开发服务器 (runserver)
  │  ② 进入总路由 mysite/urls.py
  │     path('polls/', include('polls.urls'))
  ▼
polls/urls.py
  │  ③ 匹配到 path('<int:question_id>/', views.detail, name='detail')
  │     把 1 传给 question_id
  ▼
polls/views.py → detail(request, question_id=1)
  │  ④ get_object_or_404(Question, pk=1)   ← 查数据库
  │  ⑤ render(request, 'polls/detail.html', {'question': question})
  ▼
templates/polls/detail.html
  │  ⑥ 模板引擎把 {{ question.question_text }} 替换成真实值
  ▼
返回 HTML 给浏览器 → 渲染成页面
```

**记住这条链：URL → View → Model/Template → Response。**
面试被问「Django 请求流程」，答这条就够。

---

## 2. MVT 是什么？和 MVC 有什么区别？

| 传统 MVC | Django 的 MVT | 对应文件 |
| --- | --- | --- |
| Model（数据） | **M**odel | `polls/models.py` |
| View（界面） | **T**emplate | `templates/` |
| Controller（逻辑） | **V**iew | `polls/views.py` |

Django 自己承担了「Controller」的角色（路由分发），所以把原先的 View 叫 Template，
把 Controller 叫 View。**本质和 MVC 一样，只是名字换了。**

好处：页面（HTML）和业务逻辑分开，改样式不用碰 Python，改逻辑不用碰 HTML。

---

## 3. 项目（Project）vs 应用（App）

| | Project | App |
| --- | --- | --- |
| 是什么 | 一个网站的整体配置 | 一块可复用的功能 |
| 例子 | `mysite/`（settings、总路由） | `polls/`（投票功能） |
| 数量 | 一个网站一个 | 一个网站可以有很多个（blog、shop…） |

创建命令：

```powershell
django-admin startproject mysite .   # 创建项目（最后的 . 表示建在当前目录）
python manage.py startapp polls      # 创建应用
```

创建后**必须**去 `settings.py` 的 `INSTALLED_APPS` 里登记 `'polls'`，
否则 Django 不会加载它的模型和模板 —— 这是新手第一个大坑。

---

## 4. URL 路由

### 基本写法

```python
urlpatterns = [
    path('polls/', include('polls.urls')),   # 分发给子路由
]
```

```python
# polls/urls.py
app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
]
```

### 路径转换器

| 写法 | 匹配 |
| --- | --- |
| `<int:pk>` | 整数 |
| `<str:slug>` | 不含 `/` 的字符串 |
| `<uuid:id>` | UUID |

### name 与反向解析

给路由起名字后，模板和代码里就不要写死 URL：

```html
<a href="{% url 'polls:detail' question.id %}">详情</a>   <!-- 模板里 -->
```

```python
from django.urls import reverse
reverse('polls:results', args=(1,))   # → '/polls/1/results/'
```

以后改 URL 规则，只改 `urls.py` 一处，全站链接自动跟着变。

---

## 5. 视图（View）

### 函数视图的四步套路

```python
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)  # ① 查数据
    return render(request, 'polls/detail.html', {'question': question})  # ② 渲染返回
```

普通函数视图都长这样：

1. 从 `request` 或 URL 参数里拿输入；
2. 用模型查 / 改数据库；
3. 把数据放进 `context` 字典；
4. `render()` 渲染模板，或 `HttpResponseRedirect()` 跳转。

### request 里有什么

| 属性 | 说明 |
| --- | --- |
| `request.method` | `'GET'` / `'POST'` |
| `request.GET` | URL 问号后面的参数 |
| `request.POST` | 表单提交的数据 |
| `request.user` | 当前登录用户 |

### 两种返回方式

```python
return render(request, 'polls/index.html', context)              # 返回页面
return HttpResponseRedirect(reverse('polls:results', args=(id,))) # 重定向
```

**投票成功后一定要重定向**（PRG 模式：Post → Redirect → Get），
否则用户按 F5 刷新会重复提交一次投票。

---

## 6. 模板（Template）

### 两种语法

| 语法 | 用途 | 例子 |
| --- | --- | --- |
| `{{ 变量 }}` | 输出值 | `{{ question.question_text }}` |
| `{% 标签 %}` | 逻辑 | `{% if %}` `{% for %}` `{% url %}` `{% extends %}` |

### 模板继承（很重要）

```html
<!-- base.html：只写一次 -->
<html>... {% block content %}{% endblock %} ...</html>
```

```html
<!-- 子模板：复用骨架，只填内容 -->
{% extends 'base.html' %}
{% block content %}
  <h1>你好</h1>
{% endblock %}
```

### 三个必背标签

```html
{% load static %}                          <!-- 用静态文件前必须加载 -->
<link rel="stylesheet" href="{% static 'polls/style.css' %}">

{% csrf_token %}                           <!-- 所有 POST 表单必须有，否则 403 -->
```

### 模板找文件的顺序

1. `settings.TEMPLATES['DIRS']` 里的目录（本项目是 `templates/`）
2. 每个 `INSTALLED_APPS` 里的 `app/templates/` 目录

所以模板路径要写全：`'polls/index.html'`，不是 `'index.html'`。

---

## 7. 模型与 ORM

### 定义模型

```python
class Question(models.Model):
    question_text = models.CharField('问题内容', max_length=200)
    pub_date = models.DateTimeField('发布时间')
```

### 常用字段类型

| 字段 | 对应数据库 | 用途 |
| --- | --- | --- |
| `CharField(max_length=)` | VARCHAR | 短文本（必须指定长度） |
| `TextField()` | TEXT | 长文本 |
| `IntegerField()` | INTEGER | 整数 |
| `DateTimeField()` | DATETIME | 日期时间 |
| `BooleanField()` | BOOLEAN | 真假 |
| `ForeignKey(Other, on_delete=...)` | 外键 | 一对多 |
| `EmailField()` / `ImageField()` | VARCHAR | 带校验的文本 |

### 迁移（改模型后必做）

```powershell
python manage.py makemigrations   # 生成迁移文件（模型 → 建表语句）
python manage.py migrate          # 真正执行到数据库
```

记忆：**改了 models.py 就要 makemigrations + migrate**，否则数据库还是旧表结构。

### 常用查询（ORM，不写 SQL）

```python
Question.objects.all()                          # 查全部
Question.objects.get(pk=1)                      # 查一个（找不到会抛异常）
Question.objects.filter(pub_date__lte=now)      # 条件查询（lte = 小于等于）
Question.objects.exclude(...)                   # 排除
Question.objects.order_by('-pub_date')          # 排序，- 表示倒序
Question.objects.count()                        # 计数
Question.objects.annotate(Count('choices'))     # 聚合统计

# 双下划线是 ORM 的魔法
Question.objects.filter(question_text__contains='Django')   # 模糊查询
Question.objects.filter(pub_date__year=2026)                # 按年份
```

### 外键与 related_name

```python
question = models.ForeignKey(Question, on_delete=models.CASCADE,
                             related_name='choices')
```

- `on_delete=models.CASCADE`：问题删了，选项跟着删；
- `related_name='choices'`：反向查询 —— `question.choices.all()` 拿到所有选项。

### QuerySet 是「懒」的

```python
qs = Question.objects.all()   # 此刻没有查数据库！
for q in qs:                  # 用到时才真正执行 SQL
    print(q)
```

---

## 8. 后台管理（admin）

三步走：

1. `admin.site.register(Question)`（已写好）
2. `python manage.py createsuperuser` 创建管理员
3. 访问 `/admin/` 登录，直接增删改查

进阶：`list_display`（列表显示哪些列）、`search_fields`（搜索）、
`list_filter`（筛选）、`inlines`（在问题页面里直接编辑选项）。

---

## 9. 测试

```python
class PollsViewsTests(TestCase):
    def test_vote_increments(self):
        ...
        self.assertEqual(choice.votes, 1)
```

```powershell
python manage.py test        # 跑全部
```

测试的好处：改代码后一条命令确认「没把原来的功能弄坏」。
`TestCase` 每次跑测试都会自动建一个临时数据库，测完销毁，**不碰真实数据**。

---

## 10. 常见报错速查

| 报错 | 原因 | 解决 |
| --- | --- | --- |
| `TemplateDoesNotExist: polls/index.html` | 模板路径不对 / 目录没建 | 确认 `templates/polls/index.html` 存在且 `TEMPLATES['DIRS']` 配了 |
| `ModuleNotFoundError: No module named 'polls'` | 没在 `INSTALLED_APPS` 注册 | 加上 `'polls'` |
| `no such table: polls_question` | 没执行迁移 | `makemigrations` + `migrate` |
| `403 Forbidden (CSRF)` | POST 表单缺 `{% csrf_token %}` | 加上 |
| `DisallowedHost` | `ALLOWED_HOSTS` 没配 | 加上 `127.0.0.1` |
| `That port is already in use` | 8000 端口被占用 | `runserver 8080` 换端口 |
| 「无法加载 Activate.ps1」 | PowerShell 执行策略 | `Set-ExecutionPolicy -Scope Process RemoteSigned` |
| 终端中文乱码 | Windows 控制台默认 GBK | VS Code 终端输入 `chcp 65001`，或用 `$env:PYTHONIOENCODING="utf-8"` |
| 改了 CSS 页面没变 | 浏览器缓存 | `Ctrl + F5` 强制刷新 |
| 改了模型没生效 | 忘了迁移 | `makemigrations` + `migrate` |

---

## 11. 学习路线建议（对照 B 站视频）

视频：**2026版-零基础玩转 Python Django5 项目实战-学完可就业**（知了传课，B 站）

建议这样看，别从第一集开始「匀速」看：

1. **1.5～2 倍速**先跳着看完「环境搭建 + 创建项目」那一节，跟着本项目跑通；
2. 重点看 **模型（ORM）、路由、视图、模板** 四章 —— 这是 Django 的骨架，也是面试必问；
3. 项目实战部分**跟着敲**，不要只看。看会 ≠ 会写；
4. 每学完一章，回来对照本项目对应文件，自己改点东西：
   - 加一个「问题创建页」（表单 + `request.POST`）
   - 给 Question 加 `is_active` 字段，只显示启用的（改模型 → 迁移 → 改查询）
   - 把 admin 列表加上 `list_editable`
5. 官方教程也建议过一遍：<https://docs.djangoproject.com/zh-hans/5.2/intro/tutorial01/>
   （本项目就是官方 tutorial 的加强版）

---

## 12. 自测题（能答出来就算「熟悉框架」）

1. MVT 分别对应哪三个文件？Django 里谁扮演 Controller？
2. 新建 app 后必须做哪一步，Django 才会加载它？
3. `path('<int:question_id>/', ...)` 里的 `int` 起什么作用？
4. 为什么投票提交后要 `HttpResponseRedirect` 而不是直接 `render`？
5. 所有 POST 表单里必须加什么标签？不加会报什么错？
6. `makemigrations` 和 `migrate` 的区别？
7. `related_name` 的作用是什么？
8. `Question.objects.all()` 执行时真的查数据库了吗？

<details>
<summary>参考答案</summary>

1. Model → `models.py`，Template → `templates/`，View → `views.py`；Django 的路由分发相当于 Controller。
2. 在 `settings.INSTALLED_APPS` 里注册。
3. 把 URL 里这一段当整数解析后传给视图，非整数不匹配。
4. PRG 模式：重定向后刷新页面不会重复提交投票（否则刷新会再投一次）。
5. `{% csrf_token %}`；不加会 403 Forbidden。
6. `makemigrations` 把模型变化生成迁移文件，`migrate` 把迁移应用到数据库。
7. 定义外键的反向查询名，如 `question.choices.all()`。
8. 没有。QuerySet 是惰性的，遍历 / 切片 / `len()` 时才真正执行 SQL。

</details>
