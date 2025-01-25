from django.urls import path
from . import views
from .views import add_product, edit_product
from .views import rate_product


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('search/', views.search, name='search'),
    path('product/new/', add_product, name='add_product'),  # صفحة إضافة إعلان جديد
    path('product/<int:product_id>/edit/', edit_product, name='edit_product'),  # تعديل الإعلان
    path('chat/<int:product_id>/<int:receiver_id>/', views.chat, name='chat'),
    path('inbox/', views.inbox, name='inbox'),
    path('product/<int:product_id>/rate/', rate_product, name='rate_product'),
    path('reserve/<int:product_id>/', views.reserve_product, name='reserve_product'),
    path('reservations/', views.user_reservations, name='user_reservations'),
    path('delete-reservation/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
    

]
