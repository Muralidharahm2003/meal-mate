from django.http import HttpResponse
from django.shortcuts import get_object_or_404 , redirect, render
from . models import Customer
from . models import Restaurant

# Create your views here.
def index(request):
    return render(request, 'index.html')

def open_signin(request):
    return render(request, 'signin.html')

def open_signup(request):
    return render(request, 'signup.html')

def signup(request):
     if request.method == 'POST':
       username = request.POST.get('username')
       password = request.POST.get('password')
       email = request.POST.get('email')
       mobile = request.POST.get('mobile')
       address = request.POST.get('address')
       
       try:
           Customer.objects.get(username = username)
           return HttpResponse("Duplicates username not allowed")
       #creating customer table object
       except:
        Customer.objects.create(username = username,
                               password = password,
                               email = email,
                               mobile = mobile,
                               address = address)
       
       return render(request, "signin.html")
   
def signin(request):
    #return HttpResponse("Received")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    
    try:    
        Customer.objects.get(username = username,password = password)
        if username == "admin":
           return render(request, "admin_home.html")
        else:
           return render(request, "customer_home.html") 
    
    except Customer.DoesNotExist:
        return render(request, 'fail.html')

def open_add_restaurant(request):
    return render(request, "add_restaurant.html") 

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        Restaurant.objects.create(name=name,
                                  picture=picture,
                                  cuisine=cuisine,
                                  rating=rating)
        restaurants = Restaurant.objects.all()
        return render(request, "show_restaurants.html", {"restaurants": restaurants}) 
    
    return HttpResponse("Invalid request")

def open_show_restaurant(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'display_restaurants.html', {"restaurants": restaurants})
   
def open_update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant": restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method =='POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()
        return redirect('open_show_restaurant')
    return render(request, 'update_restaurant.html', {"restaurant": restaurant})
    
    #Delete Restaurant
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
    if request.method =="POST":
        restaurant.delete()
        return redirect("open_show_restaurant")
