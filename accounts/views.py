from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # Import the custom form
from cryptos.models import UserAvlbBalance,UserBalance,UserLimitBalance
from decimal import Decimal


def landing_page(request):
    return render(request, 'landing_page.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            UserBalance.objects.create(user=user, balance=Decimal('1000.00'))  
            UserAvlbBalance.objects.create(user=user, avlb_balance=Decimal('1000.00')) 
            UserLimitBalance.objects.create(user = user,limit_balance =Decimal('0.00'))
            return redirect('landing_page')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
