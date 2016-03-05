from django.contrib import admin
from .models import Blog

from dj_markdown.widgets import CodeMirror
from dj_markdown.models import MarkdownField


@admin.register(Blog)
class ProfileAdmin(admin.ModelAdmin):
    formfield_overrides = {
        MarkdownField: {
            'widget': CodeMirror(
                mode='gfm',
                addons=['mode/overlay'],
                theme='light',
                theme_path='dj_markdown/light.css',
                options={
                    'lineNumbers': True,
                    'matchBrackets': True,
                    'viewportMargin': float('inf'),
                },
                additional_modes=['markdown', 'python', 'javascript'],
                js_var_format='editor_%s'
            )
        }
    }
