from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Admin(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.admin_name

class SubCategory(models.Model):
    is_men = models.BooleanField(default=False)
    is_women = models.BooleanField(default=False)
    is_kids = models.BooleanField(default=False)
    type = models.CharField(max_length=255)
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    video_link = models.URLField(blank=True, null=True)
    is_trending = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    images = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

class Banner(models.Model):
    image = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if Banner.objects.count() >= 3:
            raise ValueError("Only 3 banner images are allowed.")
        super().save(*args, **kwargs)

class Video(models.Model):
    video_link = models.URLField()

    def save(self, *args, **kwargs):
        if Video.objects.count() >= 1:
            raise ValueError("Only one video link is allowed.")
        super().save(*args, **kwargs)

