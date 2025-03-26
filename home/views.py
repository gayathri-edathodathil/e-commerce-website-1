from django.shortcuts import render
from .models import category,product
from user.models import wishlist,cart
from django.shortcuts import get_object_or_404
from random import sample

# Create your views here.
def home(request):
    categories=category.objects.all()
    return render(request,'index.html',{'categories':categories})

def shop(request):
    cate=request.GET.get('category','')
    if cate!='':
        items=product.objects.filter(category=cate)
        cate=int(cate)

    else:
        items=product.objects.all()
    categories=category.objects.all()
    return render(request,'shop-left-sidebar.html',{'items':items,'categories':categories,'filter':cate})

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def productDetails(request,item_id):
    item=get_object_or_404(product,id=item_id)
    rating = int(item.rating)
    half_star = item.rating - rating >= 0.5
    if half_star:
        empty_stars = int(5-item.rating)
    else:
        empty_stars = 5 - rating
    saved=False
    addedtocart=False
    if request.user.is_authenticated:
        saved=wishlist.objects.filter(user=request.user,product=item).exists()
        addedtocart=cart.objects.filter(user=request.user,product=item).exists()
    sampleset=product.objects.exclude(id=item_id)
    suggestions = sample(list(sampleset), 3)

    return render(request,'single-product.html',{'item':item,'rating':range(rating),'empty_stars':range(empty_stars),'half_star': half_star,'suggestions':suggestions,'saved':saved,'addedtocart':addedtocart})