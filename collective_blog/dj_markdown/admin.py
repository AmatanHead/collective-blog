from django.contrib import admin

from dj_markdown.models import MarkdownField
from dj_markdown.widgets import CodeMirror


class MarkdownAdmin(admin.ModelAdmin):
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
