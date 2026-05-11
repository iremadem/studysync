 # 1. views.py'ye delete_message ekle
with open('core/views.py', 'r', encoding='utf-8') as f:
    views = f.read()

if 'def delete_message' not in views:
    new_view = '''

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
'''
    with open('core/views.py', 'a', encoding='utf-8') as f:
        f.write(new_view)
    print("views.py guncellendi.")
else:
    print("views.py zaten guncelli.")

# 2. urls.py'ye ekle
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls = f.read()

if 'delete-message' not in urls:
    urls = urls.replace(
        "path('room/<int:room_pk>/kick/<int:user_pk>/', views.kick_participant, name='kick-participant'),",
        "path('room/<int:room_pk>/kick/<int:user_pk>/', views.kick_participant, name='kick-participant'),\n    path('room/<int:room_pk>/delete-message/<int:msg_pk>/', views.delete_message, name='delete-message'),"
    )
    with open('core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls)
    print("urls.py guncellendi.")
else:
    print("urls.py zaten guncelli.")

# 3. room_detail.html: mesaj satırına sil butonu ekle
with open('core/templates/room_detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = '''                <div class="chat-msg">
                    <strong>{{ msg.user.username }}</strong>{% user_badge msg.user %}&nbsp; {{ msg.content }}
                </div>'''

new = '''                <div class="chat-msg" id="msg-{{ msg.id }}" style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
                    <div><strong>{{ msg.user.username }}</strong>{% user_badge msg.user %}&nbsp; {{ msg.content }}</div>
                    {% if is_creator %}
                    <button onclick="deleteMsgBtn({{ msg.id }})" style="background:none;border:none;color:#ddd;cursor:pointer;font-size:0.85rem;padding:2px 4px;flex-shrink:0;transition:color 0.2s;" onmouseover="this.style.color='#e74c3c'" onmouseout="this.style.color='#ddd'">🗑</button>
                    {% endif %}
                </div>'''

if 'deleteMsgBtn' not in html:
    html = html.replace(old, new)
    print("Chat mesaj HTML guncellendi.")
else:
    print("HTML zaten guncelli.")

# 4. kickUser fonksiyonunun hemen altına deleteMsgBtn ekle
old_js = '''// ── KICK ──
function kickUser'''

new_js = '''// ── MESAJ SİL ──
function deleteMsgBtn(msgId) {
    fetch('/room/' + ROOM_ID + '/delete-message/' + msgId + '/', {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            var el = document.getElementById('msg-' + msgId);
            if (el) el.remove();
        }
    });
}

// ── KICK ──
function kickUser'''

if 'deleteMsgBtn' not in html:
    html = html.replace(old_js, new_js)
    print("JS guncellendi.")

with open('core/templates/room_detail.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\nTAMAMLANDI!")
