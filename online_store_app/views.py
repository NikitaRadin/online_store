from online_store_app import constants, models, forms, token_generators
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Sum, F
import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


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
    context = {'product_id': product_id,
               'text': '* * * Отзыв * * *'}
    feedback_writing_form = forms.FeedbackWritingForm(context)
    context = {'title': product_.name,
               'header': product_.name,
               'images': product_.productimage_set.all(),
               'product': product_,
               'product_moving_to_from_cart_form': product_moving_to_from_cart_form,
               'product_is_in_cart': product_is_in_cart,
               'feedback_writing_form': feedback_writing_form,
               'characteristics': product_.productcharacteristic_set.all(),
               'feedback': product_.feedback_set.all().order_by('-date_time')}
    add_basic_context(context)
    return render(request, 'product.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def feedback_writing(request):
    if request.method == 'POST':
        feedback_writing_form = forms.FeedbackWritingForm(request.POST)
        if feedback_writing_form.is_valid():
            product_id = feedback_writing_form.cleaned_data['product_id']
            text = feedback_writing_form.cleaned_data['text']
            try:
                product_ = models.Product.objects.get(id=product_id)
            except models.Product.DoesNotExist:
                return HttpResponse(status=404)
            models.Feedback.objects.create(text=text, user=request.user, product=product_)
            return HttpResponse(status=200)
    return HttpResponse(status=400)


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
            delivery_address = order_making_form.cleaned_data['delivery_address']
            entrance = order_making_form.cleaned_data['entrance']
            floor = order_making_form.cleaned_data['floor']
            apartment = order_making_form.cleaned_data['apartment']
            recipient_first_last_name = order_making_form.cleaned_data['recipient_first_last_name']
            recipient_phone_number = order_making_form.cleaned_data['recipient_phone_number']
            order = models.Order.objects.create(delivery_address=delivery_address, entrance=entrance, floor=floor,
                                                apartment=apartment, recipient_first_last_name=recipient_first_last_name,
                                                recipient_phone_number=recipient_phone_number, status=constants.MADE,
                                                user=request.user)
            for product_ in request.user.cart.products.all():
                order.products.add(product_,
                                   through_defaults={'units_number':
                                                         product_.cartproduct_set.get(cart=request.user.cart).units_number})
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
                    success_url = f'{constants.BASIC_URL}successful_payment_completion/?order_id={order.id}',
                    cancel_url = f'{constants.BASIC_URL}unsuccessful_payment_completion/?order_id={order.id}'
                )
                return HttpResponse(status=200, content=checkout_session['id'])
            except:
                return HttpResponse(status=520)
    return HttpResponse(status=400)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def successful_payment_completion(request):
    order_id = request.GET.get('order_id', None)
    try:
        order_ = models.Order.objects.get(id=order_id)
    except models.Order.DoesNotExist:
        return redirect('/category/?category_id=1')
    order_.status = constants.PAID
    order_.save()
    request.user.cart.products.clear()
    messages.success(request, 'Оплата успешно завершена')
    return redirect('/cart')


@login_required(login_url='/user_login',
                redirect_field_name=None)
def unsuccessful_payment_completion(request):
    order_id = request.GET.get('order_id', None)
    try:
        order_ = models.Order.objects.get(id=order_id)
    except models.Order.DoesNotExist:
        return redirect('/category/?category_id=1')
    order_.status = constants.REJECTED
    order_.save()
    messages.error(request, 'Не удалось завершить оплату')
    return redirect('/cart')


@login_required(login_url='/user_login',
                redirect_field_name=None)
def orders(request):
    extended_orders = [{'object': order,
                        'extended_products': [{'object': product_,
                                               'units_number': product_.orderproduct_set.get(order=order).units_number}
                                              for product_ in order.products.all()]}
                       for order in request.user.order_set.all().order_by('-last_change_date_time')]
    context = {'title': 'Заказы',
               'header': 'Заказы',
               'extended_orders': extended_orders}
    add_basic_context(context)
    return render(request, 'orders.html', context=context)


@login_required(login_url='/user_login',
                redirect_field_name=None)
def profile(request):
    context = {'title': 'Профиль',
               'header': 'Профиль'}
    add_basic_context(context)
    return render(request, 'profile.html', context=context)


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
            user = user_registration_form.save(commit=False)
            user.is_active = False
            user.save()
            models.Cart.objects.create(user=user)
            subject = 'Подтверждение адреса электронной почты'
            context = {'first_name': user.first_name,
                       'domain': get_current_site(request).domain,
                       'user_id': urlsafe_base64_encode(force_bytes(user.id)),
                       'email_confirmation_token': token_generators.email_confirmation_token_generator.make_token(user)}
            email_message = EmailMessage(subject=subject,
                                         body=render_to_string('email_confirmation.html', context),
                                         to=[user.email])
            email_message.send()
            messages.success(request, f'На адрес электронной почты {user.email} отправлено электронное письмо с '
                                      f'дальнейшими инструкциями')
            return redirect('/user_registration')
        messages.error(request, 'Не удалось завершить регистрацию')
    user_registration_form = forms.UserRegistrationForm()
    context = {'title': 'Регистрация',
               'header': 'Регистрация',
               'user_registration_form': user_registration_form}
    add_basic_context(context)
    return render(request, 'user_registration.html', context=context)


@user_passes_test(lambda user: not user.is_authenticated,
                  login_url='/category/?category_id=1',
                  redirect_field_name=None)
def email_confirmation(request):
    try:
        user_id = force_text(urlsafe_base64_decode(request.GET.get('user_id', None)))
        user = models.User.objects.get(id=user_id)
    except (AttributeError, DjangoUnicodeDecodeError, ValueError, models.User.DoesNotExist):
        messages.error(request, 'Ссылка для подтверждения адреса электронной почты, по которой вы перешли, некорректна')
        return redirect('/user_registration')
    email_confirmation_token = request.GET.get('email_confirmation_token', None)
    if not token_generators.email_confirmation_token_generator.check_token(user, email_confirmation_token):
        messages.error(request, 'Ссылка для подтверждения адреса электронной почты, по которой вы перешли, некорректна')
        return redirect('/user_registration')
    user.is_active = True
    user.save()
    login(request, user)
    messages.success(request, 'Регистрация успешно завершена')
    return redirect('/category/?category_id=1')
