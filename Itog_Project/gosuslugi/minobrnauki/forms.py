from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Application
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    # Поле для логина
    username = forms.CharField(
        label="Логин",
        max_length=150,
        help_text="Обязательное поле. Только буквы, цифры и символы @/./+/-/_.",
        widget=forms.TextInput(attrs={'placeholder': 'Логин'})
    )

    # Поле для email
    email = forms.EmailField(
        label="Email",
        max_length=254,
        help_text="Обязательное поле. Введите действующий email.",
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )

    # Поля для личных данных
    first_name = forms.CharField(
        label="Имя",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'})
    )
    middle_name = forms.CharField(
        label="Отчество",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Отчество'})
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'placeholder': 'ДД.ММ.ГГГГ', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        label="Пол",
        choices=[('male', 'Мужской'), ('female', 'Женский')],
        widget=forms.Select()
    )

    # Паспортные данные
    passport_series = forms.CharField(
        label="Серия паспорта",
        max_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'Серия паспорта'})
    )
    passport_number = forms.CharField(
        label="Номер паспорта",
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Номер паспорта'})
    )

    # Адреса
    registration_address = forms.CharField(
        label="Адрес регистрации",
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Адрес регистрации'})
    )
    actual_address = forms.CharField(
        label="Адрес фактического проживания",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Адрес фактического проживания'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'middle_name', 'birth_date', 'gender', 'passport_series', 'passport_number', 'registration_address', 'actual_address', 'password1', 'password2')

    def clean_username(self):
        """Проверка на уникальность логина."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean_email(self):
        """Проверка на уникальность email."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        """Сохранение пользователя и создание профиля."""
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создание профиля пользователя
            profile = UserProfile(
                user=user,
                middle_name=self.cleaned_data['middle_name'],
                birth_date=self.cleaned_data['birth_date'],
                gender=self.cleaned_data['gender'],
                passport_series=self.cleaned_data['passport_series'],
                passport_number=self.cleaned_data['passport_number'],
                registration_address=self.cleaned_data['registration_address'],
                actual_address=self.cleaned_data['actual_address']
            )
            profile.save()
        return user


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=150
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином не найден.")
        return username


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['application_type', 'education_document', 'application_document', 'additional_document']

    def clean_education_document(self):
        document = self.cleaned_data['education_document']
        if not document.name.endswith('.pdf'):
            raise ValidationError("Документ должен быть в формате PDF.")
        return document

    def clean_application_document(self):
        document = self.cleaned_data['application_document']
        if not document.name.endswith('.pdf'):
            raise ValidationError("Документ должен быть в формате PDF.")
        return document

    def clean_additional_document(self):
        document = self.cleaned_data['additional_document']
        if document and not document.name.endswith('.pdf'):
            raise ValidationError("Документ должен быть в формате PDF.")
        return document