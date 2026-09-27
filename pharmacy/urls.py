from django.urls import path

from . import views

app_name = "pharmacy"

urlpatterns = [
    path("", views.medicine_list, name="medicine_list"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:pk>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.my_orders, name="my_orders"),
    path("orders/<str:order_id>/", views.order_detail, name="order_detail"),
    path("medicine/<slug:slug>/", views.medicine_detail, name="medicine_detail"),
]
