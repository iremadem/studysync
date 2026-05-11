import os

BASE = 'core'
TEMPLATES = os.path.join(BASE, 'templates')

# ── 1. PRICING TEMPLATE ──────────────────────────────────────────
pricing_html = """{% extends 'base.html' %}
{% block content %}

<div class="text-center mb-5">
    <h2 style="font-family:'Playfair Display',Georgia,serif; font-style:italic; font-size:2.5rem; background:linear-gradient(135deg,#667eea,#764ba2); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Choose Your Plan
    </h2>
    <p style="color:#777; font-size:1.1rem;">Unlock premium content and exclusive study rooms.</p>
</div>

<div class="row g-4 justify-content-center mb-5">

    <!-- WEEKLY -->
    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px; border:1.5px solid rgba(102,126,234,0.3); box-shadow:0 4px 20px rgba(102,126,234,0.1); transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-6px)'" onmouseout="this.style.transform='translateY(0)'">
            <div class="mb-3" style="font-size:2.5rem;">⚡</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif; font-style:italic; color:#667eea;">Weekly</h4>
            <div style="font-size:2.2rem; font-weight:700; color:#333;" class="my-3">₺49 <span style="font-size:1rem; color:#999;">/ week</span></div>
            <ul style="list-style:none; padding:0; color:#555; text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2" style="color:#bbb;">❌ Öncelikli destek</li>
            </ul>
            <button class="btn w-100 mt-3" style="background:linear-gradient(135deg,#667eea,#764ba2); color:white; border:none; border-radius:10px; padding:12px;" onclick="alert('Yakında aktif olacak!')">Başla →</button>
        </div>
    </div>

    <!-- MONTHLY (öne çıkan) -->
    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px; background:linear-gradient(135deg,#667eea,#764ba2); box-shadow:0 8px 30px rgba(102,126,234,0.4); transform:translateY(-8px); transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-14px)'" onmouseout="this.style.transform='translateY(-8px)'">
            <div class="mb-2"><span style="background:rgba(255,255,255,0.25); color:white; border-radius:20px; padding:4px 14px; font-size:0.8rem;">⭐ En Popüler</span></div>
            <div class="mb-3" style="font-size:2.5rem;">🚀</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif; font-style:italic; color:white;">Monthly</h4>
            <div style="font-size:2.2rem; font-weight:700; color:white;" class="my-3">₺149 <span style="font-size:1rem; opacity:0.8;">/ month</span></div>
            <ul style="list-style:none; padding:0; color:rgba(255,255,255,0.9); text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2">✅ Öncelikli destek</li>
            </ul>
            <button class="btn w-100 mt-3" style="background:white; color:#667eea; border:none; border-radius:10px; padding:12px; font-weight:600;" onclick="alert('Yakında aktif olacak!')">Başla →</button>
        </div>
    </div>

    <!-- YEARLY -->
    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px; border:1.5px solid rgba(102,126,234,0.3); box-shadow:0 4px 20px rgba(102,126,234,0.1); transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-6px)'" onmouseout="this.style.transform='translateY(0)'">
            <div class="mb-3" style="font-size:2.5rem;">👑</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif; font-style:italic; color:#667eea;">Yearly</h4>
            <div style="font-size:2.2rem; font-weight:700; color:#333;" class="my-3">₺999 <span style="font-size:1rem; color:#999;">/ year</span></div>
            <div style="color:#e74c3c; font-size:0.85rem; margin-bottom:8px;">🎁 2 ay ücretsiz!</div>
            <ul style="list-style:none; padding:0; color:#555; text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2">✅ Öncelikli destek</li>
            </ul>
            <button class="btn w-100 mt-3" style="background:linear-gradient(135deg,#667eea,#764ba2); color:white; border:none; border-radius:10px; padding:12px;" onclick="alert('Yakında aktif olacak!')">Başla →</button>
        </div>
    </div>
</div>
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'pricing.html'), 'w', encoding='utf-8') as f:
    f.write(pricing_html)
print("pricing.html olusturuldu.")

# ── 2. DOCUMENTATION TEMPLATE (premium kilitli icerik) ──────────
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
                    {% if request.user.userprofile.is_premium %}
                        <li>{{ room.subject }} - Detayli Notlar <span style="color:#667eea;">⭐</span></li>
                        <li>{{ room.subject }} - Sinav Hazirlik Paketi <span style="color:#667eea;">⭐</span></li>
                    {% else %}
                        <li style="color:#bbb;">🔒 Detayli Notlar <a href="/pricing/" style="color:#667eea; font-size:0.8rem;">Premium'a geç</a></li>
                        <li style="color:#bbb;">🔒 Sinav Hazirlik Paketi <a href="/pricing/" style="color:#667eea; font-size:0.8rem;">Premium'a geç</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
        <div class="col-md-6">
            <div class="p-3" style="background:rgba(102,126,234,0.07); border-radius:10px;">
                <h6 style="color:#764ba2;">🎥 Ders Video Kaynakları</h6>
                <ul style="color:#555; padding-left:18px;">
                    <li>{{ room.subject }} - Giris Videosu</li>
                    <li>{{ room.subject }} - Konu Anlatimi</li>
                    {% if request.user.userprofile.is_premium %}
                        <li>{{ room.subject }} - Ileri Duzey Video <span style="color:#667eea;">⭐</span></li>
                        <li>{{ room.subject }} - Canli Ders Arsivi <span style="color:#667eea;">⭐</span></li>
                    {% else %}
                        <li style="color:#bbb;">🔒 Ileri Duzey Video <a href="/pricing/" style="color:#667eea; font-size:0.8rem;">Premium'a geç</a></li>
                        <li style="color:#bbb;">🔒 Canli Ders Arsivi <a href="/pricing/" style="color:#667eea; font-size:0.8rem;">Premium'a geç</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </div>
</div>
{% empty %}
<p class="text-center text-muted">Henuz hic room olusturulmamis.</p>
{% endfor %}
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'documentation.html'), 'w', encoding='utf-8') as f:
    f.write(doc_html)
print("documentation.html guncellendi.")

# ── 3. models.py'ye UserProfile ekle ────────────────────────────
models_path = os.path.join(BASE, 'models.py')
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

profile_model = """

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f\"{self.user.username} - {'Premium' if self.is_premium else 'Free'}\"
"""

if 'UserProfile' not in models_content:
    with open(models_path, 'a', encoding='utf-8') as f:
        f.write(profile_model)
    print("models.py guncellendi.")
else:
    print("models.py zaten guncelli.")

# ── 4. views.py'ye pricing + auto profile oluşturma ─────────────
views_path = os.path.join(BASE, 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

pricing_view = """

