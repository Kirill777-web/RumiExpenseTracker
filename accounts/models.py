from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

PROFESSION_CHOICES = [
    ('Student', 'Student'),
    ('Employee', 'Employee'),
    ('Business', 'Business'),
    ('Other', 'Other'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES)
    savings = models.IntegerField(null=True, blank=True)
    income = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
