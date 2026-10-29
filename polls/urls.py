"""polls 应用的 URL 路由。

注意：这里用 app_name 给路由「命名空间」，配合模板里的 {% url 'polls:index' %}。
"""

from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    # 首页：http://127.0.0.1:8000/polls/
    path('', views.index, name='index'),
    # 详情页：http://127.0.0.1:8000/polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # 结果页：http://127.0.0.1:8000/polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # 投票：POST 到 http://127.0.0.1:8000/polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
