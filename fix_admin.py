import os

TEMPLATES = 'core/templates'

# ── 1. models.py: PremiumRequest modeli ekle ─────────────────────
with open('core/models.py', 'r', encoding='utf-8') as f:
    models_content = f.read()

if 'PremiumRequest' not in models_content:
    models_content += """

class PremiumRequest(models.Model):
    PLAN_CHOICES = [
        ('weekly', 'Haftalık - 49TL'),
        ('monthly', 'Aylık - 149TL'),
        ('yearly', 'Yıllık - 999TL'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_requests')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f\"{self.user.username} - {self.plan} - {self.status}\"
"""
    with open('core/models.py', 'w', encoding='utf-8') as f:
        f.write(models_content)
    print("models.py guncellendi.")
else:
    print("models.py zaten guncelli.")

# ── 2. admin_panel.html ──────────────────────────────────────────
admin_panel_html = """{% extends 'base.html' %}
{% block content %}

{% if not request.user.is_staff %}
<div class="text-center py-5">
    <div style="font-size:4rem;">🚫</div>
    <h3 style="color:#e74c3c;" class="mt-3">Bu alana erişim yetkiniz yok.</h3>
</div>
{% else %}

<h2 class="mb-4" style="font-family:'Playfair Display',Georgia,serif;font-style:italic;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    Admin Paneli
</h2>

<!-- İSTATİSTİK KARTLARI -->
<div class="row g-3 mb-5">
    <div class="col-md-3">
        <div class="p-4 text-center" style="border-radius:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;box-shadow:0 6px 20px rgba(102,126,234,0.3);">
            <div style="font-size:2.2rem;font-weight:700;">{{ total_users }}</div>
            <div style="opacity:0.85;font-size:0.9rem;">👥 Toplam Kullanıcı</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="p-4 text-center" style="border-radius:15px;background:linear-gradient(135deg,#f093fb,#f5576c);color:white;box-shadow:0 6px 20px rgba(240,147,251,0.3);">
            <div style="font-size:2.2rem;font-weight:700;">{{ premium_users }}</div>
            <div style="opacity:0.85;font-size:0.9rem;">⭐ Premium Kullanıcı</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="p-4 text-center" style="border-radius:15px;background:linear-gradient(135deg,#4facfe,#00f2fe);color:white;box-shadow:0 6px 20px rgba(79,172,254,0.3);">
            <div style="font-size:2.2rem;font-weight:700;">{{ total_rooms }}</div>
            <div style="opacity:0.85;font-size:0.9rem;">🏠 Toplam Room</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="p-4 text-center" style="border-radius:15px;background:linear-gradient(135deg,#43e97b,#38f9d7);color:white;box-shadow:0 6px 20px rgba(67,233,123,0.3);">
            <div style="font-size:2.2rem;font-weight:700;">{{ pending_count }}</div>
            <div style="opacity:0.85;font-size:0.9rem;">⏳ Bekleyen Talep</div>
        </div>
    </div>
</div>

<!-- EN AKTİF ROOMLAR -->
<div class="mb-5">
    <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;" class="mb-3">🏆 En Aktif Roomlar</h5>
    <div style="border-radius:15px;border:1.5px solid rgba(102,126,234,0.2);overflow:hidden;">
        <table class="table mb-0">
            <thead style="background:rgba(102,126,234,0.08);">
                <tr>
                    <th style="color:#667eea;">#</th>
                    <th style="color:#667eea;">Room Adı</th>
                    <th style="color:#667eea;">Konu</th>
                    <th style="color:#667eea;">Oluşturan</th>
                </tr>
            </thead>
            <tbody>
                {% for room in top_rooms %}
                <tr>
                    <td style="color:#999;">{{ forloop.counter }}</td>
                    <td style="font-weight:500;">{{ room.title }}</td>
                    <td><span class="badge" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;">{{ room.subject }}</span></td>
                    <td style="color:#555;">{{ room.host.username }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="4" class="text-center text-muted py-3">Henüz room yok.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- BEKLEYen TALEPLER -->
<div class="mb-5">
    <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;" class="mb-3">⏳ Bekleyen Premium Talepleri</h5>
    <div style="border-radius:15px;border:1.5px solid rgba(102,126,234,0.2);overflow:hidden;">
        <table class="table mb-0">
            <thead style="background:rgba(102,126,234,0.08);">
                <tr>
                    <th style="color:#667eea;">Kullanıcı</th>
                    <th style="color:#667eea;">Plan</th>
                    <th style="color:#667eea;">Tarih</th>
                    <th style="color:#667eea;">İşlem</th>
                </tr>
            </thead>
            <tbody>
                {% for req in pending_requests %}
                <tr>
                    <td style="font-weight:500;">{{ req.user.username }}</td>
                    <td><span class="badge" style="background:linear-gradient(135deg,#f093fb,#f5576c);color:white;">{{ req.get_plan_display }}</span></td>
                    <td style="color:#777;font-size:0.85rem;">{{ req.created_at|date:"d.m.Y H:i" }}</td>
                    <td>
                        <form method="POST" action="/admin-panel/approve/{{ req.id }}/" style="display:inline;">
                            {% csrf_token %}
                            <button class="btn btn-sm" style="background:linear-gradient(135deg,#43e97b,#38f9d7);color:white;border:none;border-radius:8px;">✓ Onayla</button>
                        </form>
                        <form method="POST" action="/admin-panel/reject/{{ req.id }}/" style="display:inline;margin-left:6px;">
                            {% csrf_token %}
                            <button class="btn btn-sm" style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;border:none;border-radius:8px;">✗ Reddet</button>
                        </form>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="4" class="text-center text-muted py-3">Bekleyen talep yok. ✅</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- TÜM TALEP GEÇMİŞİ -->
<div class="mb-4">
    <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;" class="mb-3">📋 Tüm Talep Geçmişi</h5>
    <div style="border-radius:15px;border:1.5px solid rgba(102,126,234,0.2);overflow:hidden;">
        <table class="table mb-0">
            <thead style="background:rgba(102,126,234,0.08);">
                <tr>
                    <th style="color:#667eea;">Kullanıcı</th>
                    <th style="color:#667eea;">Plan</th>
                    <th style="color:#667eea;">Durum</th>
                    <th style="color:#667eea;">Başvuru</th>
                    <th style="color:#667eea;">İşlem Tarihi</th>
                </tr>
            </thead>
            <tbody>
                {% for req in all_requests %}
                <tr>
                    <td style="font-weight:500;">{{ req.user.username }}</td>
                    <td>{{ req.get_plan_display }}</td>
                    <td>
                        {% if req.status == 'approved' %}
                            <span class="badge" style="background:#43e97b;color:white;">✓ Onaylandı</span>
                        {% elif req.status == 'rejected' %}
                            <span class="badge" style="background:#e74c3c;color:white;">✗ Reddedildi</span>
                        {% else %}
                            <span class="badge" style="background:#f39c12;color:white;">⏳ Bekliyor</span>
                        {% endif %}
                    </td>
                    <td style="color:#777;font-size:0.85rem;">{{ req.created_at|date:"d.m.Y H:i" }}</td>
                    <td style="color:#777;font-size:0.85rem;">{{ req.reviewed_at|date:"d.m.Y H:i"|default:"-" }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="text-center text-muted py-3">Henüz talep yok.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

{% endif %}
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'admin_panel.html'), 'w', encoding='utf-8') as f:
    f.write(admin_panel_html)
print("admin_panel.html olusturuldu.")

# ── 3. premium.html: butonlara talep formu ekle ──────────────────
premium_html = """{% extends 'base.html' %}
{% block content %}

