from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .views import (
    UserRegistrationView,UserProfileView, UserUpdateView,WishlistItemView, ReviewView,
    ProductListView, CartItemView, CartItemDetailView,ProductListAPIView,
    OrderView, OrderHistoryView,CategoryListView,AdminProductListView,CouponListView, DiscountListView,AdminProductDetailView,AdminProductCreateView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UserUpdateView.as_view(), name='user-profile-update'),
    path('wishlist/add/', WishlistItemView.as_view(), name='wishlist-add'),
    path('reviews/submit/', ReviewView.as_view(), name='review-submit'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('api/products/', ProductListAPIView.as_view(), name='product-list'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    path('cart/', CartItemView.as_view(), name='cart-list'),
    path('cart/<int:cart_item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    
    path('place-order/', OrderView.as_view(), name='place-order'),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('add_products/',AdminProductListView.as_view(),name='AdminProductListView'),
    path('products/', AdminProductListView.as_view(), name='admin-product-list'),
    path('products/create/', AdminProductCreateView.as_view(), name='admin-product-create'),
    path('products/<int:pk>/', AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('coupons/', CouponListView.as_view(), name='coupon-list'),
    path('discounts/', DiscountListView.as_view(), name='discount-list')
]   
