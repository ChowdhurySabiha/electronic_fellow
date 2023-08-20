from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import Group
from django.contrib import messages
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.http import JsonResponse
from .models import *
from .forms import OrderForm, ProductForm, CreateUserForm, CustomerForm
import json
import datetime


#########################################LOGIN#########################################

@unauthenticated_user
def registration(request):
    form =CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name = 'customer')
            user.groups.add(group)
            Customer.objects.create(user=user, name=username,)
            
            messages.success(request, "Registration was successful!")

            return redirect('login')

    context = {'form':form}
    return render(request, 'store/registration.html', context)

@unauthenticated_user
def loginPage(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        print(user)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, "Username or password is incorrect!")

    context = {}
    return render(request, 'store/login.html', context)

@login_required
def logoutUser(request):
    logout(request)
    return redirect('login')


#########################################ADMIN#########################################

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    products = Product.objects.all()
    
    total_products = products.count()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders':orders, 'customers':customers, 'products':products, 'total_products':total_products, 'total_customers':total_customers,
        'total_orders':total_orders, 'delivered':delivered, 'pending':pending
    }
    print(customers)

    return render(request, 'store/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'store/admin_products.html', {'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)

    orders = customer.order_set.all()
    order_count = orders.count()

    context = {'customer':customer, 'orders':orders, 'order_count':order_count}
    return render(request, 'store/admin_customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request):
    
    form = OrderForm()
    if request.method == "POST":
        # print(request.method)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

    context = {'form':form}
    return render(request, 'store/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form':form}
    return render(request, 'store/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('dashboard')
    context = {'item':order}
    return render(request, 'store/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

#########################################STORE#########################################
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    print(orders)

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending}
    return render(request, 'store/customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('user_page')

    context = {'form':form}
    return render(request, 'store/settings.html', context)

def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()    
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete = False)
    cartItems = order.get_cart_items
    return render(request, 'store/product_detail.html', {'product': product, 'cartItems':cartItems})

@login_required
def subscribe(request):
    customer = request.user.customer
    subscription_plans = SubscriptionPlan.objects.all()
    order, created = Order.objects.get_or_create(customer=customer, complete = False)
    cartItems = order.get_cart_items
    if request.method == 'POST':
        selected_plan_id = request.POST.get('plan')
        selected_plan = SubscriptionPlan.objects.get(id=selected_plan_id)
        customer.subscription = selected_plan
        customer.save()
        return redirect('store')  # Redirect to user's profile page
    context = {
        'subscription_plans': subscription_plans, 'cartItems':cartItems
    }
    return render(request, 'store/subscribe.html', context)

def category(request, category):
    if request.user.is_authenticated:
        products = Product.objects.filter(category = category)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'products': products, 'category': category, 'cartItems':cartItems}   
    return render(request, 'store/category.html', context)

@login_required
def cart(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

@login_required
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        print(order.get_cart_total)
        if customer.subscription is not None:
            order_total = order.get_cart_total * 0.9
        else:
            order_total = order.get_cart_total
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'shipping':False, 'cartItems':cartItems,'order_total': order_total,}
    return render(request, 'store/checkout.html', context)

@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action', action)
    print('productId', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        print(orderItem.quantity)
        orderItem.quantity += 1
        
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was Added', safe = False)

@login_required
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id


        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping ==True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )

    else:
        print('User is not Logged in')
    return JsonResponse('Payment Complete', safe = False)