{% if messages %}
{% for message in messages %}
<div class="alert" style="border-radius:10px;background:{% if 'hata' in message.tags %}rgba(231,76,60,0.1){% else %}rgba(67,233,123,0.15){% endif %};border:1.5px solid {% if 'hata' in message.tags %}#e74c3c{% else %}#43e97b{% endif %};color:#333;margin-bottom:16px;">
    {{ message }}
</div>
{% endfor %}
{% endif %}

<div class="text-center mb-5">
    <h2 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;font-size:2.5rem;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Choose Your Plan
    </h2>
    <p style="color:#777;font-size:1.1rem;">Unlock premium content and exclusive study rooms.</p>
</div>

<div class="row g-4 justify-content-center mb-5">

    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px;border:1.5px solid rgba(102,126,234,0.3);box-shadow:0 4px 20px rgba(102,126,234,0.1);transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-6px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="font-size:2.5rem;" class="mb-3">⚡</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;">Haftalık</h4>
            <div style="font-size:2.2rem;font-weight:700;color:#333;" class="my-3">₺49 <span style="font-size:1rem;color:#999;">/ hafta</span></div>
            <ul style="list-style:none;padding:0;color:#555;text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2" style="color:#bbb;">❌ Öncelikli destek</li>
            </ul>
            <form method="POST" action="/premium/request/">
                {% csrf_token %}
                <input type="hidden" name="plan" value="weekly">
                <button class="btn w-100 mt-3" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;padding:12px;">Satın Al →</button>
            </form>
        </div>
    </div>

    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px;background:linear-gradient(135deg,#667eea,#764ba2);box-shadow:0 8px 30px rgba(102,126,234,0.4);transform:translateY(-8px);transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-14px)'" onmouseout="this.style.transform='translateY(-8px)'">
            <div class="mb-2"><span style="background:rgba(255,255,255,0.25);color:white;border-radius:20px;padding:4px 14px;font-size:0.8rem;">⭐ En Popüler</span></div>
            <div style="font-size:2.5rem;" class="mb-3">🚀</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:white;">Aylık</h4>
            <div style="font-size:2.2rem;font-weight:700;color:white;" class="my-3">₺149 <span style="font-size:1rem;opacity:0.8;">/ ay</span></div>
            <ul style="list-style:none;padding:0;color:rgba(255,255,255,0.9);text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2">✅ Öncelikli destek</li>
            </ul>
            <form method="POST" action="/premium/request/">
                {% csrf_token %}
                <input type="hidden" name="plan" value="monthly">
                <button class="btn w-100 mt-3" style="background:white;color:#667eea;border:none;border-radius:10px;padding:12px;font-weight:600;">Satın Al →</button>
            </form>
        </div>
    </div>

    <div class="col-md-4">
        <div class="p-4 text-center h-100" style="border-radius:20px;border:1.5px solid rgba(102,126,234,0.3);box-shadow:0 4px 20px rgba(102,126,234,0.1);transition:transform 0.3s;" onmouseover="this.style.transform='translateY(-6px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="font-size:2.5rem;" class="mb-3">👑</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;">Yıllık</h4>
            <div style="font-size:2.2rem;font-weight:700;color:#333;" class="my-3">₺999 <span style="font-size:1rem;color:#999;">/ yıl</span></div>
            <div style="color:#e74c3c;font-size:0.85rem;margin-bottom:8px;">🎁 2 ay ücretsiz!</div>
            <ul style="list-style:none;padding:0;color:#555;text-align:left;">
                <li class="mb-2">✅ Premium ders notları</li>
                <li class="mb-2">✅ Premium video kaynakları</li>
                <li class="mb-2">✅ Özel premium roomlar</li>
                <li class="mb-2">✅ Öncelikli destek</li>
            </ul>
            <form method="POST" action="/premium/request/">
                {% csrf_token %}
                <input type="hidden" name="plan" value="yearly">
                <button class="btn w-100 mt-3" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;padding:12px;">Satın Al →</button>
            </form>
        </div>
    </div>
</div>

<div class="text-center mt-2 mb-4">
    <a href="/premium-rooms/" class="btn" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;padding:12px 32px;font-size:1rem;">
        ⭐ Premium Odaları Görüntüle
    </a>
</div>
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'premium.html'), 'w', encoding='utf-8') as f:
    f.write(premium_html)
