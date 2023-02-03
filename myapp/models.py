from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	message=models.TextField()


	def __str__(self):
		return self.name
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveSmallIntegerField()
	address=models.TextField()
	password=models.CharField(max_length=50)
	profile_pic=models.ImageField(upload_to="profile_pic/")
	firstlogin=models.BooleanField(default=False)
	usertype=models.CharField(max_length=100,default="buyer")
	
	def __str__(self):
		return self.fname+""+self.lname
class Product(models.Model):
	product_seller=models.ForeignKey(User,on_delete=models.CASCADE)
	product_name=models.CharField(max_length=100)
	product_price=models.PositiveSmallIntegerField()
	product_desc=models.TextField()
	product_pic=models.ImageField(upload_to="product_pic/")

	def __str__(self):
		return self.product_seller.fname+" - "+self.product_name

class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.product_name
class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	product_price=models.PositiveSmallIntegerField()
	product_qty=models.PositiveSmallIntegerField()
	total_price=models.PositiveSmallIntegerField()
	payment_status=models.BooleanField(default=False)
	delivery_charge=models.PositiveSmallIntegerField(default=100)

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name


class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)