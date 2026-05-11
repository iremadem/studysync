import os

TEMPLATES = 'core/templates'

# ── 1. DOCUMENTATION.HTML ────────────────────────────────────────
doc_html = """{% extends 'base.html' %}
{% block content %}

<h2 class="mb-4 text-center" style="font-family:'Playfair Display',Georgia,serif;font-style:italic;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Documentation</h2>

{% for room in rooms %}
<div class="mb-4 p-4" style="border-radius:15px;border:1.5px solid rgba(102,126,234,0.3);box-shadow:0 4px 15px rgba(102,126,234,0.1);">
    <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;">{{ room.title }}</h5>
    <span class="badge mb-3" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;">{{ room.subject }}</span>

    <div class="row g-3 mt-1">
        <div class="col-md-6">
            <div class="p-3" style="background:rgba(102,126,234,0.07);border-radius:10px;">
                <h6 style="color:#764ba2;">📝 Ders Notu Kaynakları</h6>
                <ul style="list-style:none;padding:0;">
                    <li class="mb-2">
                        <a href="#" onclick="openNote('{{ room.subject }} - Ders Notları', '{{ room.subject }} dersine ait temel kavramlar, formüller ve özet bilgiler bu notta yer almaktadır. Konular: Giriş, Temel Kavramlar, Örnekler, Özet.'); return false;" style="color:#667eea;text-decoration:none;">
                            📄 {{ room.subject }} - Ders Notları
                        </a>
                    </li>
                    <li class="mb-2">
                        <a href="#" onclick="openNote('{{ room.subject }} - Özet Notlar', '{{ room.subject }} dersinin kısa özeti. Sınav öncesi tekrar için idealdir. Anahtar kelimeler ve formüller öne çıkarılmıştır.'); return false;" style="color:#667eea;text-decoration:none;">
                            📄 {{ room.subject }} - Özet Notlar
                        </a>
                    </li>
                    {% if request.user.userprofile.is_premium %}
                    <li class="mb-2">
                        <a href="#" onclick="openNote('{{ room.subject }} - Detaylı Notlar ⭐', '{{ room.subject }} dersinin ileri seviye detaylı notları. İspat ve türetmeler dahil. Premium içerik: Bölüm 1-5 arası tüm konular derinlemesine işlenmiştir.'); return false;" style="color:#764ba2;text-decoration:none;font-weight:500;">
                            ⭐ {{ room.subject }} - Detaylı Notlar
                        </a>
                    </li>
                    <li class="mb-2">
                        <a href="#" onclick="openNote('{{ room.subject }} - Sınav Hazırlık Paketi ⭐', '{{ room.subject }} sınavına özel hazırlık paketi. Çıkmış sorular, tahmin sorular ve cevap anahtarları. Premium üyelere özel.'); return false;" style="color:#764ba2;text-decoration:none;font-weight:500;">
                            ⭐ {{ room.subject }} - Sınav Hazırlık
                        </a>
                    </li>
                    {% else %}
                    <li class="mb-2" style="color:#bbb;">🔒 Detaylı Notlar <a href="/premium/" style="color:#667eea;font-size:0.8rem;">Premium'a geç</a></li>
                    <li class="mb-2" style="color:#bbb;">🔒 Sınav Hazırlık <a href="/premium/" style="color:#667eea;font-size:0.8rem;">Premium'a geç</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>

        <div class="col-md-6">
            <div class="p-3" style="background:rgba(102,126,234,0.07);border-radius:10px;">
                <h6 style="color:#764ba2;">🎥 Ders Video Kaynakları</h6>
                <ul style="list-style:none;padding:0;">
                    <li class="mb-2">
                        <a href="#" onclick="openFakeVideo('{{ room.subject }} - Giriş Videosu'); return false;" style="color:#667eea;text-decoration:none;">
                            ▶ {{ room.subject }} - Giriş Videosu
                        </a>
                    </li>
                    <li class="mb-2">
                        <a href="#" onclick="openFakeVideo('{{ room.subject }} - Konu Anlatımı'); return false;" style="color:#667eea;text-decoration:none;">
                            ▶ {{ room.subject }} - Konu Anlatımı
                        </a>
                    </li>
                    {% if request.user.userprofile.is_premium %}
                    <li class="mb-2">
                        <a href="#" onclick="openYoutube('https://www.youtube.com/embed/dQw4w9WgXcQ', '{{ room.subject }} - İleri Düzey Video'); return false;" style="color:#764ba2;text-decoration:none;font-weight:500;">
                            ⭐ {{ room.subject }} - İleri Düzey Video
                        </a>
                    </li>
                    <li class="mb-2">
                        <a href="#" onclick="openYoutube('https://www.youtube.com/embed/dQw4w9WgXcQ', '{{ room.subject }} - Canlı Ders Arşivi'); return false;" style="color:#764ba2;text-decoration:none;font-weight:500;">
                            ⭐ {{ room.subject }} - Canlı Ders Arşivi
                        </a>
                    </li>
                    {% else %}
                    <li class="mb-2" style="color:#bbb;">🔒 İleri Düzey Video <a href="/premium/" style="color:#667eea;font-size:0.8rem;">Premium'a geç</a></li>
                    <li class="mb-2" style="color:#bbb;">🔒 Canlı Ders Arşivi <a href="/premium/" style="color:#667eea;font-size:0.8rem;">Premium'a geç</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </div>
</div>
{% empty %}
<p class="text-center text-muted">Henüz hiç room oluşturulmamış.</p>
{% endfor %}

<!-- NOT MODAL -->
<div id="noteModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:20px;padding:36px;max-width:560px;width:90%;position:relative;box-shadow:0 20px 60px rgba(0,0,0,0.2);">
        <button onclick="closeModal('noteModal')" style="position:absolute;top:16px;right:20px;background:none;border:none;font-size:1.5rem;cursor:pointer;color:#999;">✕</button>
        <h5 id="noteTitle" style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;margin-bottom:16px;"></h5>
        <div style="background:rgba(102,126,234,0.07);border-radius:12px;padding:20px;">
            <p id="noteContent" style="color:#444;line-height:1.8;margin:0;"></p>
        </div>
        <div class="mt-3 text-end">
            <button onclick="closeModal('noteModal')" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;padding:8px 24px;cursor:pointer;">Kapat</button>
        </div>
    </div>
</div>

<!-- SAHTE VIDEO MODAL -->
<div id="fakeVideoModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:20px;padding:28px;max-width:600px;width:90%;position:relative;">
        <button onclick="closeModal('fakeVideoModal')" style="position:absolute;top:16px;right:20px;background:none;border:none;font-size:1.5rem;cursor:pointer;color:#999;">✕</button>
        <h5 id="fakeVideoTitle" style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;margin-bottom:16px;"></h5>
        <div style="background:#111;border-radius:12px;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;">
            <div style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;" onclick="this.innerHTML='⏸';this.style.background='rgba(102,126,234,0.5)'">
                <span style="color:white;font-size:1.8rem;">▶</span>
            </div>
            <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;">Ücretsiz önizleme</span>
        </div>
        <div class="mt-3 text-center">
            <span style="color:#999;font-size:0.85rem;">Daha fazlası için </span>
            <a href="/premium/" style="color:#667eea;font-size:0.85rem;font-weight:600;">Premium'a geçin ⭐</a>
        </div>
    </div>
</div>

<!-- YOUTUBE MODAL (PREMIUM) -->
<div id="youtubeModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:20px;padding:28px;max-width:700px;width:90%;position:relative;">
        <button onclick="closeModal('youtubeModal')" style="position:absolute;top:16px;right:20px;background:none;border:none;font-size:1.5rem;cursor:pointer;color:#999;">✕</button>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <h5 id="youtubeTitle" style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;margin:0;"></h5>
            <span style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:20px;padding:2px 10px;font-size:0.75rem;">⭐ Premium</span>
        </div>
        <div style="border-radius:12px;overflow:hidden;aspect-ratio:16/9;">
            <iframe id="youtubeFrame" width="100%" height="100%" src="" frameborder="0" allowfullscreen style="display:block;"></iframe>
        </div>
    </div>
</div>

<script>
function openNote(title, content) {
    document.getElementById('noteTitle').innerText = title;
    document.getElementById('noteContent').innerText = content;
    document.getElementById('noteModal').style.display = 'flex';
}
function openFakeVideo(title) {
    document.getElementById('fakeVideoTitle').innerText = title;
    document.getElementById('fakeVideoModal').style.display = 'flex';
}
function openYoutube(url, title) {
    document.getElementById('youtubeTitle').innerText = title;
    document.getElementById('youtubeFrame').src = url;
    document.getElementById('youtubeModal').style.display = 'flex';
}
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
    if (id === 'youtubeModal') document.getElementById('youtubeFrame').src = '';
}
window.onclick = function(e) {
    ['noteModal','fakeVideoModal','youtubeModal'].forEach(function(id) {
        var modal = document.getElementById(id);
        if (e.target === modal) {
            modal.style.display = 'none';
            if (id === 'youtubeModal') document.getElementById('youtubeFrame').src = '';
        }
    });
}
</script>
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'documentation.html'), 'w', encoding='utf-8') as f:
    f.write(doc_html)
print("documentation.html guncellendi.")

# ── 2. PREMIUM ROOMS TEMPLATE ────────────────────────────────────
premium_rooms_html = """{% extends 'base.html' %}
{% block content %}

