from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('my-orders/', views.my_orders, name='my_orders'),

    path('service/<int:id>/', views.service_detail, name='service_detail'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('update-cart/<int:id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
]
path('dashboard/', views.dashboard, name='dashboard'),
path('manage-orders/', views.manage_orders, name='manage_orders'),
path('update-order-status/<int:id>/<str:status>/', views.update_order_status, name='update_order_status'),
path('delete-order/<int:id>/', views.delete_order, name='delete_order'),