"""表单。

用 ModelForm 让 Django 根据模型自动生成字段和校验规则，
我们只额外补三件事：
  1. 加几个「选项」输入框（它们不是 Question 的字段，是给 Choice 用的）
  2. 自定义校验：至少要两个选项，否则投票没意义
  3. 提供 choice_texts()，让视图直接拿到填了的选项
"""

from django import forms

from .models import Question


class QuestionCreateForm(forms.ModelForm):
    """创建投票：一个问题 + 最多 4 个选项。"""

    choice_1 = forms.CharField(label='选项 1', max_length=200)
    choice_2 = forms.CharField(label='选项 2', max_length=200)
    # 3、4 可以不填；required=False 就是允许留空
    choice_3 = forms.CharField(label='选项 3', max_length=200, required=False)
    choice_4 = forms.CharField(label='选项 4', max_length=200, required=False)

    class Meta:
        model = Question
        fields = ['question_text']
        labels = {'question_text': '问题'}
        widgets = {
            'question_text': forms.TextInput(
                attrs={'placeholder': '例如：周末去哪里团建？'}
            ),
        }

    def clean(self):
        """整体校验：不能只填一个选项。"""
        cleaned = super().clean()
        filled = [
            cleaned.get('choice_%d' % index)
            for index in range(1, 5)
            if cleaned.get('choice_%d' % index)
        ]
        if len(filled) < 2:
            raise forms.ValidationError('至少要填两个选项，不然投票没有意义。')
        return cleaned

    def choice_texts(self):
        """把用户填了的选项按顺序取出来，给视图批量创建 Choice 用。"""
        return [
            self.cleaned_data['choice_%d' % index]
            for index in range(1, 5)
            if self.cleaned_data.get('choice_%d' % index)
        ]
