from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser, name = 'logout'),
    path('registration/',views.registration, name = 'register'),

    path('admin-panel/', views.home, name = 'dashboard'),
    path('admin-panel/products', views.products, name = 'products'),
    path('admin-panel/customer/<int:pk>', views.customer, name = 'customer'),
    path('admin-panel/create_order', views.createOrder, name = 'create_order'),
    path('admin-panel/update_order/<int:pk>', views.updateOrder, name = 'update_order'),
    path('admin-panel/delete_order/<str:pk>', views.deleteOrder, name = 'delete_order'),
    path('admin_panel/add', views.add_product, name='add_product'),

    path('user/', views.userPage, name = 'user_page'),
    path('account/', views.accountSettings, name = 'settings'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
	path('', views.store, name="store"),
    path('products/<str:pk>', views.product_detail, name="product_detail"),
    path('products/<str:category>', views.category, name="category"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]