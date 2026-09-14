from django.urls import path, include
from rest_framework import routers
from .views import (UserProfileListAPIView, SubCategoryListAPIView,
                    SubCategoryDetailAPIView,CategoryDetailAPIView,
                    ProductsListAPIView, ReviewViewSet,CategoryListAPIView,
                    UserProfileDetailAPIView, ProductsDetailAPIView, RegisterView,
                    CustomLoginView, LogoutView, CartAPIView, CartItemViewSet, FavoriteAPIView,
                    FavoriteItemViewSet)

router = routers.DefaultRouter()
router.register(r'review', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/', UserProfileListAPIView.as_view()),
    path('user/<int:pk>/', UserProfileDetailAPIView.as_view()),
    path('product/', ProductsListAPIView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductsDetailAPIView.as_view(), name='product_detail'),
    path('category/', CategoryListAPIView.as_view(), name='category_list'),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),
    path('subcategory/', SubCategoryListAPIView.as_view(), name='category_list'),
    path('subcategory/<int:pk>/', SubCategoryDetailAPIView.as_view(), name='category_detail'),
    path('register/', RegisterView.as_view(), name='user_register'),
    path('login/', CustomLoginView.as_view(), name='user_login'),
    path('logout/', LogoutView.as_view(), name='user_logout'),
    path('cart/', CartAPIView.as_view(), name='cart_detail'),
    path('cart_item/', CartItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cart_item/<int:pk>/', CartItemViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('favorite/', FavoriteAPIView.as_view(), name='favorite_detail'),
    path('favorite_item/', FavoriteItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('favorite_item/<int:pk>', FavoriteItemViewSet.as_view({'delete': 'destroy'}))
]
