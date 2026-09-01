from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
from .models import wishlist as wl
from .models import cart as cartOfUser
from .models import Order, OrderItem
from home.models import product

# Create your views here.
def add_to_wishlist(request,product_id):
    if request.user.is_authenticated:
        action=request.GET.get('action')
        prod = get_object_or_404(product,id=product_id)
        if action=='remove-wishlist':
            wl.objects.filter(user=request.user,product=prod).delete()
        elif action=='add-wishlist':
            wl.objects.get_or_create(user=request.user, product=prod)
        next_url=request.GET.get('next')
        if next_url is not None:
            return redirect(next_url)
        return redirect('product',item_id=product_id)
    else:
        messages.error(request,"Login to manage Wishlist")
        return redirect('login')
def wishlist(request):
    if request.user.is_authenticated:
        items = wl.objects.filter(user=request.user)
        return render(request,'wishlist.html',{'items':items})
    else:
        return redirect('login')

def add_to_cart(request):
    if request.user.is_authenticated:
        action=request.GET.get('action')
        product_id=request.GET.get('product_id')
        if action=='remove-cart':
            prod = get_object_or_404(product,id=product_id)
            cartOfUser.objects.filter(user=request.user,product=prod).delete()
        elif action=='add-cart':
            prod = get_object_or_404(product,id=product_id)
            qty=request.GET.get('qty')
            totalprice=prod.price*int(qty)
            cartOfUser.objects.get_or_create(user=request.user, product=prod,quantity=qty,totalprice=totalprice)
        elif action=='clear-cart':
            cartOfUser.objects.filter(user=request.user).delete()
        next_url=request.GET.get('next')
        if next_url is not None:
            return redirect(next_url)
        return redirect('product',item_id=product_id)
    else:
        messages.error(request,"Login to manage Wishlist")
        return redirect('login')
def cart(request):
    if request.user.is_authenticated:
        cart_items=cartOfUser.objects.filter(user=request.user)
        grandTotal=0
        for i in cart_items:
            grandTotal+=i.product.price*i.quantity
        return render(request,'cart.html',{'items':cart_items,'grandtotal':grandTotal})
    else:
        messages.info("Login to buy")
        return redirect('login')
    
def login(request):
    if request.method =='POST':
        username=request.POST['username']
        password=request.POST['password']
        if username=='' or password=='':
            messages.info(request,'All fields are required')
            return redirect('login')
        else:
            user = auth.authenticate(username=username,password=password)
            if user is not None:
                auth.login(request,user)
                next_url = request.POST.get('next','/')
                if next_url=='':
                    next_url='/'
                return redirect(next_url)
            else:
                messages.info(request,'Username or Password invalid')
                return redirect('login')
    else:
        return render(request,'login-register.html')

def signup(request):
    if request.method == 'POST':
        name=request.POST['full-name']
        phone=request.POST['phone']
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
        repass=request.POST['retype-password']
        if username=='' or password=='' or email=='' or name=='':
            messages.info(request,'All fields are required')
            return redirect('signup')
        if password!=repass:
            messages.info(request,'Passwords are not matching')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.info(request,'Username taken')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request,'Email already used by another account')
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username,password=password,first_name=name,email=email)
            user.save()
            user = auth.authenticate(username=username,password=password)
            auth.login(request,user)
            next_url = request.POST.get('next','/')
            if next_url=='':
                    next_url='/'
            return redirect(next_url)
    else:
        return render(request,'login-register.html')

def logout(request):
    auth.logout(request)
    next_url = request.GET.get('next','/')
    return redirect(next_url)

import uuid
import datetime
from django.db import transaction

def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login to checkout")
        return redirect('login')
        
    orderitems = cartOfUser.objects.filter(user=request.user)
    if not orderitems.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart')
        
    grandTotal = sum(i.product.price * i.quantity for i in orderitems)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('billing_email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_1 = request.POST.get('address_1', '').strip()
        city = request.POST.get('city', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        country = request.POST.get('billing_country', 'US').strip()
        order_note = request.POST.get('order', '').strip()
        payment_method = request.POST.get('payment_method', 'Direct bank transfer')

        full_name = f"{first_name} {last_name}".strip() or request.user.get_full_name() or request.user.username

        if not address_1 or not email or not phone:
            messages.error(request, "Please fill in all required contact and shipping details.")
            return render(request, 'checkout.html', {'items': orderitems, 'total': grandTotal})

        # Inventory check
        for item in orderitems:
            if item.product.stock < item.quantity:
                messages.error(
                    request,
                    f"Insufficient stock for {item.product.name}. Only {item.product.stock} left available."
                )
                return redirect('cart')

        # Create Order atomically
        with transaction.atomic():
            order_num = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            order = Order.objects.create(
                user=request.user,
                order_number=order_num,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address_1,
                city=city,
                postal_code=postcode,
                country=country,
                order_note=order_note,
                total_price=grandTotal,
                status='Confirmed',
                payment_method=payment_method,
                payment_status='Paid'
            )

            for item in orderitems:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                if item.product.stock <= 0:
                    item.product.availability = False
                item.product.save()

            # Clear cart
            orderitems.delete()

        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect('order_confirmation', order_number=order.order_number)

    return render(request, 'checkout.html', {'items': orderitems, 'total': grandTotal})


def order_confirmation(request, order_number):
    if not request.user.is_authenticated:
        return redirect('login')
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


def order_history(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login to view order history")
        return redirect('login')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


def order_detail(request, order_number):
    if not request.user.is_authenticated:
        return redirect('login')
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'order_detail.html', {'order': order})