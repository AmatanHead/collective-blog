"""
Markdown widgets

"""

from django import forms
from django.utils.safestring import mark_safe

from json import dumps


class MarkdownTextarea(forms.Textarea):
    """
    Basic textarea widget for rendering Markdown objects

    """
    pass


class CodeMirror(MarkdownTextarea):
    """
    Widget that uses the `CodeMirror` editor

    """

    def __init__(self, *args, **kwargs):
        self.mode = kwargs.pop('mode', 'markdown')
        self.addons = kwargs.pop('addons', [])
        self.theme = kwargs.pop('theme', 'default')
        self.theme_path = kwargs.pop('theme_path', 'dj_markdown/codemirror/theme/%s.css' % self.theme)
        self.keymap = kwargs.pop('keymap', None)
        self.options = kwargs.pop('options', {})
        self.additional_modes = kwargs.pop('additional_modes', [])
        self.js_var_format = kwargs.pop('js_var_format', None)

        self.options.update(dict(mode=self.mode, theme=self.theme))

        self.option_json = dumps(self.options)

        super(CodeMirror, self).__init__(*args, **kwargs)

    @property
    def media(self):
        css = ['dj_markdown/codemirror/lib/codemirror.css']
        if self.theme:
            css.append(self.theme_path)
        js = ['dj_markdown/codemirror/lib/codemirror.js']
        js.extend('dj_markdown/codemirror/addon/%s.js' % a for a in self.addons)
        if self.keymap:
            js.append('dj_markdown/codemirror/keymap/%s.js' % self.keymap)
        if self.mode:
            js.append('dj_markdown/codemirror/mode/%s/%s.js' % (self.mode, self.mode))
        for mode in self.additional_modes:
            js.append('dj_markdown/codemirror/mode/%s/%s.js' % (mode, mode))
        return forms.Media(
            css=dict(all=css),
            js=js,
        )

    def render(self, name, value, attrs=None):
        """
        Render this widget.

        :param name: Name of the widget.
        :return: Rendered html

        """
        if self.js_var_format is not None:
            js_var_bit = 'var %s = ' % (self.js_var_format % name)
        else:
            js_var_bit = ''
        output = [super(CodeMirror, self).render(name, value, attrs),
                  '<script type="text/javascript">'
                  '%sCodeMirror.fromTextArea('
                  'document.getElementById(%s), %s);'
                  '</script>' %
                  (js_var_bit, '"id_%s"' % name, self.option_json)]
        return mark_safe('\n'.join(output))
