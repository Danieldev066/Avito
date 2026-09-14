from rest_framework import viewsets, generics, status, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (UserProfileListSerializer, UserProfileEditSerializer, CategoryListSerializer,
                          SubcategoryListSerializer, CategoryDetailSerializer, ProductsListSerializer,
                          ReviewSerializer, ProductsDetailSerializer, SubcategoryDetailSerializer,
                          RegisterSerializer, CustomLoginSerializer, LogoutSerializer, CartSerializer,
                          CartItemSerializer, FavoriteSerializer, FavoriteItemSerializer)
from .models import Category, UserProfile, SubCategory, Product, Review, Cart, CartItem, Favorite, FavoriteItem
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .pagination import ProductPagination

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Невалидный токен'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListAPIView(generics.ListAPIView):
    serializer_class = UserProfileListSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

class UserProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileEditSerializer

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer

class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class SubCategoryListAPIView(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubcategoryListSerializer

class SubCategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubcategoryDetailSerializer

class ProductsListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductsListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['product_name']
    ordering_fields = ['created_date', 'price']
    pagination_class = ProductPagination

class ProductsDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductsDetailSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class =ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


from django.contrib.auth.models import AnonymousUser

class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return CartItem.objects.none()

        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class FavoriteAPIView(generics.RetrieveAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


    def retrieve(self, request, *args, **kwargs):
        favorite, created = Favorite.objects.get_or_create(user=self.request.user)
        serializer = self.get_serializer(favorite)
        return Response(serializer.data)


class FavoriteItemViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class =  FavoriteItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return FavoriteItem.objects.none()

        return FavoriteItem.objects.filter(favorite__user=self.request.user)


    def perform_create(self, serializer):
        favorite, created = Favorite.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data['product']

        if FavoriteItem.objects.filter(favorite=favorite, product=product).exists():
            raise serializers.ValidationError('Товар кошулган')

        serializer.save(favorite=favorite)