# faceapp/models.py
from django.db import models
from django.contrib.auth.models import User

def user_face_path(instance, filename):
    return f"faces/user_{instance.user.id}/{filename}"

class FaceSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="face_samples")
    image = models.ImageField(upload_to=user_face_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} sample {self.id}"
