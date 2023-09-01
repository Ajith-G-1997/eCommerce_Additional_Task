from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Category, CartItem, Order,Coupon, Discount, OrderItem,Review,WishlistItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'quantity', 'categories','image')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'user', 'product', 'quantity')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'quantity', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Order
        fields = ('id', 'user',  'total_amount', 'created_at', 'status')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=('user','product','rating','text')

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=WishlistItem
        fields=('user','product')
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'