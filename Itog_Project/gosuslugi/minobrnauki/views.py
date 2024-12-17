from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, ForgotPasswordForm, ApplicationForm
from .models import Application, UserProfile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .weather import get_location_by_ip, get_yandex_weather
from datetime import timedelta, datetime
from django.db.models import Count
from django.views.decorators.cache import cache_page

import matplotlib.pyplot as plt
import io
import base64
from django.contrib.auth.decorators import user_passes_test

import matplotlib
matplotlib.use('Agg')


def register(request):
    if request.method == 'POST':
        # Получаем данные из формы
        login = request.POST.get('login')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        birth_date_str = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        passport_series = request.POST.get('passport_series')
        passport_number = request.POST.get('passport_number')
        registration_address = request.POST.get('registration_address')
        actual_address = request.POST.get('actual_address')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Проверка на совпадение паролей
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html', {'form_data': request.POST})

        # Проверка на уникальность логина
        if User.objects.filter(username=login).exists():
            messages.error(request, 'Пользователь с таким логином уже существует')
            return render(request, 'register.html', {'form_data': request.POST})

        # Проверка на уникальность email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'register.html', {'form_data': request.POST})

        # Преобразуем дату из формата день.месяц.год в YYYY-MM-DD
        try:
            birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Неверный формат даты. Используйте формат день.месяц.год')
            return render(request, 'register.html', {'form_data': request.POST})

        # Проверка чекбокса "Совпадает с адресом регистрации"
        same_address = request.POST.get('same_address')
        if same_address:
            actual_address = registration_address
        else:
            if not actual_address:
                actual_address = "Не указан"

        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=login,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                middle_name=middle_name,
                birth_date=birth_date,
                gender=gender,
                passport_series=passport_series,
                passport_number=passport_number,
                registration_address=registration_address,
                actual_address=actual_address
            )

            # Успешная регистрация
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('registration_success')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {e}')
            return render(request, 'register.html', {'form_data': request.POST})

    return render(request, 'register.html')


def registration_success(request):
    return render(request, 'registration_success.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Проверка существования пользователя
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким логином не найден')
            return render(request, 'forgot_password.html')

        # Если пользователь существует, переходим ко второму этапу
        if user:
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            # Проверка совпадения паролей
            if new_password1 != new_password2:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'forgot_password.html')

            # Изменение пароля
            user.password = make_password(new_password1)
            user.save()

            # Успешное изменение пароля
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('login')  # Перенаправляем на страницу входа

    return render(request, 'forgot_password.html')


def home(request):
    return render(request, 'home.html')


def profile(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'profile.html', {'applications': applications})


def applications(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'applications.html', {'applications': applications})


def submit_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return render(request, 'success.html')
    else:
        form = ApplicationForm()

    # Получаем данные из таблиц User и UserProfile
    user = request.user
    try:
        profile = user.userprofile  # Связь через OneToOneField
    except UserProfile.DoesNotExist:
        profile = None

    # Формируем ФИО
    full_name = f"{user.last_name} {user.first_name} {profile.middle_name if profile else ''}"

    # Преобразуем дату рождения в формат ДД.ММ.ГГГГ
    birth_date = profile.birth_date.strftime('%d.%m.%Y') if profile and profile.birth_date else ''

    # Передаем данные в шаблон
    context = {
        'form': form,
        'full_name': full_name,
        'birth_date': birth_date,
        'registration_address': profile.registration_address if profile else '',
        'actual_address': profile.actual_address if profile else '',
    }
    return render(request, 'apply.html', context)


def regulations(request):
    return render(request, 'reglament.html')


def about(request):
    return render(request, 'about.html')


def contacts(request):
    return render(request, 'contacts.html')


def profile(request):
    # Получаем текущего пользователя
    user = request.user

    # Получаем профиль пользователя
    try:
        profile = user.userprofile  # Связь через OneToOneField
    except UserProfile.DoesNotExist:
        # Если профиль не существует, создаем пустой объект
        profile = None

    # Передаем данные в шаблон
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'profile.html', context)


def weather_view(request):
    city = get_location_by_ip()
    weather_data = get_yandex_weather(city)

    if weather_data:
        return render(request, 'weather.html', {'weather_data': weather_data})
    else:
        return render(request, 'weather.html', {'error': 'Не удалось получить данные о погоде.'})


@user_passes_test(lambda u: u.is_superuser)
def admin_analytics(request):
    # График 1: Зарегистрированные пользователи за последние 7 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    user_data = User.objects.filter(date_joined__range=(start_date, end_date)) \
                            .values('date_joined__date') \
                            .annotate(count=Count('id')) \
                            .order_by('date_joined__date')

    # Преобразуем даты в формат ДД.ММ.ГГГГ
    dates = [entry['date_joined__date'].strftime('%d.%m.%Y') for entry in user_data]
    counts = [entry['count'] for entry in user_data]

    # Заменяем значения оси Y на последовательные числа
    y_values = list(range(1, len(counts) + 1))

    plt.figure(figsize=(10, 5))
    plt.plot(dates, y_values, marker='o')
    plt.title('Зарегистрированные пользователи за последние 7 дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество пользователей')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    user_chart = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    # График 2: Количество поданных заявлений по типу
    application_data = Application.objects.values('application_type') \
                                          .annotate(count=Count('id')) \
                                          .order_by('application_type')

    # Преобразуем ключи application_type в их отображаемые значения
    type_choices = dict(Application.application_type.field.choices)
    types = [type_choices[entry['application_type']] for entry in application_data]
    counts = [entry['count'] for entry in application_data]

    # Если нужно взять второе значение (например, 'Получение дубликата'), можно сделать это так:
    if len(types) > 1:
        types = [types[1]]  # Берем второе значение
        counts = [counts[1]]  # Берем второе значение

    # Заменяем значения оси Y на последовательные числа
    y_values = list(range(1, len(counts) + 1))

    plt.figure(figsize=(10, 5))
    plt.bar(types, y_values)
    plt.title('Количество поданных заявлений по типу')
    plt.xlabel('Тип заявления')
    plt.ylabel('Количество')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    application_chart = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    # Передаем графики в шаблон
    context = {
        'user_chart': user_chart,
        'application_chart': application_chart,
    }
    return render(request, 'admin_analytics.html', context)