def pricing(request):
    return render(request, 'pricing.html')
"""

register_fix = """
def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from .models import UserProfile
            UserProfile.objects.get_or_create(user=user)
            return redirect('login')

    return render(request, 'register.html', {'form': form})
"""

if 'def pricing' not in views_content:
    views_content += pricing_view

views_content = views_content.replace(
    """def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    return render(request, 'register.html', {'form': form})""",
    register_fix.strip()
)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)
print("views.py guncellendi.")

# ── 5. urls.py'ye pricing ekle ───────────────────────────────────
urls_path = os.path.join(BASE, 'urls.py')
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if "'pricing/'" not in urls_content:
    urls_content = urls_content.replace(
        "path('documentation/', views.documentation, name='documentation'),",
        "path('documentation/', views.documentation, name='documentation'),\n    path('pricing/', views.pricing, name='pricing'),"
    )
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# ── 6. admin.py'ye UserProfile kaydet ───────────────────────────
admin_path = os.path.join(BASE, 'admin.py')
with open(admin_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

if 'UserProfile' not in admin_content:
    admin_content += "\nfrom .models import UserProfile\nadmin.site.register(UserProfile)\n"
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(admin_content)
    print("admin.py guncellendi.")
else:
    print("admin.py zaten guncelli.")

print("\nTUM ISLEMLER TAMAMLANDI!") 