{% if not request.user.userprofile.is_premium %}
<div class="text-center py-5">
    <div style="font-size:4rem;">🔒</div>
    <h3 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;color:#667eea;" class="mt-3">Bu alan Premium üyelere özeldir</h3>
    <p style="color:#777;" class="mt-2">Birebir özel ders odalarına erişmek için Premium üyeliğe geçin.</p>
    <a href="/premium/" class="btn mt-3" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;padding:12px 32px;font-size:1rem;">⭐ Premium'a Geç</a>
</div>
{% else %}

<div class="d-flex align-items-center justify-content-between mb-4">
    <h2 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;">Premium Rooms</h2>
    <span style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:20px;padding:4px 16px;font-size:0.85rem;">⭐ Premium Üye</span>
</div>

<div class="row g-4">

    <div class="col-md-6">
        <div class="p-4" style="border-radius:15px;background:linear-gradient(135deg,#667eea,#764ba2);box-shadow:0 8px 25px rgba(102,126,234,0.35);color:white;">
            <div style="font-size:2rem;" class="mb-2">🧑‍🏫</div>
            <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;">Birebir Matematik Odası</h5>
            <p style="opacity:0.85;font-size:0.9rem;">Özel öğretmen eşliğinde birebir matematik çalışma seansı. Sorularını anlık sor, anında cevap al.</p>
            <div class="d-flex align-items-center gap-2 mb-3">
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">👥 Max 2 kişi</span>
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">⏱ 60 dk</span>
            </div>
            <a href="/rooms/" class="btn" style="background:white;color:#667eea;border:none;border-radius:10px;font-weight:600;">Odaya Katıl →</a>
        </div>
    </div>

    <div class="col-md-6">
        <div class="p-4" style="border-radius:15px;background:linear-gradient(135deg,#f093fb,#f5576c);box-shadow:0 8px 25px rgba(240,147,251,0.35);color:white;">
            <div style="font-size:2rem;" class="mb-2">🔬</div>
            <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;">Birebir Fizik Odası</h5>
            <p style="opacity:0.85;font-size:0.9rem;">Fizik problemlerini adım adım çöz. Formüller, deneyler ve soru çözüm teknikleri üzerine odaklan.</p>
            <div class="d-flex align-items-center gap-2 mb-3">
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">👥 Max 2 kişi</span>
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">⏱ 60 dk</span>
            </div>
            <a href="/rooms/" class="btn" style="background:white;color:#f5576c;border:none;border-radius:10px;font-weight:600;">Odaya Katıl →</a>
        </div>
    </div>

    <div class="col-md-6">
        <div class="p-4" style="border-radius:15px;background:linear-gradient(135deg,#4facfe,#00f2fe);box-shadow:0 8px 25px rgba(79,172,254,0.35);color:white;">
            <div style="font-size:2rem;" class="mb-2">💻</div>
            <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;">Birebir Programlama Odası</h5>
            <p style="opacity:0.85;font-size:0.9rem;">Python, Java veya web geliştirme konularında bire bir mentorluk. Proje bazlı öğrenme.</p>
            <div class="d-flex align-items-center gap-2 mb-3">
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">👥 Max 2 kişi</span>
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">⏱ 90 dk</span>
            </div>
            <a href="/rooms/" class="btn" style="background:white;color:#4facfe;border:none;border-radius:10px;font-weight:600;">Odaya Katıl →</a>
        </div>
    </div>

    <div class="col-md-6">
        <div class="p-4" style="border-radius:15px;background:linear-gradient(135deg,#43e97b,#38f9d7);box-shadow:0 8px 25px rgba(67,233,123,0.35);color:white;">
            <div style="font-size:2rem;" class="mb-2">📚</div>
            <h5 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;">Birebir Türkçe/Edebiyat Odası</h5>
            <p style="opacity:0.85;font-size:0.9rem;">Kompozisyon, şiir analizi ve dil bilgisi konularında özel destek. YKS Türkçe hazırlık.</p>
            <div class="d-flex align-items-center gap-2 mb-3">
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">👥 Max 2 kişi</span>
                <span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:0.8rem;">⏱ 60 dk</span>
            </div>
            <a href="/rooms/" class="btn" style="background:white;color:#43e97b;border:none;border-radius:10px;font-weight:600;">Odaya Katıl →</a>
        </div>
    </div>