print("premium.html guncellendi.")

# ── 4. views.py: yeni viewlar ekle ──────────────────────────────
with open('core/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

new_views = """

def admin_panel(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, 'admin_panel.html')
    from django.contrib.auth.models import User
    from .models import StudyRoom, UserProfile, PremiumRequest
    total_users = User.objects.count()
    premium_users = UserProfile.objects.filter(is_premium=True).count()
    total_rooms = StudyRoom.objects.count()
    pending_requests = PremiumRequest.objects.filter(status='pending').order_by('-created_at')
    pending_count = pending_requests.count()
    all_requests = PremiumRequest.objects.all().order_by('-created_at')
    top_rooms = StudyRoom.objects.all()[:10]
    return render(request, 'admin_panel.html', {
        'total_users': total_users,
        'premium_users': premium_users,
        'total_rooms': total_rooms,
        'pending_requests': pending_requests,
        'pending_count': pending_count,
        'all_requests': all_requests,
        'top_rooms': top_rooms,
    })


def premium_request(request):
    if not request.user.is_authenticated:
        return redirect('login')
    from .models import PremiumRequest
    from django.contrib import messages
    if request.method == 'POST':
        plan = request.POST.get('plan')
        existing = PremiumRequest.objects.filter(user=request.user, status='pending')
        if existing.exists():
            messages.warning(request, 'Zaten bekleyen bir talebiniz var. Admin onayını bekleyin.')
        else:
            PremiumRequest.objects.create(user=request.user, plan=plan)
            messages.success(request, 'Talebiniz alındı! Admin onayından sonra premium üye olacaksınız.')
    return redirect('pricing')


def approve_premium(request, req_id):
    if not request.user.is_staff:
        return redirect('home')
    from .models import PremiumRequest, UserProfile
    from django.utils import timezone
    if request.method == 'POST':
        req = PremiumRequest.objects.get(id=req_id)
        req.status = 'approved'
        req.reviewed_at = timezone.now()
        req.save()
        profile, _ = UserProfile.objects.get_or_create(user=req.user)
        profile.is_premium = True
        profile.save()
    return redirect('admin_panel')


def reject_premium(request, req_id):
    if not request.user.is_staff:
        return redirect('home')
    from .models import PremiumRequest
    from django.utils import timezone
    if request.method == 'POST':
        req = PremiumRequest.objects.get(id=req_id)
        req.status = 'rejected'
        req.reviewed_at = timezone.now()
        req.save()
    return redirect('admin_panel')
"""

if 'def admin_panel' not in views_content:
    with open('core/views.py', 'a', encoding='utf-8') as f:
        f.write(new_views)
    print("views.py guncellendi.")
else:
    print("views.py zaten guncelli.")

# ── 5. urls.py: yeni urllar ekle ────────────────────────────────
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

new_urls = """    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('premium/request/', views.premium_request, name='premium_request'),
    path('admin-panel/approve/<int:req_id>/', views.approve_premium, name='approve_premium'),
    path('admin-panel/reject/<int:req_id>/', views.reject_premium, name='reject_premium'),"""

if 'admin-panel' not in urls_content:
    urls_content = urls_content.replace(
        "path('premium-rooms/', views.premium_rooms, name='premium-rooms'),",
        "path('premium-rooms/', views.premium_rooms, name='premium-rooms'),\n" + new_urls
    )
    with open('core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# ── 6. admin.py: PremiumRequest kaydet ──────────────────────────
with open('core/admin.py', 'r', encoding='utf-8') as f:
    admin_content = f.read()

if 'PremiumRequest' not in admin_content:
    admin_content += "\nfrom .models import PremiumRequest\nadmin.site.register(PremiumRequest)\n"
    with open('core/admin.py', 'w', encoding='utf-8') as f:
        f.write(admin_content)
    print("admin.py guncellendi.")

print("\nTUM ISLEMLER TAMAMLANDI!")