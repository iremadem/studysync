from django.forms import ModelForm
from .models import StudyRoom

class RoomForm(ModelForm):
    class Meta:
        model = StudyRoom
        fields = ['title', 'subject', 'description']