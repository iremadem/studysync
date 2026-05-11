 
html = """<!DOCTYPE html>
<html>
<head>
    <title>StudySync</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body {
        background: linear-gradient(135deg, #89f7fe, #66a6ff, #c2e9fb);
        min-height: 100vh;
    }
    </style>
</head>
<body>
<div class="container mt-4 p-4" style="background-color:white; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.1); min-height:80vh;">

    <nav class="navbar navbar-expand-lg rounded" style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 12px 20px;">
        <div class="container-fluid">
            <a href="/" style="font-family:Georgia,serif; font-style:italic; font-weight:700; font-size:1.35rem; background:linear-gradient(135deg,#e0c3fc,#ffffff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-decoration:none;">StudySync</a>
            <div>
                <a class="btn me-2" href="/rooms/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">Rooms</a>
                <a class="btn me-2" href="/create-room/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">Create</a>

                {% if request.user.is_authenticated %}
                    <span style="color:white; margin-right:8px;">👤 {{ request.user.username }}</span>
                    <form action="/logout/" method="POST" style="display:inline; margin:0;">
                        {% csrf_token %}
                        <button class="btn" style="border:1.5px solid rgba(255,100,100,0.7); color:#ffcccc; background:transparent;" onmouseover="this.style.background='#e74c3c'; this.style.color='white'" onmouseout="this.style.background='transparent'; this.style.color='#ffcccc'">Logout</button>
                    </form>
                {% else %}
                    <a class="btn me-2" href="/login/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">Login</a>
                    <a class="btn" href="/register/" style="border:1.5px solid rgba(255,255,255,0.6); color:white; background:transparent;" onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='transparent'">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="mt-4">
        {% block content %}
        {% endblock %}
    </div>

</div>
</body>
</html>"""

with open('core/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Basarili! base.html guncellendi.")