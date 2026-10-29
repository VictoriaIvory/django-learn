"""后台管理（admin）—— Django 自带的最实用功能之一。

注册模型后不用写一行前端代码，就能在 /admin/ 增删改查数据。
"""

from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """在问题编辑页里直接编辑它的选项（内联表单）。"""

    model = Choice
    extra = 3  # 默认多给 3 个空白选项输入框


class QuestionAdmin(admin.ModelAdmin):
    # 字段分组显示，比默认的一长串更好用
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('时间信息', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    # 列表页展示的列
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    list_filter = ['pub_date']
    search_fields = ['question_text']
    date_hierarchy = 'pub_date'


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
