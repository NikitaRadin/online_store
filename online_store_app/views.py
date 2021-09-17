from django.shortcuts import render, redirect
from online_store_app.forms import UserLoginForm, UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages


def category(request):
    category_id = request.GET.get('category_id', None)
    if category_id == '1':
        context = {'title': 'Одежда',
                   'header': 'Одежда',
                   'subcategories': ['Куртки', 'Джинсы', 'Футболки', 'Шорты', 'Рубашки', 'Брюки', 'Трусы', 'Носки']}
    elif category_id == '2':
        context = {'title': 'Обувь',
                   'header': 'Обувь',
                   'subcategories': ['Ботинки', 'Сандали', 'Туфли', 'Тапки']}
    return render(request, 'category.html', context=context)


def subcategory(request):
    subcategory_id = request.GET.get('subcategory_id', None)
    if subcategory_id == '1':
        context = {'title': 'Подкатегория',
                   'header': 'Подкатегория',
                   'products': ['Первый', 'Второй', 'Третий', 'Четвёртый', 'Пятый', 'Шестой', 'Седьмой', 'Восьмой', 'Девятый']}
    return render(request, 'subcategory.html', context=context)


def product(request):
    product_id = request.GET.get('product_id', None)
    if product_id == '1':
        context = {'title': 'Товар',
                   'header': 'Товар',
                   'images': ['', '', '', '', ''],
                   'description': '''
                   Зарядное устройство UGREEN PD 100 Вт, USB Type C PD, быстрое зарядное устройство с быстрой зарядкой 
                   4,0 3,0 USB для телефона MacBook, ноутбука, смартфона. 
                   Зарядное устройство UGREEN PD 100 Вт, USB Type C PD, быстрое зарядное устройство с быстрой зарядкой 
                   4,0 3,0 USB для телефона MacBook, ноутбука, смартфона. 
                   Зарядное устройство UGREEN PD 100 Вт, USB Type C PD, быстрое зарядное устройство с быстрой зарядкой 
                   4,0 3,0 USB для телефона MacBook, ноутбука, смартфона. 
                   Зарядное устройство UGREEN PD 100 Вт, USB Type C PD, быстрое зарядное устройство с быстрой зарядкой 
                   4,0 3,0 USB для телефона MacBook, ноутбука, смартфона.''',
                   'price': 1000,
                   'currency': 'руб.',
                   'characteristics': [{'name': 'Первая', 'value': 'Первое'},
                                       {'name': 'Вторая', 'value': 'Второе'},
                                       {'name': 'Третья', 'value': 'Третье'},
                                       {'name': 'Четвёртая', 'value': 'Четвёртое'},
                                       {'name': 'Пятая', 'value': 'Пятое'}]}
    return render(request, 'product.html', context=context)


def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(request, request.POST)
        if user_login_form.is_valid():
            username = user_login_form.cleaned_data['username']
            password = user_login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f'Вход в систему под учётной записью {username} успешно завершён')
                return redirect('/category/?category_id=1')
        messages.error(request, 'Введены неверные логин и/или пароль')
    user_login_form = UserLoginForm()
    context = {'title': 'Вход в систему',
               'header': 'Вход в систему',
               'user_login_form': user_login_form}
    return render(request, 'user_login.html', context=context)


def user_registration(request):
    if request.method == 'POST':
        user_registration_form = UserRegistrationForm(request.POST)
        if user_registration_form.is_valid():
            user = user_registration_form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена')
            return redirect('/category/?category_id=1')
        messages.error(request, 'Не удалось завершить регистрацию')
    user_registration_form = UserRegistrationForm()
    context = {'title': 'Регистрация',
               'header': 'Регистрация',
               'user_registration_form': user_registration_form}
    return render(request, 'user_registration.html', context=context)
