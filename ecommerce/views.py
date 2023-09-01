from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer


from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.conf import settings

from .models import Product, Category, CartItem, Order, OrderItem
from .serializers import (
    UserSerializer, ProductSerializer, CategorySerializer,
    CartItemSerializer, OrderSerializer, OrderItemSerializer

)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.conf import settings
from .Pagination import CustomPagination
from rest_framework.pagination import PageNumberPagination






class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            subject = 'Welcome to Ecommerce Platform'
            context = {
                'user': user,
                'message': 'Thank you for registering on our platform.'
            }
            html_message = render_to_string('welcome_email.html', context)

            text_message = strip_tags(html_message)

            try:
                email = EmailMultiAlternatives(subject, text_message, settings.EMAIL_HOST_USER, [user.email])
                email.attach_alternative(html_message, 'text/html')
                email.send()
            except Exception as e:
                # If there's an exception while sending email, print recipient and content
                print("Error sending email to:", user.email)
                print("Email content:", html_message)
                print("Error details:", str(e))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ProductListView(APIView):
    def get(self, request):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        pagination_class = CustomPagination
        return Response(serializer.data)

    
    

class ProductDetailView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart_item(self, user, cart_item_id):
        try:
            return CartItem.objects.get(pk=cart_item_id, user=user)
        except CartItem.DoesNotExist:
            return None

    def get(self, request, cart_item_id):
        cart_item = self.get_cart_item(request.user, cart_item_id)
        if cart_item:
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, cart_item_id):
        cart_item = self.get_cart_item(request.user, cart_item_id)
        if cart_item:
            serializer = CartItemSerializer(cart_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, cart_item_id):
        cart_item = self.get_cart_item(request.user, cart_item_id)
        if cart_item:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)


# class OrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         coupon_discount=Coupon.objects.filter()
#         cart_items = CartItem.objects.filter(user=request.user)

#         if not cart_items:
#             return Response({'message': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

#         total_amount = sum(item.product.price * item.quantity for item in cart_items)

#         order = Order.objects.create(user=request.user, total_amount=total_amount)
#         for cart_item in cart_items:
#             OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, subtotal=cart_item.product.price * cart_item.quantity)
        
#         cart_items.delete()

#         subject = 'Order Placed'
#         message = f'Your order has been placed. Total amount: {total_amount}'
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [request.user.email]

#         # Render HTML template for the email
#         html_message = render_to_string('order_email_template.html', {'message': message, 'total_amount': total_amount})
#         plain_message = strip_tags(html_message)

#         try:
#             send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
#         except Exception as e:
#             # If there's an exception while sending email, print recipient and content
#             print("Error sending order confirmation email to:", request.user.email)
#             print("Email content:", html_message)
#             print("Error details:", str(e))

#         return Response({'message': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Assuming you have a Coupon model
from .models import CartItem, Order, OrderItem, Coupon

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            return Response({'message': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        
        coupon_code = request.data.get('coupon_code')  
        
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount_amount = apply_discount_coupon(total_amount, coupon.percentage)
                total_amount -= discount_amount
            except Coupon.DoesNotExist:
                return Response({'message': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(user=request.user, total_amount=total_amount)
            for cart_item in cart_items:
                OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity, subtotal=cart_item.product.price * cart_item.quantity)
            
            cart_items.delete()

        subject = 'Order Placed'
        message = f'Your order has been placed. Total amount: {total_amount}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]

        html_message = render_to_string('order_email_template.html', {'message': message, 'total_amount': total_amount})
        plain_message = strip_tags(html_message)

        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        except Exception as e:
            print("Error sending order confirmation email to:", request.user.email)
            print("Email content:", html_message)
            print("Error details:", str(e))

        return Response({'message': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
class CategoryListView(APIView):
    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    


from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Product
from .serializers import ProductSerializer

class AdminProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AdminProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        product = serializer.save()

        subject = 'Admin Added A New Product'
        message = f'A new product "{product.name}" has been created.'
        from_email = 'your@example.com'
        recipient_list = ['user@example.com']

        # Render HTML template for the email
        html_message = render_to_string('add_product.html', {'product': product})
        plain_message = strip_tags(html_message)

        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=True)
        except Exception as e:
            # If there's an exception while sending email, print product info and content
            print("Error sending new product email:")
            print("Product:", product)
            print("Email content:", html_message)
            print("Error details:", str(e))

class AdminProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        instance = serializer.save()

        subject = 'Admin Updated Product'
        message = f'The product "{instance.name}" has been updated.'
        from_email = 'your@example.com'
        recipient_list = ['user@example.com']

        # Render HTML template for the email
        html_message = render_to_string('update_product.html', {'product': instance})
        plain_message = strip_tags(html_message)

        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=True)
        except Exception as e:
            # If there's an exception while sending email, print product info and content
            print("Error sending product update email:")
            print("Product:", instance)
            print("Email content:", html_message)
            print("Error details:", str(e))

    def perform_destroy(self, instance):
        subject = 'Admin Deleted Product'
        message = f'The product "{instance.name}" has been deleted.'
        from_email = 'your@example.com'
        recipient_list = ['user@example.com']

        # Render HTML template for the email
        html_message = render_to_string('delete_product.html', {'product': instance})
        plain_message = strip_tags(html_message)

        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=True)
        except Exception as e:
            # If there's an exception while sending email, print product info and content
            print("Error sending product deletion email:")
            print("Product:", instance)
            print("Email content:", html_message)
            print("Error details:", str(e))

        instance.delete()



class ProductListAPIView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()

      
        category = self.request.query_params.get('category')
        if category:
            products = products.filter(category=category)

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)

     
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserProfileSerializer, UserUpdateSerializer,CouponSerializer, DiscountSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WishlistItem, Review,Coupon, Discount
from .serializers import WishlistItemSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticated


class WishlistItemView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = WishlistItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user





class CouponListView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = (IsAuthenticated,)

class DiscountListView(generics.ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = (IsAuthenticated,)
