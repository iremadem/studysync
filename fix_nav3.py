 
with open('core/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '{% if request.user.is_authenticated %}'
new = """{% if request.user.is_staff %}
                <a class="btn me-2" href="/admin-panel/" style="border:1.5px solid rgba(255,255,255,0.6);color:white;background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">⚙ Panel</a>
                {% endif %}
                {% if request.user.is_authenticated %}"""

content = content.replace(old, new, 1)

with open('core/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Navbar guncellendi!")