from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')])
    passport_series = models.CharField(max_length=4)
    passport_number = models.CharField(max_length=6)
    registration_address = models.CharField(max_length=255)
    actual_address = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        if len(self.passport_series) != 4 or not self.passport_series.isdigit():
            raise ValidationError("Серия паспорта должна состоять из 4 цифр.")
        if len(self.passport_number) != 6 or not self.passport_number.isdigit():
            raise ValidationError("Номер паспорта должен состоять из 6 цифр.")

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application_type = models.CharField(max_length=100, choices=[
        ('title', 'Присвоение ученого звания'),
        ('duplicate', 'Получение дубликата'),
        ('replacement', 'Замена аттестата'),
        ('cancellation', 'Аннулирование звания')
    ])
    education_document = models.FileField(upload_to='documents/')
    application_document = models.FileField(upload_to='documents/')
    additional_document = models.FileField(upload_to='documents/', blank=True, null=True)
    status = models.CharField(max_length=50, default='Отправлено на рассмотрение')

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Заявление {self.id} от {self.user.last_name}"