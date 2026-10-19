from django.urls import path

from . import feature_views


urlpatterns = [
    path(
        "dashboard/",
        feature_views.patient_dashboard,
        name="patient_dashboard",
    ),
    path(
        "medicine-finder/",
        feature_views.medicine_finder,
        name="medicine_finder",
    ),
    path(
        "health-tools/",
        feature_views.health_tools,
        name="health_tools",
    ),
    path(
        "admin-insights/",
        feature_views.admin_insights,
        name="admin_insights",
    ),
    path(
        "admin-orders/export/",
        feature_views.export_orders_csv,
        name="export_orders_csv",
    ),
    path(
        "admin-appointments/export/",
        feature_views.export_appointments_csv,
        name="export_appointments_csv",
    ),
]
