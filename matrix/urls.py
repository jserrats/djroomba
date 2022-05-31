from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("print/<str:image_name>", views.print, name="print"),
    path("delete/<str:image_name>", views.delete, name="delete"),
    path("clear/", views.clear, name="clear"),
]
