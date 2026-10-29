"""自定义管理命令：`python manage.py seed_demo`

作用：一键插入几条演示数据，方便第一次打开页面就能看到内容。
这也是 Django 的常见用法 —— 在 app 里建 management/commands/xxx.py。
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from polls.models import Choice, Question

DEMO_QUESTIONS = [
    (
        '你最喜欢用哪个 Python Web 框架？',
        ['Django', 'Flask', 'FastAPI', '还没想好'],
    ),
    (
        '这个周末打算做什么？',
        ['写作业', '打游戏', '睡觉', '出去玩'],
    ),
    (
        '今天午饭吃什么？',
        ['食堂', '外卖', '泡面', '不吃了'],
    ),
]


class Command(BaseCommand):
    help = '插入投票演示数据'

    def handle(self, *args, **options):
        created = 0
        for text, options_list in DEMO_QUESTIONS:
            question, is_new = Question.objects.get_or_create(
                question_text=text,
                defaults={'pub_date': timezone.now()},
            )
            if not is_new:
                continue
            for option in options_list:
                Choice.objects.create(question=question, choice_text=option)
            created += 1

        if created:
            self.stdout.write(self.style.SUCCESS(f'成功：已创建 {created} 个演示投票'))
        else:
            self.stdout.write(self.style.WARNING('提示：演示数据已存在，未重复创建'))
