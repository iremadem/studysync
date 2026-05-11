from django import template
from django.utils.safestring import mark_safe

register = template.Library()

BADGE_STYLES = {
    'moderator': {
        'label': 'Moderator',
        'color': '#e74c3c',
        'bg': 'rgba(231,76,60,0.1)',
        'border': 'rgba(231,76,60,0.25)',
    },
    'educator': {
        'label': 'Educator',
        'color': '#f7971e',
        'bg': 'rgba(247,151,30,0.1)',
        'border': 'rgba(247,151,30,0.25)',
    },
    'premium': {
        'label': 'Premium Student',
        'color': '#667eea',
        'bg': 'rgba(102,126,234,0.1)',
        'border': 'rgba(102,126,234,0.25)',
    },
    'student': {
        'label': 'Student',
        'color': '#aaa',
        'bg': 'rgba(170,170,170,0.1)',
        'border': 'rgba(170,170,170,0.2)',
    },
}

def get_role(user):
    if user.is_staff:
        return 'moderator'
    try:
        profile = user.userprofile
        if profile.is_educator:
            return 'educator'
        if profile.is_premium:
            return 'premium'
    except Exception:
        pass
    return 'student'

@register.simple_tag
def user_badge(user):
    role = get_role(user)
    s = BADGE_STYLES[role]
    html = (
        f'<span style="'
        f'display:inline-block;'
        f'background:{s["bg"]};'
        f'color:{s["color"]};'
        f'border:1px solid {s["border"]};'
        f'border-radius:20px;'
        f'padding:1px 9px;'
        f'font-size:0.7rem;'
        f'font-weight:600;'
        f'letter-spacing:0.3px;'
        f'margin-left:5px;'
        f'vertical-align:middle;'
        f'">{s["label"]}</span>'
    )
    return mark_safe(html)

@register.simple_tag
def user_badge_navbar(user):
    """Navbar için — beyaz arka plan üzerinde değil, koyu arka plan üzerinde"""
    role = get_role(user)
    s = BADGE_STYLES[role]
    html = (
        f'<span style="'
        f'display:inline-block;'
        f'background:rgba(255,255,255,0.15);'
        f'color:rgba(255,255,255,0.75);'
        f'border:1px solid rgba(255,255,255,0.2);'
        f'border-radius:20px;'
        f'padding:1px 9px;'
        f'font-size:0.7rem;'
        f'font-weight:600;'
        f'letter-spacing:0.3px;'
        f'margin-left:5px;'
        f'vertical-align:middle;'
        f'">{s["label"]}</span>'
    )
    return mark_safe(html)