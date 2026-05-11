from django.contrib import admin
from .models import StudyRoom, Message, PomodoroSession

admin.site.register(StudyRoom)
admin.site.register(Message)
admin.site.register(PomodoroSession)
from .models import UserProfile
admin.site.register(UserProfile)

from .models import PremiumRequest
admin.site.register(PremiumRequest)
