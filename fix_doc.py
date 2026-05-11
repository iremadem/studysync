 
import os

# 1. documentation.html template
doc_html = """{% extends 'base.html' %}
{% block content %}
<h2 class="mb-4 text-center" style="font-family:'Playfair Display',Georgia,serif; font-style:italic; background:linear-gradient(135deg,#667eea,#764ba2); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">Documentation</h2>

{% for room in rooms %}
<div class="mb-4 p-4" style="border-radius:15px; border:1.5px solid rgba(102,126,234,0.3); box-shadow:0 4px 15px rgba(102,126,234,0.1);">
    <h5 style="font-family:'Playfair Display',Georgia,serif; font-style:italic; color:#667eea;">{{ room.title }}</h5>
    <span class="badge mb-3" style="background:linear-gradient(135deg,#667eea,#764ba2); color:white;">{{ room.subject }}</span>

    <div class="row g-3 mt-1">
        <div class="col-md-6">
            <div class="p-3" style="background:rgba(102,126,234,0.07); border-radius:10px;">
                <h6 style="color:#764ba2;">📝 Ders Notu Kaynakları</h6>
                <ul style="color:#555; padding-left:18px;">
                    <li>{{ room.subject }} - Ders Notlari (PDF)</li>
                    <li>{{ room.subject }} - Ozet Notlar</li>
                    <li>{{ room.subject }} - Calisma Kagidi</li>
                </ul>
            </div>
        </div>
        <div class="col-md-6">
            <div class="p-3" style="background:rgba(102,126,234,0.07); border-radius:10px;">
                <h6 style="color:#764ba2;">🎥 Ders Video Kaynakları</h6>
                <ul style="color:#555; padding-left:18px;">
                    <li>{{ room.subject }} - Giris Videosu</li>
                    <li>{{ room.subject }} - Konu Anlatimi</li>
                    <li>{{ room.subject }} - Soru Cozumu</li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% empty %}
<p class="text-center text-muted">Henuz hic room olusturulmamis.</p>
{% endfor %}
{% endblock %}"""

# 2. views.py'ye documentation view ekle
views_path = 'core/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

doc_view = """

def documentation(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import StudyRoom
    rooms = StudyRoom.objects.all()
    return render(request, 'documentation.html', {'rooms': rooms})
"""

if 'def documentation' not in views_content:
    with open(views_path, 'a', encoding='utf-8') as f:
        f.write(doc_view)
    print("views.py guncellendi.")
else:
    print("views.py zaten guncelli.")

# 3. urls.py'ye path ekle
urls_path = 'core/urls.py'
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if 'documentation' not in urls_content:
    urls_content = urls_content.replace(
        "path('save-notes/<int:pk>/', views.save_notes, name='save-notes'),",
        "path('save-notes/<int:pk>/', views.save_notes, name='save-notes'),\n    path('documentation/', views.documentation, name='documentation'),"
    )
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# 4. documentation.html kaydet
template_path = 'core/templates/documentation.html'
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(doc_html)
print("documentation.html olusturuldu.")

print("\nTUM ISLEMLER TAMAMLANDI!")