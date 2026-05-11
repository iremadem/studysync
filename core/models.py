from django.db import models
from django.contrib.auth.models import User

class StudyRoom(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="joined_rooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_premium_room = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=8, blank=True, unique=True, null=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class PomodoroSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.IntegerField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Note(models.Model):
    room = models.OneToOneField(StudyRoom, on_delete=models.CASCADE)
    content = models.TextField(blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    is_premium = models.BooleanField(default=False)
    is_educator = models.BooleanField(default=False)
    educator_code = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Premium' if self.is_premium else 'Free'}"


class PremiumRequest(models.Model):
    PLAN_CHOICES = [
        ('weekly', 'Weekly - 49TL'),
        ('monthly', 'Monthly - 149TL'),
        ('yearly', 'Yearly - 999TL'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_requests')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan} - {self.status}"


class PricingPlan(models.Model):
    key = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='₺')
    period = models.CharField(max_length=20)
    icon = models.CharField(max_length=10, default='⚡')
    features = models.TextField(help_text='One feature per line')
    has_priority_support = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    promo_text = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)

    def features_list(self):
        return [f.strip() for f in self.features.strip().splitlines() if f.strip()]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class EducatorRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educator_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Educator Request - {self.status}"


class TutorRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_requests')
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class SharedFile(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='shared_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='room_files/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} - {self.room.title}"


class LessonRoom(models.Model):
    """Educator'ın oluşturduğu özel ders odaları."""
    educator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_rooms')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_students = models.IntegerField(default=2)
    duration_minutes = models.IntegerField(default=60)
    allow_camera = models.BooleanField(default=True)
    allow_mic = models.BooleanField(default=True)
    allow_chat = models.BooleanField(default=True)
    allow_notes = models.BooleanField(default=True)
    allow_files = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=8, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.educator.username}"


class DocumentationContent(models.Model):
    """Educator'ın oluşturduğu doküman içerikleri."""
    CONTENT_TYPES = [
        ('note', 'Course Note'),
        ('video', 'Video Resource'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doc_contents')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='note')
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    is_premium = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.content_type})"

    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    TYPES = [
        ('general', 'General'),
        ('join_request', 'Join Request'),
        ('join_accepted', 'Join Accepted'),
        ('join_rejected', 'Join Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES, default='general')
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True)
    room_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:40]}"

    class Meta:
        ordering = ['-created_at']


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:30]}"

    class Meta:
        ordering = ['created_at']


class KickLog(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='kick_logs')
    kicked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kicks_given')
    kicked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kicks_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.kicked_user.username} kicked from {self.room.title} by {self.kicked_by.username}"


class YeditepeVerification(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='yeditepe_verification')
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.email} - {self.status}"
