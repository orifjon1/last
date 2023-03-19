from django.db import models
from django.contrib.auth.models import AbstractUser


class Sector(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    Status = (('director', 'Director'),
              ('manager', 'Manager'),
              ('employee', 'Employee'),)

    status = models.CharField(max_length=15, choices=Status, default='employee')
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    shior = models.CharField(max_length=35, blank=True)
    main_task = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    photo = models.ImageField(upload_to='photos', blank=True, null=True)

    def __str__(self):
        return self.username
