"""视图（View）—— 接收请求、处理数据、返回响应。

本文件用「函数视图」（FBV）写法，最直白好懂；
等熟悉了可以再了解 Django 自带的「类视图」（CBV，如 ListView / DetailView）。
"""

from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Choice, Question


def index(request):
    """首页：列出所有已发布的投票问题。"""
    # QuerySet 就是「还没执行的 SQL 查询」，这里用 annotate 顺便统计每个问题有几个选项
    latest_question_list = (
        Question.objects.filter(pub_date__lte=timezone.now())
        .annotate(choice_count=Count('choices'))
    )
    context = {'latest_question_list': latest_question_list}
    # render 会把 context 塞进模板，生成最终 HTML
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """问题详情页：显示问题 + 所有选项（投票表单）。"""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """结果页：显示每个选项的票数和占比。"""
    question = get_object_or_404(Question, pk=question_id)
    choices = list(question.choices.all())
    total = sum(choice.votes for choice in choices)
    # 在视图里算好百分比，模板只负责显示，逻辑和展示分开
    results_data = [
        {
            'choice': choice,
            'percent': round(choice.votes * 100 / total) if total else 0,
        }
        for choice in choices
    ]
    context = {'question': question, 'results': results_data, 'total': total}
    return render(request, 'polls/results.html', context)


@require_POST  # 只允许 POST 请求，用 GET 访问会直接返回 405，防止误操作
def vote(request, question_id):
    """处理投票表单提交。"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        # request.POST 里拿表单提交的选项 id
        selected_choice = question.choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 用户没选就点了投票：回到详情页并提示
        return render(
            request,
            'polls/detail.html',
            {'question': question, 'error_message': '你还没有选择任何选项哦～'},
        )
    selected_choice.votes += 1
    selected_choice.save()
    # 投完票重定向到结果页（PRG 模式：Post-Redirect-Get），刷新页面不会重复投票
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
