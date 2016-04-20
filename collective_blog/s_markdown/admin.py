from s_markdown.models import MarkdownField
from s_markdown.widgets import CodeMirror


class MarkdownAdmin(object):
    """Mixin that fixes markdown widgets"""
    formfield_overrides = {
        MarkdownField: {
            'widget': CodeMirror(
                mode='gfm',
                addons=['mode/overlay'],
                theme='light',
                theme_path='s_markdown/light.css',
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
