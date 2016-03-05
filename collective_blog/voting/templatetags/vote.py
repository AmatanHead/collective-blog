from django import template

register = template.Library()


@register.inclusion_tag('voting/tags/vote.html')
def vote(name, prefix, url, pressed_class='outline',
         current_score=0,
         current_color='',
         self_vote=0,
         use_colors=True,
         bad_color_threshold=-10,
         good_color_threshold=10):
    """Display voting buttons"""
    return {
        'name': name,
        'prefix': prefix,
        'url': url,
        'pressed_class': pressed_class,
        'current_score': current_score,
        'self_vote': self_vote,
        'use_colors': use_colors,
        'current_color': current_color,
        'bad_color_threshold': bad_color_threshold,
        'good_color_threshold': good_color_threshold
    }


@register.inclusion_tag('voting/tags/vote_script.html')
def vote_script(name, prefix, url, pressed_class='outline',
                current_score=0,
                current_color='',
                self_vote=0,
                use_colors=True,
                bad_color_threshold=-10,
                good_color_threshold=10):
    """Make ajax script for voting

    Note that `voting/ajax_voting.js` should be loaded manually.

    Usage:

        <script>
            var vote = {% vote_script ... %};
        </script>

    """
    return {
        'name': name,
        'prefix': prefix,
        'url': url,
        'pressed_class': pressed_class,
        'current_score': current_score,
        'self_vote': self_vote,
        'use_colors': use_colors,
        'current_color': current_color,
        'bad_color_threshold': bad_color_threshold,
        'good_color_threshold': good_color_threshold
    }
