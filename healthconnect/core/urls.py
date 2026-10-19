from django.urls import include, path
from . import views


urlpatterns = [

    path(
        "",
        include("core.feature_urls")
    ),

    # User
    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "register/",
        views.user_register,
        name="register"
    ),

    path(
        "login/",
        views.user_login,
        name="login"
    ),

    path(
        "verify-email/<uidb64>/<token>/",
        views.verify_email,
        name="verify_email"
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),


    # Doctors
    path(
        "doctors/",
        views.doctors_list,
        name="doctors"
    ),

    path(
        "book/<int:doctor_id>/",
        views.book_appointment,
        name="book"
    ),


    # Medicines
    path(
        "medicines/",
        views.medicines_list,
        name="medicines"
    ),

    path(
        "order/<int:medicine_id>/",
        views.confirm_order,
        name="order"
    ),


    # User history
    path(
        "appointments/",
        views.user_appointments,
        name="user_appointments"
    ),

    path(
        "my-orders/",
        views.user_orders,
        name="user_orders"
    ),





    # Admin authentication
    path(
        "admin-login/",
        views.admin_login,
        name="admin_login"
    ),

    path(
        "admin-logout/",
        views.admin_logout,
        name="admin_logout"
    ),


    # Admin dashboard
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # Doctors
    path(
        "admin-doctors/",
        views.admin_doctors,
        name="admin_doctors"
    ),

    path(
        "add-doctor/",
        views.add_doctor,
        name="add_doctor"
    ),


    # Schedules
    path(
        "schedules/",
        views.admin_schedules,
        name="admin_schedules"
    ),

    path(
        "add-schedule/",
        views.add_schedule,
        name="add_schedule"
    ),


    # Appointments
    path(
        "admin-appointments/",
        views.admin_appointments,
        name="admin_appointments"
    ),


    # Medicines
    path(
        "admin-medicines/",
        views.admin_medicines,
        name="admin_medicines"
    ),

    path(
        "add-medicine/",
        views.add_medicine,
        name="add_medicine"
    ),


    # Orders
    path(
        "admin-orders/",
        views.admin_orders,
        name="admin_orders"
    ),
]
