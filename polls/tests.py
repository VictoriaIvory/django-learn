"""自动化测试 —— 用 `python manage.py test` 运行。

测试是「熟悉框架」很重要的一环：改代码后跑一遍，确认没把功能弄坏。
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


class PollsViewsTests(TestCase):
    def create_question(self, text, days=0):
        """辅助方法：造一个指定发布时间的问题。"""
        return Question.objects.create(
            question_text=text,
            pub_date=timezone.now() + timezone.timedelta(days=days),
        )

    def test_index_lists_only_published_questions(self):
        """首页只显示已发布的问题，未来的问题不显示。"""
        self.create_question('过去的问题', days=-1)
        self.create_question('未来的问题', days=1)

        response = self.client.get(reverse('polls:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '过去的问题')
        self.assertNotContains(response, '未来的问题')

    def test_detail_returns_404_for_missing_question(self):
        response = self.client.get(reverse('polls:detail', args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_vote_increments_and_redirects(self):
        question = self.create_question('今天吃什么？')
        choice = Choice.objects.create(question=question, choice_text='火锅')

        response = self.client.post(
            reverse('polls:vote', args=(question.id,)),
            {'choice': choice.id},
        )

        self.assertRedirects(
            response, reverse('polls:results', args=(question.id,))
        )
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

    def test_vote_without_choice_shows_error(self):
        question = self.create_question('今天吃什么？')
        response = self.client.post(reverse('polls:vote', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '你还没有选择任何选项')

    def test_results_page_shows_votes(self):
        question = self.create_question('今天吃什么？')
        Choice.objects.create(question=question, choice_text='火锅', votes=3)
        Choice.objects.create(question=question, choice_text='烧烤', votes=1)

        response = self.client.get(reverse('polls:results', args=(question.id,)))

        self.assertContains(response, '火锅')
        self.assertContains(response, '75%')
