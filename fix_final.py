# 1. urls.py'ye eksik endpointleri ekle
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls = f.read()

if 'check-kicked' not in urls:
    urls = urls.replace(
        "path('room/<int:room_pk>/kick/<int:user_pk>/', views.kick_participant, name='kick-participant'),",
        "path('room/<int:room_pk>/kick/<int:user_pk>/', views.kick_participant, name='kick-participant'),\n    path('room/<int:room_pk>/check-kicked/', views.check_kicked, name='check-kicked'),\n    path('room/<int:room_pk>/delete-message/<int:msg_pk>/', views.delete_message, name='delete-message'),"
    )
    with open('core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# 2. views.py'ye check_kicked ve delete_message ekle
with open('core/views.py', 'r', encoding='utf-8') as f:
    views = f.read()

if 'def check_kicked' not in views:
    views = views.replace(
        "def kick_participant(request, room_pk, user_pk):",
        """def check_kicked(request, room_pk):
    if not request.user.is_authenticated:
        return JsonResponse({'kicked': False})
    from django.core.cache import cache
    key = f'kicked_{room_pk}_{request.user.id}'
    kicked = bool(cache.get(key))
    if kicked:
        cache.delete(key)
    return JsonResponse({'kicked': kicked})


def delete_message(request, room_pk, msg_pk):
    room = get_object_or_404(StudyRoom, id=room_pk)
    if request.user != room.creator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        from .models import Message
        msg = get_object_or_404(Message, id=msg_pk, room=room)
        msg.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid'}, status=405)


def kick_participant(request, room_pk, user_pk):"""
    )
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(views)
    print("views.py guncellendi.")
else:
    print("views.py zaten guncelli.")

# 3. kick_participant'a cache sinyali ve admin yetkisi ekle
with open('core/views.py', 'r', encoding='utf-8') as f:
    views = f.read()

old_kick = '''def kick_participant(request, room_pk, user_pk):
    from django.contrib.auth.models import User
    room = get_object_or_404(StudyRoom, id=room_pk)
    if request.user != room.creator:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        user_to_kick = get_object_or_404(User, id=user_pk)
        room.participants.remove(user_to_kick)
        return JsonResponse({'status': 'ok', 'kicked': user_to_kick.username})
    return JsonResponse({'error': 'Invalid method'}, status=405)'''

new_kick = '''def kick_participant(request, room_pk, user_pk):
    from django.contrib.auth.models import User
    from django.core.cache import cache
    room = get_object_or_404(StudyRoom, id=room_pk)
    if request.user != room.creator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        user_to_kick = get_object_or_404(User, id=user_pk)
        room.participants.remove(user_to_kick)
        cache.set(f'kicked_{room_pk}_{user_pk}', True, timeout=60)
        return JsonResponse({'status': 'ok', 'kicked': user_to_kick.username})
    return JsonResponse({'error': 'Invalid method'}, status=405)'''

if 'cache.set' not in views.split('def kick_participant')[1].split('def ')[0]:
    views = views.replace(old_kick, new_kick)
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(views)
    print("kick_participant guncellendi.")
else:
    print("kick_participant zaten guncelli.")

# 4. room_detail.html: JS kickUser + deleteMsg + polling + overlayler
with open('core/templates/room_detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_kick_js = '''// ── KICK ──
function kickUser(userId, username) {
    if (!confirm(`Remove ${username} from this room?`)) return;
    fetch(`/room/${ROOM_ID}/kick/${userId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF, 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') location.reload();
    });
}'''

new_kick_js = '''// ── KICK ──
function kickUser(userId, username) {
    if (!confirm(username + ' adlı kullanıcıyı odadan çıkarmak istediğine emin misin?')) return;
    fetch(`/room/${ROOM_ID}/kick/${userId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF, 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            const row = document.getElementById('participant-' + userId);
            if (row) row.style.display = 'none';
        }
    });
}

// ── MESAJ SİL ──
function deleteMsg(msgId) {
    fetch(`/room/${ROOM_ID}/delete-message/${msgId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            const el = document.getElementById('msg-' + msgId);
            if (el) { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; setTimeout(() => el.remove(), 300); }
        }
    });
}

// ── KICK POLLİNG ──
{% if not is_creator %}
setInterval(function() {
    fetch('/room/' + ROOM_ID + '/check-kicked/')
    .then(r => r.json())
    .then(data => {
        if (data.kicked) {
            document.getElementById('kickedOverlay').style.display = 'flex';
            setTimeout(() => { window.location.href = '/rooms/'; }, 3000);
        }
    }).catch(() => {});
}, 4000);
{% endif %}'''

html = html.replace(old_kick_js, new_kick_js)

# 5. Participant div'lerine id ekle
old_p = '''<div class="participant-item">
                    <div class="participant-left">
                        <div class="avatar {% if participant == room.creator %}creator-avatar{% endif %}">
                            {{ participant.username|first|upper }}
                        </div>'''

new_p = '''<div class="participant-item" id="participant-{{ participant.id }}">
                    <div class="participant-left">
                        <div class="avatar {% if participant == room.creator %}creator-avatar{% endif %}">
                            {{ participant.username|first|upper }}
                        </div>'''

html = html.replace(old_p, new_p)

# 6. Chat mesajlarına silme butonu ekle
old_msg = '''<div class="chat-msg">
                    <strong>{{ msg.user.username }}</strong>{% user_badge msg.user %}&nbsp; {{ msg.content }}
                </div>'''

new_msg = '''<div class="chat-msg" id="msg-{{ msg.id }}" style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
                    <div><strong>{{ msg.user.username }}</strong>{% user_badge msg.user %}&nbsp; {{ msg.content }}</div>
                    {% if is_creator %}
                    <button onclick="deleteMsg({{ msg.id }})" style="background:none;border:none;color:#ddd;cursor:pointer;font-size:0.85rem;padding:2px 4px;flex-shrink:0;transition:color 0.2s;" onmouseover="this.style.color='#e74c3c'" onmouseout="this.style.color='#ddd'">🗑</button>
                    {% endif %}
                </div>'''

html = html.replace(old_msg, new_msg)

# 7. endblock'tan önce overlay'leri ve sözleşmeyi ekle
old_end = '</script>\n\n{% endblock %}'
new_end = '''</script>

<!-- ATILDI OVERLAY -->
<div id="kickedOverlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:99999;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:22px;padding:40px;max-width:380px;width:90%;text-align:center;box-shadow:0 24px 70px rgba(0,0,0,0.3);">
        <div style="font-size:3.5rem;">🚪</div>
        <h4 style="color:#e74c3c;margin:16px 0 10px;font-family:'Playfair Display',Georgia,serif;font-style:italic;">Odadan Çıkarıldın</h4>
        <p style="color:#777;font-size:0.9rem;line-height:1.6;">Moderatör tarafından bu odadan çıkarıldın.<br>Rooms sayfasına yönlendiriliyorsun...</p>
        <div style="margin-top:16px;height:4px;background:#f0f0f0;border-radius:4px;overflow:hidden;">
            <div style="height:100%;width:100%;background:linear-gradient(135deg,#e74c3c,#c0392b);animation:shrink 3s linear forwards;border-radius:4px;"></div>
        </div>
    </div>
</div>

<!-- KULLANIM SÖZLEŞMESİ -->
<div id="agreementOverlay" style="display:flex;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.65);z-index:99998;align-items:center;justify-content:center;">
    <div style="background:white;border-radius:22px;padding:40px 36px;max-width:500px;width:92%;box-shadow:0 24px 70px rgba(0,0,0,0.3);">
        <div style="text-align:center;margin-bottom:22px;">
            <div style="font-size:2.8rem;">📋</div>
            <h4 style="font-family:'Playfair Display',Georgia,serif;font-style:italic;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:10px;font-size:1.5rem;">Kullanım Kuralları</h4>
        </div>
        <div style="background:rgba(102,126,234,0.06);border-radius:14px;padding:20px 24px;margin-bottom:24px;border:1.5px solid rgba(102,126,234,0.12);">
            <p style="color:#444;font-size:0.92rem;line-height:1.9;margin:0;">
                🚫 <strong>Hakaret ve küçük düşürücü dil</strong> kesinlikle yasaktır.<br>
                🔒 <strong>Kişisel bilgi paylaşımı</strong> (telefon, adres, kimlik) ban sebebidir.<br>
                🤝 Saygılı ve yapıcı bir iletişim ortamı herkesin sorumluluğudur.<br>
                ⚠️ Kurallara uymayan kullanıcılar moderatör tarafından <strong>atılabilir veya banlanabilir</strong>.
            </p>
        </div>
        <div style="text-align:center;">
            <button onclick="acceptAgreement()" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;padding:13px 40px;font-size:1rem;font-weight:600;cursor:pointer;box-shadow:0 4px 18px rgba(102,126,234,0.35);">
                ✅ Okudum, Kabul Ediyorum
            </button>
        </div>
    </div>
</div>

<style>
@keyframes shrink { from { width:100%; } to { width:0%; } }
</style>

<script>
function acceptAgreement() {
    sessionStorage.setItem('agreed_{{ room.id }}', '1');
    document.getElementById('agreementOverlay').style.display = 'none';
}
window.onload = function() {
    if (!sessionStorage.getItem('agreed_{{ room.id }}')) {
        document.getElementById('agreementOverlay').style.display = 'flex';
    }
};
</script>

{% endblock %}'''

html = html.replace(old_end, new_end)

with open('core/templates/room_detail.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("room_detail.html guncellendi!")
print("\nTUM ISLEMLER TAMAMLANDI!") 
