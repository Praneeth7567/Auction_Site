from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:name>", views.product, name="product"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/<str:item_name>/", views.watchlist_item, name="watchlist_item"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:name>/", views.category, name="category"),
    path("categories/<str:name>/<str:item_name>/", views.category_item, name="category_item"),
    path("create/", views.create, name="create"),
    path("<str:name>/button/", views.button, name="button"),
    path("close_bid/<str:name>", views.close_bid, name="close_bid"),
]