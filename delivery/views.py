from django.http import HttpResponse
from django.shortcuts import get_object_or_404 , redirect, render
from . models import Customer
from . models import Restaurant
from . models import Item
from . models import Cart

import razorpay
from django.conf import settings

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
           restaurants = Restaurant.objects.all() 
        return render(request, 'customer_home.html', {"restaurants": restaurants, "username": username})
    
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
    return render(request, 'show_restaurants.html', {"restaurants": restaurants})
   
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
    
def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get( id=restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'update_menu.html', {"itemList": itemList, "restaurant": restaurant})

def update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_veg = request.POST.get('is_veg') == 'on'
        picture = request.POST.get('picture')
        
    Item.objects.create(
        restaurant=restaurant,
        name=name,
        description=description,
        price=price,
        is_veg=is_veg,
        picture=picture
    )
    return render(request, 'admin_home.html')

     
def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get( id=restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'customer_menu.html', {"itemList": itemList,
                                                  "restaurant": restaurant,
                                                  "username": username})
    
def add_to_cart(request, item_id, username):
    item = Item.objects.get(id = item_id)
    customer = Customer.objects.get(username = username)
    
    cart, created = Cart.objects.get_or_create(customer = customer)
    cart.items.add(item)
    return HttpResponse('added to cart')

def show_cart(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0
    
    return render(request, 'cart.html',{"itemList": items,
                                        "total_price": total_price,
                                        "username": username})
    
def checkout(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else[]
    total_price = cart.total_price() if cart else 0
    
    if total_price == 0:
        return render(request, 'checkout.html', {'error': 'Your cart is empty',})
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order_data = {
        'amount': int(total_price * 100),  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1',  # Automatically capture payment
    }
    order = client.order.create(data=order_data)

    # Pass the order details to the frontend
    return render(request, 'delivery/checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount': total_price,
    })


# Orders Page
def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price before clearing the cart
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    # Clear the cart after fetching its details
    if cart:
        cart.items.clear()

    return render(request, 'orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })
    
    
    