</div>
{% endif %}
{% endblock %}"""

with open(os.path.join(TEMPLATES, 'premium_rooms.html'), 'w', encoding='utf-8') as f:
    f.write(premium_rooms_html)
print("premium_rooms.html olusturuldu.")

# ── 3. views.py'ye premium_rooms ekle ───────────────────────────
with open('core/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

if 'def premium_rooms' not in views_content:
    views_content += """

def premium_rooms(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    return render(request, 'premium_rooms.html')
"""
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("views.py guncellendi.")
else:
    print("views.py zaten guncelli.")

# ── 4. urls.py'ye premium_rooms ekle ────────────────────────────
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

if 'premium-rooms' not in urls_content:
    urls_content = urls_content.replace(
        "path('premium/', views.pricing, name='pricing'),",
        "path('premium/', views.pricing, name='pricing'),\n    path('premium-rooms/', views.premium_rooms, name='premium-rooms'),"
    )
    with open('core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# ── 5. premium.html'e Premium Rooms linki ekle ──────────────────
with open(os.path.join(TEMPLATES, 'premium.html'), 'r', encoding='utf-8') as f:
    premium_content = f.read()

if 'premium-rooms' not in premium_content:
    cta = """
<div class="text-center mt-4 mb-2">
    <a href="/premium-rooms/" class="btn" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;padding:12px 32px;font-size:1rem;">
        ⭐ Premium Odaları Görüntüle
    </a>
</div>"""
    premium_content = premium_content.replace('{% endblock %}', cta + '\n{% endblock %}')
    with open(os.path.join(TEMPLATES, 'premium.html'), 'w', encoding='utf-8') as f:
        f.write(premium_content)
    print("premium.html guncellendi.")

print("\nTUM ISLEMLER TAMAMLANDI!")