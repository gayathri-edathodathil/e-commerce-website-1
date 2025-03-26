from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
from .models import wishlist as wl
from .models import cart as cartOfUser
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

def checkout(request):
    orderitems=cartOfUser.objects.filter(user=request.user)
    grandTotal=0
    for i in orderitems:
            grandTotal+=i.product.price*i.quantity
    return render(request,'checkout.html',{'items':orderitems,'total':grandTotal})