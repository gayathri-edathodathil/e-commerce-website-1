from user.models import cart

def custom_variables(request):
    if request.user.is_authenticated:
        cartno=cart.objects.filter(user=request.user).count()
    else:
        cartno=0
    return {
            'cartno': cartno,
    }