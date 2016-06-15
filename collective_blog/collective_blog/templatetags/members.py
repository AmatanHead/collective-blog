from django import template

register = template.Library()


@register.inclusion_tag('blog/tags/member.html')
def render_membership(membership, self_membership, render_karma=True):
    return dict(
        membership=membership,
        self_membership=self_membership,
        render_karma=render_karma,
        ban_perm=(
            (self_membership.role == "O" and membership.role != "O") or (
                self_membership.can_ban() and
                membership.role in ["M", "B", "LB"])
        ) if membership is not None and self_membership is not None else False,
        accept_perm=(
            self_membership.can_accept_new_users() and
            membership.role == "W"
        ) if membership is not None and self_membership is not None else False,
        manage_perm=(
            (self_membership.role == "O" and membership.role != "O") or (
                self_membership.can_manage_permissions() and
                membership.role in ["M", "A"]) and
            not membership.is_banned() and
            self_membership.user != membership.user
        ) if membership is not None and self_membership is not None else False
    )
