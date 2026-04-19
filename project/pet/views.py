from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import ServiceItem, Order, OrderItem


def home(request):
    query = request.GET.get('q')
    items = ServiceItem.objects.filter(is_available=True)

    if query:
        items = items.filter(name__icontains=query)

    return render(request, 'home.html', {'items': items})


def signup_view(request):
    form = UserCreationForm()

    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    form = AuthenticationForm()

    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


def service_detail(request, id):
    item = get_object_or_404(ServiceItem, id=id, is_available=True)
    return render(request, 'service_detail.html', {'item': item})


@login_required
def add_to_cart(request, id):
    item = get_object_or_404(ServiceItem, id=id, is_available=True)

    cart = request.session.get('cart', {})
    item_id = str(item.id)

    if item_id in cart:
        cart[item_id]['quantity'] += 1
    else:
        cart[item_id] = {
            'name': item.name,
            'price': float(item.price),
            'quantity': 1,
            'image': item.image.url if item.image else '',
        }

    request.session['cart'] = cart
    return redirect('cart')


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for item_id, item_data in cart.items():
        subtotal = item_data['price'] * item_data['quantity']
        total_price += subtotal

        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'price': item_data['price'],
            'quantity': item_data['quantity'],
            'image': item_data['image'],
            'subtotal': subtotal,
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def update_cart(request, id, action):
    cart = request.session.get('cart', {})
    item_id = str(id)

    if item_id in cart:
        if action == 'increase':
            cart[item_id]['quantity'] += 1
        elif action == 'decrease':
            cart[item_id]['quantity'] -= 1

            if cart[item_id]['quantity'] <= 0:
                del cart[item_id]

    request.session['cart'] = cart
    return redirect('cart')


@login_required
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    item_id = str(id)

    if item_id in cart:
        del cart[item_id]

    request.session['cart'] = cart
    return redirect('cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    cart_items = []
    total_price = 0

    for item_id, item_data in cart.items():
        subtotal = item_data['price'] * item_data['quantity']
        total_price += subtotal

        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'price': item_data['price'],
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pet_name = request.POST.get('pet_name')
        pet_type = request.POST.get('pet_type')
        booking_date = request.POST.get('booking_date')
        payment_method = request.POST.get('payment_method')
        slip_image = request.FILES.get('slip_image')

        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            pet_name=pet_name,
            pet_type=pet_type,
            booking_date=booking_date,
            payment_method=payment_method,
            payment_status=False,
            slip_image=slip_image,
            status='pending',
        )

        for item_id, item_data in cart.items():
            service_item = get_object_or_404(ServiceItem, id=item_id)

            OrderItem.objects.create(
                order=order,
                service_item=service_item,
                quantity=item_data['quantity'],
                price=item_data['price'],
            )

        request.session['cart'] = {}
        return redirect('my_orders')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import Order


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@staff_required
def dashboard(request):
    total_services = ServiceItem.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    return render(request, 'dashboard.html', {
        'total_services': total_services,
        'total_orders': total_orders,
        'total_users': total_users,
    })
from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@staff_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'manage_orders.html', {'orders': orders})


@staff_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)
    order.status = status
    order.save()
    return redirect('manage_orders')


@staff_required
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('manage_orders')