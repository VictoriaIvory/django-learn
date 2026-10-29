"""数据模型（Model）—— Django 的 MVT 里的 M。

一个模型类 = 数据库里一张表；一个字段 = 表里一列。
写完这里不用手写 SQL，执行 `python manage.py makemigrations` + `migrate`
Django 会自动生成建表语句。
"""

import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """一个问题（投票主题）。"""

    question_text = models.CharField('问题内容', max_length=200)
    pub_date = models.DateTimeField('发布时间')

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['-pub_date']  # 默认按发布时间倒序，最新的在最前面

    def __str__(self):
        # 后台和 shell 里打印对象时显示的内容
        return self.question_text

    def was_published_recently(self):
        """是否 24 小时内发布（官方教程的示例方法，演示模型里也能写业务逻辑）。"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """一个选项，挂在某个问题下面。"""

    # 外键：一个 Question 对应多个 Choice，on_delete=CASCADE 表示问题删了选项跟着删
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',  # 之后可以用 question.choices.all() 拿到所有选项
        verbose_name='所属问题',
    )
    choice_text = models.CharField('选项内容', max_length=200)
    votes = models.IntegerField('得票数', default=0)

    class Meta:
        verbose_name = '选项'
        verbose_name_plural = '选项'

    def __str__(self):
        return self.choice_text
