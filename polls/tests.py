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

    def test_index_shows_total_votes(self):
        """首页每题显示总票数（annotate 算出来的）。"""
        question = self.create_question('今天吃什么？')
        Choice.objects.create(question=question, choice_text='火锅', votes=3)
        Choice.objects.create(question=question, choice_text='烧烤', votes=1)

        response = self.client.get(reverse('polls:index'))

        self.assertContains(response, '4 票')

    def test_results_shows_leading_choice(self):
        """结果页标出票数最高的选项。"""
        question = self.create_question('今天吃什么？')
        Choice.objects.create(question=question, choice_text='火锅', votes=3)
        Choice.objects.create(question=question, choice_text='烧烤', votes=1)

        response = self.client.get(reverse('polls:results', args=(question.id,)))

        self.assertContains(response, '目前领先')
        self.assertContains(response, '火锅')

    def test_results_with_no_votes_does_not_crash(self):
        """一票都没有时不能 500，也不能瞎标领先项。"""
        question = self.create_question('还没人投的题')
        Choice.objects.create(question=question, choice_text='A')
        Choice.objects.create(question=question, choice_text='B')

        response = self.client.get(reverse('polls:results', args=(question.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '还没有人投票')
        self.assertNotContains(response, '目前领先')

    def test_results_has_pie_chart_with_correct_segments(self):
        """饼图两段应该是 75% 和 25%，第二段从 75% 处开始。"""
        question = self.create_question('今天吃什么？')
        Choice.objects.create(question=question, choice_text='火锅', votes=3)
        Choice.objects.create(question=question, choice_text='烧烤', votes=1)

        response = self.client.get(reverse('polls:results', args=(question.id,)))

        self.assertContains(response, 'class="pie"')
        self.assertContains(response, 'pathLength="100"')
        # 模板注释不能漏到页面上（多行 {# #} 不会被当成注释，得用 {% comment %}）
        self.assertNotContains(response, '{#')
        # 第一段：长度 75%，从 0 开始
        self.assertContains(response, 'stroke-dasharray="75.0 100"')
        self.assertContains(response, 'stroke-dashoffset="-0.0"')
        # 第二段：长度 25%，从 75% 开始
        self.assertContains(response, 'stroke-dasharray="25.0 100"')
        self.assertContains(response, 'stroke-dashoffset="-75.0"')

    def test_no_pie_chart_when_nobody_voted(self):
        """0 票时不画饼图，避免出现一个全灰的圆。"""
        question = self.create_question('还没人投的题')
        Choice.objects.create(question=question, choice_text='A')

        response = self.client.get(reverse('polls:results', args=(question.id,)))

        self.assertNotContains(response, 'class="pie"')
        self.assertContains(response, '还没有人投票')


class CreateQuestionTests(TestCase):
    """在网页上创建投票（不经过 admin）。"""

    def test_create_page_renders(self):
        response = self.client.get(reverse('polls:create_question'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '创建一个投票')

    def test_create_question_with_two_choices(self):
        response = self.client.post(reverse('polls:create_question'), {
            'question_text': '新的问题',
            'choice_1': '选项 A',
            'choice_2': '选项 B',
            'choice_3': '',
            'choice_4': '',
        })

        question = Question.objects.get(question_text='新的问题')
        # 创建成功后应该跳到详情页，可以马上投票
        self.assertRedirects(
            response, reverse('polls:detail', args=(question.id,))
        )
        self.assertEqual(question.choices.count(), 2)
        # 发布时间由服务器补上，不能是 None
        self.assertIsNotNone(question.pub_date)

    def test_create_question_requires_two_choices(self):
        response = self.client.post(reverse('polls:create_question'), {
            'question_text': '选项不够的题',
            'choice_1': '只有一个',
            'choice_2': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '至少要填两个选项')
        self.assertFalse(
            Question.objects.filter(question_text='选项不够的题').exists()
        )
