from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import StudyRoom, Message, Note
from .forms import RoomForm


def home(request):
    return render(request, 'home.html')


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


def room_list(request):
    query = request.GET.get('q')
    if query:
        free_rooms = StudyRoom.objects.filter(title__icontains=query, is_premium_room=False)
        premium_rooms_list = StudyRoom.objects.filter(title__icontains=query, is_premium_room=True)
    else:
        free_rooms = StudyRoom.objects.filter(is_premium_room=False)
        premium_rooms_list = StudyRoom.objects.filter(is_premium_room=True)

    try:
        is_premium = request.user.is_authenticated and request.user.userprofile.is_premium
    except:
        is_premium = False

    return render(request, 'rooms.html', {
        'rooms': free_rooms,
        'premium_rooms_list': premium_rooms_list,
        'is_premium': is_premium,
    })


def create_room(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')

    try:
        is_premium = request.user.userprofile.is_premium
    except:
        is_premium = False

    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.is_premium_room = is_premium or request.user.is_staff
            if room.is_premium_room:
                import random, string
                while True:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    from .models import StudyRoom as SR
                    if not SR.objects.filter(invite_code=code).exists():
                        room.invite_code = code
                        break
            room.save()
            return redirect('rooms')

    return render(request, 'create_room.html', {'form': form, 'is_premium': is_premium})


# 🔥 ROOM DETAIL (CHAT + NOTES)
def room_detail(request, pk):
    room = get_object_or_404(StudyRoom, id=pk)

    if not request.user.is_authenticated:
        return render(request, 'must_login.html')

    # Premium oda erişim kontrolü
    if room.is_premium_room and not request.user.is_staff:
        try:
            is_premium = request.user.userprofile.is_premium
        except:
            is_premium = False
        # Invite code ile giriş?
        invite = request.GET.get('invite', '').strip().upper()
        already_invited = room.participants.filter(id=request.user.id).exists() and not room.creator == request.user
        if not is_premium and not (invite and invite == room.invite_code) and room.creator != request.user and not already_invited:
            return render(request, 'premium_gate.html', {'room': room})

    # kullanıcıyı ekle
    room.participants.add(request.user)

    # note oluştur / getir
    note, created = Note.objects.get_or_create(room=room)

    # 🔥 CHAT AJAX
    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            msg = Message.objects.create(
                user=request.user,
                room=room,
                content=content
            )

            return JsonResponse({
                "username": request.user.username,
                "content": msg.content
            })

    messages = Message.objects.filter(room=room)
    is_creator = (room.creator == request.user or request.user.is_staff)
    from .models import SharedFile
    shared_files = SharedFile.objects.filter(room=room).order_by('-uploaded_at') if room.is_premium_room else []

    return render(request, 'room_detail.html', {
        'room': room,
        'messages': messages,
        'participants': room.participants.all(),
        'notes': note.content,
        'is_creator': is_creator,
        'shared_files': shared_files,
    })




def kick_participant(request, room_pk, user_pk):
    from django.contrib.auth.models import User
    from django.core.cache import cache
    room = get_object_or_404(StudyRoom, id=room_pk)
    if request.user != room.creator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        user_to_kick = get_object_or_404(User, id=user_pk)
        room.participants.remove(user_to_kick)
        # Cache'e kick sinyali yaz — kullanıcı polling ile okuyacak
        cache.set(f'kick_signal_{room_pk}_{user_pk}', True, timeout=60)
        # KickLog kaydet
        from .models import KickLog
        KickLog.objects.create(
            room=room,
            kicked_by=request.user,
            kicked_user=user_to_kick,
        )
        return JsonResponse({'status': 'ok', 'kicked': user_to_kick.username})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def check_kick(request, room_pk):
    """Kullanıcı kendisinin kick edilip edilmediğini kontrol eder."""
    if not request.user.is_authenticated:
        return JsonResponse({'kicked': False})
    from django.core.cache import cache
    key = f'kick_signal_{room_pk}_{request.user.id}'
    kicked = cache.get(key, False)
    if kicked:
        cache.delete(key)
    return JsonResponse({'kicked': kicked})

# 🔥 NOTES SAVE (BU EKSİKTİ)
def save_notes(request, pk):
    room = get_object_or_404(StudyRoom, id=pk)
    note, created = Note.objects.get_or_create(room=room)

    if request.method == "POST":
        content = request.POST.get("content")
        note.content = content
        note.save()
        return JsonResponse({"status": "ok"})

def documentation(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import StudyRoom
    rooms = StudyRoom.objects.all()
    is_admin = request.user.is_staff
    try:
        is_premium = request.user.userprofile.is_premium
    except:
        is_premium = False
    return render(request, 'documentation.html', {
        'rooms': rooms,
        'is_admin': is_admin,
        'is_premium': is_premium,
    })


def pricing(request):
    from .models import PricingPlan
    plans = PricingPlan.objects.all()
    # DB boşsa varsayılan planları oluştur
    if not plans.exists():
        PricingPlan.objects.create(
            key='weekly', name='Weekly', price=49, period='week',
            icon='⚡', order=1,
            features='Premium course notes\nPremium video resources\nExclusive premium rooms',
            has_priority_support=False, is_popular=False,
        )
        PricingPlan.objects.create(
            key='monthly', name='Monthly', price=149, period='month',
            icon='🚀', order=2,
            features='Premium course notes\nPremium video resources\nExclusive premium rooms\nPriority support',
            has_priority_support=True, is_popular=True,
        )
        PricingPlan.objects.create(
            key='yearly', name='Yearly', price=999, period='year',
            icon='👑', order=3,
            features='Premium course notes\nPremium video resources\nExclusive premium rooms\nPriority support',
            has_priority_support=True, is_popular=False,
            promo_text='🎁 2 months free!',
        )
        plans = PricingPlan.objects.all()
    return render(request, 'premium.html', {'plans': plans})


def edit_plan(request, plan_key):
    from .models import PricingPlan
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')
    plan = PricingPlan.objects.get(key=plan_key)
    if request.method == 'POST':
        plan.name = request.POST.get('name', plan.name)
        plan.price = request.POST.get('price', plan.price)
        plan.period = request.POST.get('period', plan.period)
        plan.icon = request.POST.get('icon', plan.icon)
        plan.features = request.POST.get('features', plan.features)
        plan.promo_text = request.POST.get('promo_text', plan.promo_text)
        plan.is_popular = request.POST.get('is_popular') == 'on'
        plan.has_priority_support = request.POST.get('has_priority_support') == 'on'
        plan.save()
        return redirect('pricing')
    return render(request, 'edit_plan.html', {'plan': plan})


def premium_rooms(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import EducatorRequest
    educator_requests = EducatorRequest.objects.filter(status='pending').select_related('user') if request.user.is_staff else []
    return render(request, 'premium_rooms.html', {
        'is_admin': request.user.is_staff,
        'educator_requests': educator_requests,
    })


PREMIUM_ROOMS = {
    'math': {
        'id': 'math',
        'title': '1-on-1 Mathematics Room',
        'description': 'Private math sessions with a dedicated tutor. Ask questions instantly and get real-time explanations.',
        'icon': '🧑‍🏫',
        'color': '#667eea',
        'gradient': 'linear-gradient(135deg, #667eea, #764ba2)',
        'duration': '60 min',
    },
    'physics': {
        'id': 'physics',
        'title': '1-on-1 Physics Room',
        'description': 'Solve physics problems step by step. Focus on formulas, experiments, and proven problem-solving techniques.',
        'icon': '🔬',
        'color': '#f5576c',
        'gradient': 'linear-gradient(135deg, #f093fb, #f5576c)',
        'duration': '60 min',
    },
    'programming': {
        'id': 'programming',
        'title': '1-on-1 Programming Room',
        'description': 'One-on-one mentorship in Python, Java, or web development. Project-based learning tailored to your level.',
        'icon': '💻',
        'color': '#4facfe',
        'gradient': 'linear-gradient(135deg, #4facfe, #00f2fe)',
        'duration': '90 min',
    },
    'literature': {
        'id': 'literature',
        'title': '1-on-1 Literature Room',
        'description': 'Private support for essay writing, poetry analysis, and grammar. Tailored exam preparation with expert guidance.',
        'icon': '📚',
        'color': '#43e97b',
        'gradient': 'linear-gradient(135deg, #43e97b, #38f9d7)',
        'duration': '60 min',
    },
}

def premium_room_detail(request, room_id):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    if not request.user.is_staff:
        try:
            profile = request.user.userprofile
            if not profile.is_premium:
                return render(request, 'must_login.html')
        except:
            return render(request, 'must_login.html')
    room = PREMIUM_ROOMS.get(room_id)
    if not room:
        from django.http import Http404
        raise Http404
    return render(request, 'premium_room_detail.html', {'room': room})


def admin_panel(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, 'admin_panel.html')
    from django.contrib.auth.models import User
    from .models import StudyRoom, UserProfile, PremiumRequest, EducatorRequest, LessonRoom, TutorRequest

    # Stats
    total_users = User.objects.count()
    premium_users = UserProfile.objects.filter(is_premium=True).count()
    educator_users = UserProfile.objects.filter(is_educator=True).count()
    total_rooms = StudyRoom.objects.count()
    total_lesson_rooms = LessonRoom.objects.count()
    pending_requests = PremiumRequest.objects.filter(status='pending').order_by('-created_at')
    pending_count = pending_requests.count()
    all_requests = PremiumRequest.objects.all().order_by('-created_at')
    top_rooms = StudyRoom.objects.all().order_by('-id')[:10]
    educator_requests = EducatorRequest.objects.filter(status='pending').select_related('user')
    all_users = User.objects.select_related('userprofile').order_by('-date_joined')
    active_tutor_requests = TutorRequest.objects.filter(is_active=True).select_related('user').order_by('-created_at')
    from .models import KickLog
    kick_logs = KickLog.objects.select_related('kicked_by','kicked_user','room').order_by('-created_at')[:50]
    from .models import YeditepeVerification
    yeditepe_verifications = YeditepeVerification.objects.select_related('user').order_by('-created_at')

    # Analytics veriler
    from django.db.models import Count
    from collections import Counter
    import json as _json

    # Plan dağılımı
    plan_data = list(
        PremiumRequest.objects.filter(status='approved')
        .values('plan').annotate(count=Count('plan')).order_by('-count')
    )
    plan_labels = _json.dumps([p['plan'].capitalize() for p in plan_data])
    plan_counts = _json.dumps([p['count'] for p in plan_data])

    # En çok aranan dersler (TutorRequest subject)
    subject_data = list(
        TutorRequest.objects.values('subject')
        .annotate(count=Count('subject')).order_by('-count')[:8]
    )
    subject_labels = _json.dumps([s['subject'] for s in subject_data])
    subject_counts = _json.dumps([s['count'] for s in subject_data])

    # Oda konularına göre dağılım
    room_subject_data = list(
        StudyRoom.objects.values('subject')
        .annotate(count=Count('subject')).order_by('-count')[:8]
    )
    room_subject_labels = _json.dumps([r['subject'] for r in room_subject_data])
    room_subject_counts = _json.dumps([r['count'] for r in room_subject_data])

    # Kullanıcı tipi dağılımı
    free_users = total_users - premium_users - educator_users
    user_type_labels = _json.dumps(['Free Students', 'Premium Students', 'Educators'])
    user_type_counts = _json.dumps([max(free_users, 0), premium_users, educator_users])

    # Son 7 günde kayıt
    from django.utils import timezone
    import datetime
    today = timezone.now().date()
    daily_regs = []
    daily_labels = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        count = User.objects.filter(date_joined__date=day).count()
        daily_regs.append(count)
        daily_labels.append(day.strftime('%d %b'))
    daily_labels = _json.dumps(daily_labels)
    daily_regs = _json.dumps(daily_regs)

    # Premium vs Free oda oranı
    premium_room_count = StudyRoom.objects.filter(is_premium_room=True).count()
    free_room_count = StudyRoom.objects.filter(is_premium_room=False).count()

    # POST: kullanıcı yönetimi
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        if user_id:
            target = User.objects.get(id=user_id)
            profile, _ = UserProfile.objects.get_or_create(user=target)
            if action == 'toggle_premium':
                profile.is_premium = not profile.is_premium
                profile.save()
            elif action == 'toggle_educator':
                profile.is_educator = not profile.is_educator
                if profile.is_educator and not profile.educator_code:
                    import random, string
                    profile.educator_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                profile.save()
            elif action == 'delete_user':
                target.delete()
            elif action == 'delete_room':
                room_id = request.POST.get('room_id')
                StudyRoom.objects.filter(id=room_id).delete()
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/admin-panel/')

    return render(request, 'admin_panel.html', {
        'total_users': total_users,
        'premium_users': premium_users,
        'educator_users': educator_users,
        'total_rooms': total_rooms,
        'total_lesson_rooms': total_lesson_rooms,
        'pending_requests': pending_requests,
        'pending_count': pending_count,
        'all_requests': all_requests,
        'top_rooms': top_rooms,
        'educator_requests': educator_requests,
        'all_users': all_users,
        'active_tutor_requests': active_tutor_requests,
        'kick_logs': kick_logs,
        'yeditepe_verifications': yeditepe_verifications,
        # Analytics
        'plan_labels': plan_labels,
        'plan_counts': plan_counts,
        'subject_labels': subject_labels,
        'subject_counts': subject_counts,
        'room_subject_labels': room_subject_labels,
        'room_subject_counts': room_subject_counts,
        'user_type_labels': user_type_labels,
        'user_type_counts': user_type_counts,
        'daily_labels': daily_labels,
        'daily_regs': daily_regs,
        'premium_room_count': premium_room_count,
        'free_room_count': free_room_count,
    })


def premium_request(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import PremiumRequest
    from django.contrib import messages
    if request.method == 'POST':
        plan = request.POST.get('plan')
        existing = PremiumRequest.objects.filter(user=request.user, status='pending')
        if existing.exists():
            messages.warning(request, 'You already have a pending request. Please wait for admin approval.')
        else:
            PremiumRequest.objects.create(user=request.user, plan=plan)
            messages.success(request, 'Your request has been received! You will become a premium member after admin approval.')
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


def request_educator(request):
    """Kullanıcı eğitimci olmak için başvurur."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    if request.method == 'POST':
        profile, _ = request.user.userprofile.__class__.objects.get_or_create(user=request.user)
        from .models import EducatorRequest
        if not EducatorRequest.objects.filter(user=request.user, status='pending').exists():
            EducatorRequest.objects.create(user=request.user)
    return redirect('premium-rooms')


def approve_educator(request, req_id):
    """Admin eğitimci başvurusunu onaylar ve kod atar."""
    if not request.user.is_staff:
        return redirect('home')
    from .models import EducatorRequest, UserProfile
    import random, string
    if request.method == 'POST':
        req = EducatorRequest.objects.get(id=req_id)
        profile, _ = UserProfile.objects.get_or_create(user=req.user)
        profile.is_educator = True
        if not profile.educator_code:
            profile.educator_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        profile.save()
        req.status = 'approved'
        req.save()
    return redirect('premium-rooms')


def reject_educator(request, req_id):
    """Admin eğitimci başvurusunu reddeder."""
    if not request.user.is_staff:
        return redirect('home')
    from .models import EducatorRequest
    if request.method == 'POST':
        req = EducatorRequest.objects.get(id=req_id)
        req.status = 'rejected'
        req.save()
    return redirect('premium-rooms')


def enter_premium_room(request, room_id):
    """Koda göre premium odaya erişim kontrolü."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    if request.user.is_staff:
        return redirect('premium-room-detail', room_id=room_id)
    try:
        profile = request.user.userprofile
        if not profile.is_premium:
            return render(request, 'must_login.html')
    except:
        return render(request, 'must_login.html')

    if request.method == 'POST':
        from .models import UserProfile
        code = request.POST.get('code', '').strip().upper()
        # Kod doğrulama: herhangi bir eğitimcinin kodu mu?
        if UserProfile.objects.filter(is_educator=True, educator_code=code).exists():
            return redirect('premium-room-detail', room_id=room_id)
        else:
            room = PREMIUM_ROOMS.get(room_id)
            return render(request, 'enter_premium_room.html', {
                'room': room, 'error': 'Invalid code. Please check with your tutor.'
            })

    room = PREMIUM_ROOMS.get(room_id)
    if not room:
        from django.http import Http404
        raise Http404
    return render(request, 'enter_premium_room.html', {'room': room})

def delete_room(request, pk):
    room = get_object_or_404(StudyRoom, id=pk)
    if request.user != room.creator and not request.user.is_staff:
        return redirect('rooms')
    if request.method == 'POST':
        room.delete()
        return redirect('rooms')
    return redirect('room-detail', pk=pk)


def edit_room(request, pk):
    room = get_object_or_404(StudyRoom, id=pk)
    if request.user != room.creator and not request.user.is_staff:
        return redirect('rooms')
    if request.method == 'POST':
        room.title = request.POST.get('title', room.title).strip()
        room.subject = request.POST.get('subject', room.subject).strip()
        room.description = request.POST.get('description', room.description).strip()
        room.save()
        return redirect('room-detail', pk=pk)
    return render(request, 'edit_room.html', {'room': room})

def ai_assistant(request, room_pk):
    """Premium odalarda AI Study Assistant — Groq API."""
    import json, urllib.request, urllib.error
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    data = json.loads(request.body)
    question = data.get('question', '').strip()
    if not question:
        return JsonResponse({'error': 'No question'}, status=400)

    room = get_object_or_404(StudyRoom, id=room_pk)

    # settings.py'den Groq key oku
    try:
        from django.conf import settings
        api_key = settings.ANTHROPIC_API_KEY
    except:
        api_key = ''

    if not api_key:
        return JsonResponse({'error': 'AI key not configured.'}, status=500)

    # OpenRouter API - free models
    payload = json.dumps({
        'model': 'openrouter/auto',
        'messages': [
            {'role': 'system', 'content': f"You are an expert study assistant in a '{room.subject}' study room. Give clear, concise, educational answers. Use examples when helpful."},
            {'role': 'user', 'content': question}
        ],
        'max_tokens': 1000,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key,
            'HTTP-Referer': 'https://studysync.app',
            'X-Title': 'StudySync AI Assistant',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            answer = result['choices'][0]['message']['content']
            return JsonResponse({'answer': answer})
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return JsonResponse({'error': f'API error {e.code}: {body}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def post_tutor_request(request):
    """Premium üye ders ilanı verir."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    try:
        if not request.user.userprofile.is_premium and not request.user.is_staff:
            return JsonResponse({'error': 'Premium required'}, status=403)
    except:
        return JsonResponse({'error': 'Premium required'}, status=403)

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        if not subject:
            return JsonResponse({'error': 'Subject required'}, status=400)
        from .models import TutorRequest
        TutorRequest.objects.filter(user=request.user, is_active=True).update(is_active=False)
        tr = TutorRequest.objects.create(user=request.user, subject=subject, description=description)
        return JsonResponse({'status': 'ok', 'id': tr.id})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def get_tutor_requests(request):
    """Eğiticiler aktif ilan listesini çeker."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    try:
        if not request.user.userprofile.is_educator and not request.user.is_staff:
            return JsonResponse({'error': 'Educator required'}, status=403)
    except:
        return JsonResponse({'error': 'Educator required'}, status=403)
    from .models import TutorRequest
    requests_qs = TutorRequest.objects.filter(is_active=True).order_by('-created_at').select_related('user')
    data = [{'id': r.id, 'username': r.user.username, 'subject': r.subject, 'description': r.description, 'created_at': r.created_at.strftime('%H:%M')} for r in requests_qs]
    return JsonResponse({'requests': data})

def media_control(request, room_pk):
    """Creator başka bir kullanıcının kamera/mikrofonu kapatabilir (sinyal gönderir)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    import json
    room = get_object_or_404(StudyRoom, id=room_pk)
    if request.user != room.creator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        target_user_id = data.get('user_id')
        action = data.get('action')  # 'mute_mic', 'mute_cam', 'kick'
        # Session'a sinyal yaz — client polling ile okuyacak
        from django.core.cache import cache
        cache.set(f'media_control_{room_pk}_{target_user_id}', action, timeout=30)
        return JsonResponse({'status': 'ok', 'action': action})
    return JsonResponse({'error': 'Invalid'}, status=405)


def check_media_control(request, room_pk):
    """Kullanıcı kendi için sinyal olup olmadığını kontrol eder."""
    if not request.user.is_authenticated:
        return JsonResponse({'action': None})
    from django.core.cache import cache
    key = f'media_control_{room_pk}_{request.user.id}'
    action = cache.get(key)
    if action:
        cache.delete(key)
    return JsonResponse({'action': action})

def upload_file(request, room_pk):
    room = get_object_or_404(StudyRoom, id=room_pk)
    if not request.user.is_authenticated or not room.is_premium_room:
        return JsonResponse({'error': 'Not allowed'}, status=403)
    if request.method == 'POST' and request.FILES.get('file'):
        from .models import SharedFile
        f = request.FILES['file']
        if f.size > 20 * 1024 * 1024:  # 20MB limit
            return JsonResponse({'error': 'File too large (max 20MB)'}, status=400)
        sf = SharedFile.objects.create(
            room=room,
            uploaded_by=request.user,
            file=f,
            original_name=f.name,
        )
        return JsonResponse({
            'status': 'ok',
            'id': sf.id,
            'name': sf.original_name,
            'url': sf.file.url,
            'username': request.user.username,
            'uploaded_at': sf.uploaded_at.strftime('%H:%M'),
        })
    return JsonResponse({'error': 'Invalid'}, status=400)


def delete_file(request, room_pk, file_pk):
    from .models import SharedFile
    room = get_object_or_404(StudyRoom, id=room_pk)
    sf = get_object_or_404(SharedFile, id=file_pk, room=room)
    if request.user != sf.uploaded_by and request.user != room.creator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        sf.file.delete()
        sf.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid'}, status=405)

# ── LESSON ROOMS (EDUCATOR) ──

def lesson_rooms(request):
    """Live Tutoring sayfası — hem eski premium_rooms hem educator odaları."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import LessonRoom, EducatorRequest, TutorRequest
    try:
        profile = request.user.userprofile
        is_premium = profile.is_premium
        is_educator = profile.is_educator
    except:
        is_premium = False
        is_educator = False
    is_admin = request.user.is_staff

    lesson_rooms_list = LessonRoom.objects.filter(is_active=True).select_related('educator')
    educator_requests = EducatorRequest.objects.filter(status='pending').select_related('user') if is_admin else []
    tutor_requests = TutorRequest.objects.filter(is_active=True).order_by('-created_at').select_related('user') if (is_educator or is_admin) else []

    return render(request, 'lesson_rooms.html', {
        'lesson_rooms': lesson_rooms_list,
        'is_premium': is_premium,
        'is_educator': is_educator,
        'is_admin': is_admin,
        'educator_requests': educator_requests,
        'tutor_requests': tutor_requests,
    })


def create_lesson_room(request):
    """Educator veya admin yeni ders odası oluşturur."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    # Admin her zaman girebilir
    if not request.user.is_staff:
        try:
            if not request.user.userprofile.is_educator:
                return redirect('lesson-rooms')
        except:
            return redirect('lesson-rooms')

    if request.method == 'POST':
        import random, string
        from .models import LessonRoom
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not LessonRoom.objects.filter(invite_code=code).exists():
                break
        room = LessonRoom.objects.create(
            educator=request.user,
            title=request.POST.get('title', '').strip(),
            subject=request.POST.get('subject', '').strip(),
            description=request.POST.get('description', '').strip(),
            max_students=int(request.POST.get('max_students', 2)),
            duration_minutes=int(request.POST.get('duration_minutes', 60)),
            allow_camera=bool(request.POST.get('allow_camera')),
            allow_mic=bool(request.POST.get('allow_mic')),
            allow_chat=bool(request.POST.get('allow_chat')),
            allow_notes=bool(request.POST.get('allow_notes')),
            allow_files=bool(request.POST.get('allow_files')),
            invite_code=code,
        )
        # Bildirim: eğer tutor request'e karşılık oluştuysa öğrenciye bildir
        request_id = request.POST.get('request_id', '')
        if request_id:
            try:
                from .models import TutorRequest, Notification
                tutor_req = TutorRequest.objects.get(id=request_id)
                Notification.objects.create(
                    user=tutor_req.user,
                    message=f'🎓 An educator has opened a tutoring room for your "{tutor_req.subject}" request! Educator: {request.user.username}',
                    link=f'/lesson-rooms/{room.id}/',
                )
                tutor_req.is_active = False
                tutor_req.save()
            except Exception:
                pass
        return redirect('lesson-rooms')

    # GET: URL'den pre-fill parametrelerini al
    request_id = request.GET.get('request_id', '')
    prefill = {
        'subject': request.GET.get('subject', ''),
        'title': request.GET.get('title', ''),
        'request_id': request_id,
    }
    return render(request, 'create_lesson_room.html', {'prefill': prefill})


def edit_lesson_room(request, room_pk):
    """Educator ders odasını düzenler."""
    from .models import LessonRoom
    room = get_object_or_404(LessonRoom, id=room_pk)
    if request.user != room.educator and not request.user.is_staff:
        return redirect('lesson-rooms')
    if request.method == 'POST':
        room.title = request.POST.get('title', room.title).strip()
        room.subject = request.POST.get('subject', room.subject).strip()
        room.description = request.POST.get('description', room.description).strip()
        room.max_students = int(request.POST.get('max_students', room.max_students))
        room.duration_minutes = int(request.POST.get('duration_minutes', room.duration_minutes))
        room.allow_camera = bool(request.POST.get('allow_camera'))
        room.allow_mic = bool(request.POST.get('allow_mic'))
        room.allow_chat = bool(request.POST.get('allow_chat'))
        room.allow_notes = bool(request.POST.get('allow_notes'))
        room.allow_files = bool(request.POST.get('allow_files'))
        room.is_active = bool(request.POST.get('is_active'))
        room.save()
        return redirect('lesson-rooms')
    return render(request, 'create_lesson_room.html', {'room': room})


def delete_lesson_room(request, room_pk):
    from .models import LessonRoom
    room = get_object_or_404(LessonRoom, id=room_pk)
    if request.user != room.educator and not request.user.is_staff:
        return redirect('lesson-rooms')
    if request.method == 'POST':
        room.delete()
    return redirect('lesson-rooms')


def lesson_room_detail(request, room_pk):
    """Ders odası detay sayfası."""
    from .models import LessonRoom
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    room = get_object_or_404(LessonRoom, id=room_pk)

    # Erişim kontrolü: educator, admin, premium, veya invite code
    try:
        profile = request.user.userprofile
        is_premium = profile.is_premium
        is_educator = profile.is_educator
    except:
        is_premium = False
        is_educator = False

    # Erişim: educator kendi odası ve admin direkt girer
    # Premium öğrenci ve diğer educatorlar invite code ile girer
    invite = request.GET.get('invite', '').strip().upper()
    is_room_educator = (request.user == room.educator)

    if is_room_educator or request.user.is_staff:
        # Educator ve admin direkt girer
        pass
    elif invite and invite == room.invite_code:
        # Geçerli kod ile girer
        pass
    else:
        # Herkes (premium dahil) koda ihtiyaç duyar
        error = 'Invalid invite code.' if invite else None
        return render(request, 'lesson_gate.html', {'room': room, 'error': error})

    is_owner = (request.user == room.educator or request.user.is_staff)

    # Katılımcıları cache'e kaydet
    from django.core.cache import cache
    participants_key = f'lesson_room_participants_{room.id}'
    participants = cache.get(participants_key, {})
    participants[request.user.id] = {
        'username': request.user.username,
        'id': request.user.id,
    }
    cache.set(participants_key, participants, timeout=3600)

    # Educator olmayan katılımcılar
    participant_list = [p for uid, p in participants.items() if uid != room.educator.id]

    return render(request, 'lesson_room_detail.html', {
        'room': room,
        'is_owner': is_owner,
        'participant_list': participant_list,
        'current_user_id': request.user.id,
    })


# ── DOCUMENTATION CREATE (EDUCATOR) ──

def documentation(request):
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    from .models import StudyRoom, DocumentationContent
    is_admin = request.user.is_staff
    try:
        profile = request.user.userprofile
        is_premium = profile.is_premium
        is_educator = profile.is_educator
    except:
        is_premium = False
        is_educator = False

    doc_contents = DocumentationContent.objects.all() if (is_premium or is_educator or is_admin) else None
    rooms = StudyRoom.objects.all()
    return render(request, 'documentation.html', {
        'rooms': rooms,
        'is_admin': is_admin,
        'is_premium': is_premium,
        'is_educator': is_educator,
        'doc_contents': doc_contents,
    })


def create_doc_content(request):
    """Educator veya admin doküman içeriği oluşturur."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')
    if not request.user.is_staff:
        try:
            if not request.user.userprofile.is_educator:
                return redirect('documentation')
        except:
            return redirect('documentation')

    if request.method == 'POST':
        from .models import DocumentationContent
        DocumentationContent.objects.create(
            created_by=request.user,
            content_type=request.POST.get('content_type', 'note'),
            subject=request.POST.get('subject', '').strip(),
            title=request.POST.get('title', '').strip(),
            body=request.POST.get('body', '').strip(),
            video_url=request.POST.get('video_url', '').strip(),
            is_premium=bool(request.POST.get('is_premium', True)),
        )
        return redirect('documentation')
    return render(request, 'create_doc_content.html')


def delete_doc_content(request, content_pk):
    from .models import DocumentationContent
    obj = get_object_or_404(DocumentationContent, id=content_pk)
    if request.user != obj.created_by and not request.user.is_staff:
        return redirect('documentation')
    if request.method == 'POST':
        obj.delete()
    return redirect('documentation')

def notifications(request):
    """Kullanıcının bildirimlerini döndürür."""
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})
    from .models import Notification
    notifs = Notification.objects.filter(user=request.user, is_read=False)[:15]
    data = [{
        'id': n.id,
        'message': n.message,
        'link': n.link,
        'type': n.notification_type,
        'created_at': n.created_at.strftime('%H:%M'),
    } for n in notifs]
    return JsonResponse({'notifications': data, 'count': len(data)})


def mark_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error'})
    from .models import Notification
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


def send_to_educator(request):
    """Premium öğrenci educator'a kod isteği gönderir."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    if request.method == 'POST':
        import json
        from .models import LessonRoom, Notification
        data = json.loads(request.body)
        room_id = data.get('room_id')
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Message is empty'}, status=400)
        try:
            room = LessonRoom.objects.get(id=room_id)
            Notification.objects.create(
                user=room.educator,
                from_user=request.user,
                notification_type='join_request',
                room_id=room.id,
                message=f'📩 {request.user.username} wants to join your "{room.title}" session: "{message}"',
                link=f'/lesson-rooms/{room.id}/',
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def respond_join_request(request):
    """Educator join request'i kabul veya reddeder."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    if request.method == 'POST':
        import json
        from .models import Notification, LessonRoom
        data = json.loads(request.body)
        notif_id = data.get('notif_id')
        action = data.get('action')  # 'accept' or 'reject'
        try:
            notif = Notification.objects.get(id=notif_id, user=request.user, notification_type='join_request')
            student = notif.from_user
            room = LessonRoom.objects.get(id=notif.room_id)
            # Bildirimi okundu yap
            notif.is_read = True
            notif.save()
            if action == 'accept':
                Notification.objects.create(
                    user=student,
                    notification_type='join_accepted',
                    from_user=request.user,
                    room_id=room.id,
                    message=f'✅ {request.user.username} accepted your request! Join "{room.title}" with code: {room.invite_code}',
                    link=f'/lesson-rooms/{room.id}/?invite={room.invite_code}',
                )
                return JsonResponse({'status': 'ok', 'action': 'accept'})
            elif action == 'reject':
                Notification.objects.create(
                    user=student,
                    notification_type='join_rejected',
                    from_user=request.user,
                    room_id=room.id,
                    message=f'❌ {request.user.username} declined your request to join "{room.title}".',
                    link='',
                )
                return JsonResponse({'status': 'ok', 'action': 'reject'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def kick_lesson_participant(request, room_pk, user_pk):
    """Educator ders odasından kullanıcı atar."""
    from .models import LessonRoom
    room = get_object_or_404(LessonRoom, id=room_pk)
    if request.user != room.educator and not request.user.is_staff:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    if request.method == 'POST':
        from django.core.cache import cache
        from django.contrib.auth.models import User
        # Cache'den çıkar
        participants_key = f'lesson_room_participants_{room.id}'
        participants = cache.get(participants_key, {})
        if user_pk in participants:
            del participants[user_pk]
            cache.set(participants_key, participants, timeout=3600)
        # Media control ile kick sinyali gönder
        cache.set(f'media_control_{room_pk}_{user_pk}', 'kick', timeout=30)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid'}, status=405)


def lesson_participants(request, room_pk):
    """Ders odası katılımcı listesini döndürür."""
    from django.core.cache import cache
    participants_key = f'lesson_room_participants_{room_pk}'
    participants = cache.get(participants_key, {})
    return JsonResponse({'participants': list(participants.values())})

# ── DIRECT MESSAGES ──

def dm_users(request):
    """Kullanıcı listesi ve arama."""
    if not request.user.is_authenticated:
        return JsonResponse({'users': []})
    from django.contrib.auth.models import User
    from .models import DirectMessage
    from django.db.models import Count as DmCount
    q = request.GET.get('q', '').strip()
    users = User.objects.exclude(id=request.user.id).select_related('userprofile')
    if q:
        users = users.filter(username__icontains=q)
    users = list(users[:30])
    # Okunmamış mesaj sayısı
    unread_qs = DirectMessage.objects.filter(
        receiver=request.user, is_read=False
    ).values('sender_id').annotate(count=DmCount('id'))
    unread_map = {u['sender_id']: u['count'] for u in unread_qs}

    def get_tag(u):
        try:
            if u.is_staff: return 'Moderator'
            if u.userprofile.is_educator: return 'Educator'
            if u.userprofile.is_premium: return 'Premium Student'
        except:
            pass
        return 'Student'

    data = [{
        'id': u.id,
        'username': u.username,
        'unread': unread_map.get(u.id, 0),
        'tag': get_tag(u),
    } for u in users]
    return JsonResponse({'users': data})


def dm_messages(request, user_id):
    """İki kullanıcı arasındaki mesajlar."""
    if not request.user.is_authenticated:
        return JsonResponse({'messages': []})
    from django.contrib.auth.models import User
    from .models import DirectMessage
    from django.db.models import Q
    other = User.objects.get(id=user_id)
    qs = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    ).order_by('created_at')
    # Önce okundu işaretle, sonra slice
    qs.filter(receiver=request.user, is_read=False).update(is_read=True)
    msgs = qs[:50]
    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'sender_id': m.sender.id,
        'content': m.content,
        'created_at': m.created_at.strftime('%H:%M'),
        'is_me': m.sender_id == request.user.id,
    } for m in msgs]
    return JsonResponse({'messages': data, 'other': other.username})


def dm_send(request):
    """Mesaj gönder."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    if request.method == 'POST':
        import json
        from django.contrib.auth.models import User
        from .models import DirectMessage
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Empty message'}, status=400)
        receiver = User.objects.get(id=receiver_id)
        msg = DirectMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
        )
        return JsonResponse({
            'status': 'ok',
            'id': msg.id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_me': True,
        })
    return JsonResponse({'error': 'Invalid'}, status=405)


def dm_unread_count(request):
    """Toplam okunmamış mesaj sayısı."""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    from .models import DirectMessage
    count = DirectMessage.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})

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

def yeditepe_verify(request):
    """Yeditepe öğrencisi mail ile doğrulama isteği gönderir."""
    if not request.user.is_authenticated:
        return render(request, 'must_login.html')

    from .models import YeditepeVerification
    existing = YeditepeVerification.objects.filter(user=request.user).first()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email.endswith('@std.yeditepe.edu.tr') and not email.endswith('@yeditepe.edu.tr'):
            return render(request, 'yeditepe_verify.html', {
                'error': 'Please enter a valid Yeditepe University email (@std.yeditepe.edu.tr or @yeditepe.edu.tr)',
                'existing': existing,
            })
        if existing:
            existing.email = email
            existing.status = 'pending'
            existing.save()
        else:
            YeditepeVerification.objects.create(user=request.user, email=email)
        return render(request, 'yeditepe_verify.html', {
            'success': True,
            'existing': YeditepeVerification.objects.get(user=request.user),
        })

    return render(request, 'yeditepe_verify.html', {'existing': existing})


def yeditepe_approve(request, verify_id):
    """Admin doğrulamayı onaylar — 1 ay ücretsiz premium verir."""
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        from .models import YeditepeVerification
        import datetime
        from django.utils import timezone
        v = get_object_or_404(YeditepeVerification, id=verify_id)
        v.status = 'approved'
        # Öğretmen (@yeditepe.edu.tr) → ömür boyu, Öğrenci (@std.yeditepe.edu.tr) → 1 ay
        is_teacher = v.email.endswith('@yeditepe.edu.tr') and not v.email.endswith('@std.yeditepe.edu.tr')
        if is_teacher:
            v.expires_at = None  # Ömür boyu
        else:
            v.expires_at = timezone.now() + datetime.timedelta(days=30)
        v.save()
        # Premium ver
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=v.user)
        profile.is_premium = True
        profile.save()
        # Bildirim gönder
        from .models import Notification
        if is_teacher:
            msg = '🎉 Your Yeditepe University faculty email has been verified! You have been granted LIFETIME FREE Premium access. Welcome!'
        else:
            msg = '🎉 Your Yeditepe University email has been verified! You have been granted 1 month of FREE Premium access. Enjoy!'
        Notification.objects.create(
            user=v.user,
            notification_type='general',
            message=msg,
            link='/premium/',
        )
    return redirect('admin_panel')


def yeditepe_reject(request, verify_id):
    """Admin doğrulamayı reddeder."""
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        from .models import YeditepeVerification
        v = get_object_or_404(YeditepeVerification, id=verify_id)
        v.status = 'rejected'
        v.save()
        from .models import Notification
        Notification.objects.create(
            user=v.user,
            notification_type='general',
            message=f'❌ Your Yeditepe University email verification was rejected. Please make sure you used a valid @std.yeditepe.edu.tr email.',
            link='/verify-yeditepe/',
        )
    return redirect('admin-panel')
