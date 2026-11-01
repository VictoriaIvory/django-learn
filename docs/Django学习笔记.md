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

---

## 13. 本周新增的四块（教程里没有的）

### 13.1 ModelForm：在网页上创建投票

以前只能在 admin 里建题，现在用户自己就能建。核心是 `polls/forms.py`：

```python
class QuestionCreateForm(forms.ModelForm):
    choice_1 = forms.CharField(label='选项 1', max_length=200)
    choice_2 = forms.CharField(label='选项 2', max_length=200)
    choice_3 = forms.CharField(label='选项 3', max_length=200, required=False)

    class Meta:
        model = Question
        fields = ['question_text']
```

要点：

- `ModelForm` 按模型自动生成字段和校验，不用手写 `<input>`
- 额外的 `choice_1/2/3` 不是 `Question` 的字段，是给 `Choice` 用的，所以单独声明
- `required=False` 表示可留空（选项 3、4）

**整体校验写在 `clean()` 里**——单字段校验用 `clean_<字段名>`，跨字段的用 `clean()`：

```python
def clean(self):
    cleaned = super().clean()
    filled = [cleaned.get('choice_%d' % i) for i in range(1, 5) if cleaned.get('choice_%d' % i)]
    if len(filled) < 2:
        raise forms.ValidationError('至少要填两个选项，不然投票没有意义。')
    return cleaned
```

**视图里为什么要 `commit=False`**：

```python
question = form.save(commit=False)   # 先拿到对象，但不写库
question.pub_date = timezone.now()   # 补上表单里没有的字段
question.save()                      # 现在才 INSERT
```

因为 `pub_date` 不该让用户填（用户能随便改发布时间就不对了），所以表单里没有它，
必须 `commit=False` 补上再存。

### 13.2 annotate：让数据库帮你统计

首页要显示「每题有几个选项、一共多少票」。笨办法是循环里一条条查，会查 N+1 次。
正确做法是一次查询算完：

```python
Question.objects.filter(pub_date__lte=timezone.now()).annotate(
    choice_count=Count('choices'),
    total_votes=Sum('choices__votes'),
)
```

它翻译成 SQL 的 `COUNT()` 和 `SUM()` 配合 `GROUP BY`，**所有统计在数据库里完成**，
Python 只拿到结果。模板里直接 `{{ question.total_votes }}` 就行。

> 注意：`Count` 和 `Sum` 作用在**同一个**关联表上是安全的；如果作用在两个不同的
> 多对多/外键关系上，会产生笛卡尔积导致数字翻倍，那时要用 `distinct=True`。

### 13.3 SVG 饼图：不引图表库

结果页的环形图是纯 SVG 画的，没有任何 JS 依赖。原理只有一个：

```html
<circle pathLength="100"
        stroke-dasharray="60 100"
        stroke-dashoffset="-0" />
```

- `pathLength="100"` 把圆周长度**归一成 100**，于是 `stroke-dasharray` 可以直接写百分比
- `stroke-dasharray="60 100"` = 画 60 份实线、100 份空白 → 一段 60% 的弧
- `stroke-dashoffset="−起点"` 让这段弧从圆周的某个位置开始

**视图负责算两个数**：

```python
running = 0.0
for choice in choices:
    ratio = choice.votes / total
    pie_len = round(ratio * 100, 3)      # 弧长
    pie_start = round(running * 100, 3)  # 起点 = 前面所有选项占比之和
    running += ratio
```

> 起点要用「累积比」算，不能把「上一个选项的百分比」直接相加——四舍五入会让
> 最后一段接不上、留一道缝。

**踩过的坑**：`{# 注释 #}` 在 Django 里**只支持单行**。写成多行不会被当注释，
会原样输出到页面上。多行注释要用 `{% comment %}...{% endcomment %}`。

### 13.4 ALLOWED_HOSTS：为什么手机连不上

现象：本机能开，手机输入电脑 IP 却报 400 / `DisallowedHost`。

原因有两层，缺一不可：

1. `runserver` 默认只监听 `127.0.0.1`（只有本机能连）→ 要改成 `0.0.0.0`
2. Django 的 `ALLOWED_HOSTS` 只认白名单里的 Host → 要把手机访问用的 IP 加进去

**第二层是故意的安全设计**（防 Host 头攻击），不是 bug。光改 `0.0.0.0` 没用。

本项目的做法：`.env` 里设 `DJANGO_ALLOW_LAN=True`，`settings.py` 用
`socket` 探测本机当前出网 IP 并自动加进 `ALLOWED_HOSTS`，换网络不用手改：

```python
if os.environ.get('DJANGO_ALLOW_LAN', '').lower() in ('1', 'true', 'yes', 'on'):
    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _sock.connect(('8.8.8.8', 80))      # UDP 不真的发包，只是让系统选一张网卡
    _lan_ip = _sock.getsockname()[0]
    ALLOWED_HOSTS.append(_lan_ip)
```

---

## 14. 补充自测题（这周新增的）

9. `ModelForm` 的 `commit=False` 到底「不做」什么？什么时候必须用它？
10. `annotate(Count(...))` 比在 Python 里循环统计好在哪？
11. 饼图里 `pathLength="100"` 起了什么作用？
12. `{# #}` 和 `{% comment %}` 有什么区别？
13. 为什么把 `runserver` 改成 `0.0.0.0` 之后，手机还是打不开？

<details>
<summary>参考答案</summary>

9. 不写数据库。表单里缺少必填字段（如 `pub_date`）时，必须先拿到对象补上再 `save()`。
10. 一条 SQL 在数据库里算完，避免 N+1 查询；数据量大时差距明显。
11. 把圆周长度归一成 100 份，于是 `stroke-dasharray` 可以直接写百分比，不用算三角函数。
12. `{# #}` 只能单行，多行会漏到页面上；`{% comment %}` 支持多行。
13. 因为 `ALLOWED_HOSTS` 只认白名单，还要把手机访问用的 IP 加进去（防 Host 头攻击）。

</details>
