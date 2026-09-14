from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


STATUS_CHOICES = (
('gold','gold'),
('silver','silver'),
('bronze','bronze'),
('simple','simple'),
)

class UserProfile(AbstractUser):
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(16),
                                                       MaxValueValidator(90)],
                                           null=True, blank=True)
    phone_number = PhoneNumberField(default='+996')
    avatar = models.ImageField(upload_to='profile_image/')
    status = models.CharField(choices=STATUS_CHOICES,default='simple',max_length=50)

    def str(self):
        return f'{self.first_name} {self.last_name}'

class Category(models.Model):
     category_name = models.CharField(max_length=50)
     category_image = models.ImageField(upload_to='categories/')

     def str(self) -> str:
         return self.category_name

class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='category_sub')
    subcategory_name = models.CharField(max_length=50)
    subcategory_image = models.ImageField(upload_to='subcategories/')

    def str(self) -> str:
        return f'{self.category.category_name} - {self.subcategory_name}'

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE, related_name='sub_products')
    product_name = models.CharField(max_length=50)
    product_image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField(null=True, blank=True)
    article_number = models.PositiveBigIntegerField(unique=True)
    product_type = models.BooleanField(default=True)
    video = models.FileField(upload_to='products_videos/', null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)


    def get_avg_rating(self):
        ratings = self.product_reviews.all()
        if ratings.exists():
            return round(sum([i.stars for i in ratings]) / ratings.count(), 1)
        return 0

    def get_count_people(self):
        return self.product_reviews.count()

    def str(self) -> str:
        return f'{self.subcategory.subcategory_name} - {self.product_name}'

class ProductImages(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name = 'product_img')
    product_image = models.ImageField(upload_to='products_images/')

class Review(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name = 'product_reviews')
    stars = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1,6)], null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    review_image = models.ImageField(upload_to='reviews_images/')
    created_time = models.DateTimeField(auto_now_add=True)

    def str(self) -> str:
        return f'{self.user.username} - comment'


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def get_total_price(self):
        return sum([i.get_total_price() for i in self.item.all()])

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def get_total_price(self):
        return self.quantity * self.product.price

class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

class FavoriteItem(models.Model):
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE, related_name='favorite_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)






