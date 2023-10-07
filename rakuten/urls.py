from django.urls import path

#作成したviewをインポート
from .views import (
    home_templateView, CategoryFormView, CategoryListView, ProductListView, 
    ProductFormView, ProductDetailView, ProductUpdateView, ProductDeleteView,
    CategoryUpdateView, CategoryUpdateView, CategoryDeleteView, RegistUserView,
    UserLoginView, UserLogoutView, CategoryDetailView
    
)

app_name = 'rakuten'

urlpatterns = [
    path('home/', home_templateView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('product_list/', ProductListView.as_view(), name='product_list'),
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('product_form/', ProductFormView.as_view(), name='product_form'),
    path('category_form/', CategoryFormView.as_view(), name='category_form'),
    path('detail_product/<int:pk>', ProductDetailView.as_view(), name='detail_product'),
    path('detail_category/<int:pk>', CategoryDetailView.as_view(), name='detail_category'),
    path('update_product/<int:pk>', ProductUpdateView.as_view(), name='update_product'),
    path('delete_product/<int:pk>', ProductDeleteView.as_view(), name='delete_product'),
    path('update_category/<int:pk>', CategoryUpdateView.as_view(), name='update_category'),
    path('delete_category/<int:pk>', CategoryDeleteView.as_view(), name='delete_category'),
]