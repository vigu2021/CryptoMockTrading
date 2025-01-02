from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # Import the custom form



def landing_page(request):
    return render(request, 'landing_page.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('landing_page')  # Redirect to the landing page or any other page
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
