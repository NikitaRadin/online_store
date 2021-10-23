from online_store_app import constants, models, forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Sum, F
import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def add_basic_context(context):
    context['background_image_url'] = constants.BACKGROUND_IMAGE_URL
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
    if request.method == 'POST':
        product_units_number_changing_form = forms.ProductUnitsNumberChangingForm(request.POST)
        if product_units_number_changing_form.is_valid():
            product_id = product_units_number_changing_form.cleaned_data['product_id']
            units_number = product_units_number_changing_form.cleaned_data['units_number']
            try:
                product_ = request.user.cart.products.get(id=product_id)
            except models.Product.DoesNotExist:
                return HttpResponse(status=404)
            cartproduct = product_.cartproduct_set.get(cart=request.user.cart)
            cartproduct.units_number = units_number
            cartproduct.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    products = request.user.cart.products
    extended_products = [{'object': product_,
                          'units_number_changing_form':
                              forms.ProductUnitsNumberChangingForm({'product_id': product_.id,
                                                                    'units_number': product_.cartproduct_set.get(cart=request.user.cart).units_number}),
                          'moving_from_cart_form': forms.ProductMovingToFromCartForm({'product_id': product_.id})}
                         for product_ in products.all()]
    order_making_form = forms.OrderMakingForm()
    contents_information = products.filter(cartproduct__cart=request.user.cart).\
        aggregate(units_number=Sum('cartproduct__units_number'),
                  total_cost=Sum(F('price')*F('cartproduct__units_number')))
    context = {'title': 'Корзина',
               'header': 'Корзина',
               'extended_products': extended_products,
               'order_making_form': order_making_form,
               'mapgl_js_api_key': constants.MAPGL_JS_API_KEY,
               'geocoder_api_key': constants.GEOCODER_API_KEY,
               'stripe_publishable_key': constants.STRIPE_PUBLISHABLE_KEY,
               'contents_information': contents_information}
    add_basic_context(context)
    return render(request, 'cart.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def order_making(request):
    if request.method == 'POST':
        order_making_form = forms.OrderMakingForm(request.POST)
        if order_making_form.is_valid():
            stripe.api_key = constants.STRIPE_SECRET_KEY
            line_items = [{'name': product_.name,
                           'amount': int(product_.price * 100),
                           'currency': 'RUB',
                           'quantity': product_.cartproduct_set.get(cart=request.user.cart).units_number}
                          for product_ in request.user.cart.products.all()]
            try:
                checkout_session = stripe.checkout.Session.create(
                    mode = 'payment',
                    payment_method_types = ['card'],
                    line_items = line_items,
                    success_url = f'{constants.BASIC_URL}successful_payment_completion',
                    cancel_url = f'{constants.BASIC_URL}unsuccessful_payment_completion'
                )
                return HttpResponse(status=200, content=checkout_session['id'])
            except:
                return HttpResponse(status=520)
    return HttpResponse(status=400)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def successful_payment_completion(request):
    order = models.Order.objects.create(status=constants.PAID, user=request.user)
    products = request.user.cart.products
    for product_ in products.all():
        order.products.add(product_,
                           through_defaults={'units_number':
                                                 product_.cartproduct_set.get(cart=request.user.cart).units_number})
    products.clear()
    messages.success(request, 'Оплата успешно завершена')
    return redirect('/cart')


@login_required(login_url='/user_login',
                redirect_field_name=None)
def unsuccessful_payment_completion(request):
    messages.error(request, 'Не удалось завершить оплату')
    return redirect('/cart')


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
    add_basic_context(context)
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
    add_basic_context(context)
    return render(request, 'user_registration.html', context=context)
