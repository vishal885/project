from django.urls import path
from . import views
urlpatterns = [

    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('menu',views.menu,name='menu'),
    path('contact',views.contact,name='contact'),
    path('signup',views.signup,name='signup'),
    path('login',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('profile/',views.profile,name='profile'),
    path('change-password/',views.change_password,name='change-password'),
    path('seller-index/',views.seller_index,name='seller-index'),
    path('seller-add-product',views.seller_add_product,name='seller-add-product'),
    path('seller-view-product',views.seller_view_product,name='seller-view-product'),
    path('seller-product-detail/<int:pk>/',views.seller_product_detail,name='seller-product-detail'),
    path('seller-edit-product/<int:pk>/',views.seller_edit_product,name='seller-edit-product'),
    path('seller-delete-product/<int:pk>/',views.seller_delete_product,name='seller-delete-product'),
    path('product-detail/<int:pk>/',views.product_detail,name='product-detail'),
    path('add-to-wishlist/<int:pk>',views.add_to_wishlist,name='add-to-wishlist'),
    path('add-to-cart/<int:pk>',views.add_to_cart,name='add-to-cart'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('remove-from-wishlist/<int:pk>/',views.remove_from_wishlist,name='remove-from-wishlist'),
    path('cart/',views.cart,name='cart'),
    path('remove-from-cart/<int:pk>/',views.remove_from_cart,name='remove-from-cart'),
    path('change-qty/',views.change_qty,name='change-qty'),
    path('pay/',views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),     
    path('myorder',views.myorder,name='myorder'),


]