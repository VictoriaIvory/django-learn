"""视图（View）—— 接收请求、处理数据、返回响应。

本文件用「函数视图」（FBV）写法，最直白好懂；
等熟悉了可以再了解 Django 自带的「类视图」（CBV，如 ListView / DetailView）。
"""

from django.db.models import Count, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import QuestionCreateForm
from .models import Choice, Question


def index(request):
    """首页：列出所有已发布的投票问题。"""
    # QuerySet 就是「还没执行的 SQL 查询」。
    # annotate 会在查询里顺手算出两个统计值，避免在模板里一个个数：
    #   choice_count —— 这题有几个选项
    #   total_votes  —— 这题一共收了多少票
    latest_question_list = (
        Question.objects.filter(pub_date__lte=timezone.now())
        .annotate(
            choice_count=Count('choices'),
            total_votes=Sum('choices__votes'),
        )
    )
    context = {'latest_question_list': latest_question_list}
    # render 会把 context 塞进模板，生成最终 HTML
    return render(request, 'polls/index.html', context)


def create_question(request):
    """在网页上创建一个投票（不用进 admin 后台）。

    GET  → 显示空表单
    POST → 校验通过后建 Question 和若干 Choice，然后跳到详情页去投票
    """
    if request.method == 'POST':
        form = QuestionCreateForm(request.POST)
        if form.is_valid():
            # commit=False：先别写库，因为还要补 pub_date
            question = form.save(commit=False)
            question.pub_date = timezone.now()  # 发布时间由服务器决定
            question.save()

            # related_name='choices' 让我们能直接 question.choices.create(...)
            for text in form.choice_texts():
                question.choices.create(choice_text=text)

            return HttpResponseRedirect(
                reverse('polls:detail', args=(question.id,))
            )
    else:
        form = QuestionCreateForm()

    return render(request, 'polls/create.html', {'form': form})


def detail(request, question_id):
    """问题详情页：显示问题 + 所有选项（投票表单）。"""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """结果页：显示每个选项的票数、占比，以及当前领先项。"""
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
    # 领先项：只有真的有人投过才显示（total 为 0 时 max() 没有意义）
    leading = max(choices, key=lambda c: c.votes) if total else None
    context = {
        'question': question,
        'results': results_data,
        'total': total,
        'leading': leading,
    }
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
