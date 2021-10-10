from online_store_app import models, forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def add_basic_context(context):
    context['categories'] = models.Category.objects.all()


@login_required(login_url='/user_login',
                redirect_field_name=None)
def category(request):
    category_id = request.GET.get('category_id', None)
    try:
        category_ = models.Category.objects.get(id=category_id)
    except models.Category.DoesNotExist:
        return redirect('/category/?category_id=1')
    context = {'title': category_.name,
               'header': category_.name,
               'subcategories': category_.subcategory_set.all()}
    add_basic_context(context)
    return render(request, 'category.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def subcategory(request):
    subcategory_id = request.GET.get('subcategory_id', None)
    try:
        subcategory_ = models.Subcategory.objects.get(id=subcategory_id)
    except models.Subcategory.DoesNotExist:
        return redirect('/category/?category_id=1')
    context = {'title': subcategory_.name,
               'header': subcategory_.name,
               'products': subcategory_.product_set.all()}
    add_basic_context(context)
    return render(request, 'subcategory.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def product(request):
    if request.method == 'POST':
        product_moving_to_from_cart_form = forms.ProductMovingToFromCartForm(request.POST)
        if product_moving_to_from_cart_form.is_valid():
            product_id = product_moving_to_from_cart_form.cleaned_data['product_id']
            try:
                product_ = models.Product.objects.get(id=product_id)
            except models.Product.DoesNotExist:
                return HttpResponse(status=404)
            product_is_in_cart = product_ in request.user.cart.products.all()
            if not product_is_in_cart:
                request.user.cart.products.add(product_)
                return HttpResponse(status=200, content=True)
            else:
                request.user.cart.products.remove(product_)
                return HttpResponse(status=200, content=False)
        else:
            return HttpResponse(status=400)
    product_id = request.GET.get('product_id', None)
    try:
        product_ = models.Product.objects.get(id=product_id)
    except models.Product.DoesNotExist:
        return redirect('/category/?category_id=1')
    product_is_in_cart = product_ in request.user.cart.products.all()
    context = {'product_id': product_id}
    product_moving_to_from_cart_form = forms.ProductMovingToFromCartForm(context)
    context = {'title': product_.name,
               'header': product_.name,
               'images': product_.productimage_set.all(),
               'product': product_,
               'product_moving_to_from_cart_form': product_moving_to_from_cart_form,
               'product_is_in_cart': product_is_in_cart,
               'characteristics': product_.productcharacteristic_set.all()}
    add_basic_context(context)
    return render(request, 'product.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def cart(request):
    products = [{'object': product_,
                 'units_number_changing_form':
                     forms.ProductUnitsNumberChangingForm({'product_id': product_.id,
                                                           'product_units_number':
                                                               product_.cartproduct_set.get(cart=request.user.cart).units_number}),
                 'moving_from_cart_form': forms.ProductMovingToFromCartForm({'product_id': product_.id})}
                for product_ in request.user.cart.products.all()]
    context = {'title': 'Корзина',
               'header': 'Корзина',
               'products': products}
    add_basic_context(context)
    return render(request, 'cart.html', context=context)


@user_passes_test(lambda user: not user.is_authenticated,
                  login_url='/category/?category_id=1',
                  redirect_field_name=None)
def user_login(request):
    if request.method == 'POST':
        user_login_form = forms.UserLoginForm(request, request.POST)
        if user_login_form.is_valid():
            username = user_login_form.cleaned_data['username']
            password = user_login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f'Вход в систему под учётной записью {username} успешно завершён')
                return redirect('/category/?category_id=1')
        messages.error(request, 'Введены неверные логин и/или пароль')
    user_login_form = forms.UserLoginForm()
    context = {'title': 'Вход в систему',
               'header': 'Вход в систему',
               'user_login_form': user_login_form}
    return render(request, 'user_login.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def user_logout(request):
    logout(request)
    messages.info(request, 'Выход из системы успешно завершён')
    return redirect('/user_login')


@user_passes_test(lambda user: not user.is_authenticated,
                  login_url='/category/?category_id=1',
                  redirect_field_name=None)
def user_registration(request):
    if request.method == 'POST':
        user_registration_form = forms.UserRegistrationForm(request.POST)
        if user_registration_form.is_valid():
            user = user_registration_form.save()
            models.Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена')
            return redirect('/category/?category_id=1')
        messages.error(request, 'Не удалось завершить регистрацию')
    user_registration_form = forms.UserRegistrationForm()
    context = {'title': 'Регистрация',
               'header': 'Регистрация',
               'user_registration_form': user_registration_form}
    return render(request, 'user_registration.html', context=context)
