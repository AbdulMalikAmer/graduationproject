from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import RegexValidator



# Create Customer Profile
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	date_modified = models.DateTimeField(User, auto_now=True)
	phone = models.CharField(max_length=20, blank=True)
	address1 = models.CharField(max_length=200, blank=True)
	address2 = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=200, blank=True)
	state = models.CharField(max_length=200, blank=True)
	zipcode = models.CharField(max_length=200, blank=True)
	country = models.CharField(max_length=200, blank=True)
	old_cart = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.user.username

# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
	if created:
		user_profile = Profile(user=instance)
		user_profile.save()

# Automate the profile thing
post_save.connect(create_profile, sender=User)


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name




# Categories of Products
class Category(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	#@daverobb2011
	class Meta:
		verbose_name_plural = 'categories'


# Customers
class Customer(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=10)
	email = models.EmailField(max_length=100)
	password = models.CharField(max_length=100)


	def __str__(self):
		return f'{self.first_name} {self.last_name}'



# All of our Products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # المستخدم الذي أضاف الإعلان
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)  # المدينة
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^(092|091|094|093)\d{7}$',
                message="Phone number must start with 092, 091, 094, or 093 and be 10 digits long."
            )
        ],
        help_text="Enter a valid phone number starting with 092, 091, 094, or 093."
    )

    def __str__(self):
        return self.name

# Customer Orders
class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	address = models.CharField(max_length=100, default='', blank=True)
	phone = models.CharField(max_length=20, default='', blank=True)
	date = models.DateField(default=datetime.datetime.today)
	status = models.BooleanField(default=False)

	def __str__(self):
		return self.product



class ChatMessage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
   		 return f'{self.sender.username}: {self.message[:30]}...'


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # تقييم من 1 إلى 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.rating}★ by {self.user.username}'

    class Meta:
        unique_together = ('product', 'user')  # يمنع المستخدم من تقييم نفس المنتج مرتين

    @property
    def average_rating(self):
        return self.product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
	
#مودل للحجوزات
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # المستخدم الذي يحجز المنتج
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # المنتج المحجوز
    checkin_date = models.DateField()  # تاريخ الوصول
    checkout_date = models.DateField()  # تاريخ المغادرة
    created_at = models.DateTimeField(auto_now_add=True)  # تاريخ إنشاء الحجز

    class Meta:
        unique_together = ('product', 'checkin_date', 'checkout_date')  # منع التداخل في نفس التواريخ

    def __str__(self):
        return f"{self.user.username} reserved {self.product.name} from {self.checkin_date} to {self.checkout_date}"