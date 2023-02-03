from django.shortcuts import render,redirect
from .models import Contact,User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from django.core.mail import send_mail
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import random

def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	amount = int(request.POST['amount'])
	transaction = Transaction.objects.create(made_by=user, amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY
	params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )
	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)
	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	return render(request,'index.html')
def about(request):
	return render(request,'about.html')
def menu(request):
	product=Product.objects.all()
	return render(request,'menu.html',{'product':product})
def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			message=request.POST['message']
		)
		msg="contact save successfully"
		contacts=Contact.objects.all().order_by('-id')[:4]
		return render(request,'contact.html',{'msg':msg,'contacts':contacts} )
	else:
		contacts=Contact.objects.all().order_by('-id')[:4]
		return render(request,'contact.html',{'contacts':contacts})

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic'],
						usertype=request.POST['usertype']
					)
				msg="User signup successfully"
				return render(request,'signup.html',{'msg':msg})
			else:
				msg="Password & confirm does not matched"
				return render(request,'signup.html',{'msg':msg})	
	else:
		return render(request,'signup.html')
def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.firstlogin==False:
					user.firstlogin=True
					user.save()
					msg="Done"
					if user.usertype=="buyer":
						request.session['email']=user.email
						request.session['fname']=user.fname
						request.session['profile_pic']=user.profile_pic.url
						return render(request,'index.html',{'msg':msg})
					else:
						request.session['email']=user.email
						request.session['fname']=user.fname
						request.session['profile_pic']=user.profile_pic.url
						return render(request,'seller-index.html',{'msg':msg})

				else:
					if user.usertype=="buyer":
						request.session['email']=user.email
						request.session['fname']=user.fname
						request.session['profile_pic']=user.profile_pic.url
						wishlists=Wishlist.objects.filter(user=user)
						request.session['wishlist_count']=len(wishlists)
						carts=Cart.objects.filter(user=user,payment_status=False)
						request.session['cart_count']=len(carts)
						return render(request,'index.html')
					else:
						request.session['email']=user.email
						request.session['fname']=user.fname
						request.session['profile_pic']=user.profile_pic.url
						return render(request,'seller-index.html')

			else:
				msg="Incorrect password"
				return render(request,'login.html',{'msg':msg})
		except Exception as e:
			print(e)
			msg="Email not registered"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')


def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')
def profile(request):
	user=User.objects.get(email=request.session['email'])
	if user.usertype=="buyer":

		if request.method=="POST":
			user.fname=request.POST['fname']
			user.lname=request.POST['lname']
			user.mobile=request.POST['mobile']
			user.email=request.POST['email']
			user.address=request.POST['address']
			try:
				user.profile_pic=request.FILES['profile_pic']
			except:
				pass
			user.save()
			msg="Profile Updated Successfully"
			request.session['profile_pic']=user.profile_pic.url
			request.session['fname']=user.fname
			return render(request,"profile.html",{'user':user,'msg':msg})
		else:
			return render(request,'profile.html',{'user':user})
	else:
		if request.method=="POST":
			user.fname=request.POST['fname']
			user.lname=request.POST['lname']
			user.mobile=request.POST['mobile']
			user.email=request.POST['email']
			user.address=request.POST['address']
			try:
				user.profile_pic=request.FILES['profile_pic']
			except:
				pass
			user.save()
			msg="Profile Updated Successfully"
			request.session['profile_pic']=user.profile_pic.url
			request.session['fname']=user.fname
			return render(request,"selllr-profile.html",{'user':user,'msg':msg})
		else:
			return render(request,'seller-profile.html',{'user':user})


def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if user.usertype=="buyer":
		if request.method=="POST":
			old_password=request.POST['old_password']
			new_password=request.POST['new_password']
			cnew_password=request.POST['cnew_password']
			try:
				
				if user.password==old_password:
					if new_password==cnew_password:
						user.password=new_password
						user.save()
						return redirect('logout')
					else:
						msg="new password & confrom password does not matched"
						return render(request,'change-password.html',{'msg':msg})
				else:
					msg="old password  does not matched	"
					return render(request,'change-password.html',{'msg':msg})
			except Exception as e:
				print(e)
				msg="please login frist"
				return render(request,'login.html',{'msg':msg})
		else:
			return render(request,'change-password.html')
	else:
		if request.method=="POST":
			old_password=request.POST['old_password']
			new_password=request.POST['new_password']
			cnew_password=request.POST['cnew_password']
			try:
				
				if user.password==old_password:
					if new_password==cnew_password:
						user.password=new_password
						user.save()
						return redirect('logout')
					else:
						msg="new password & confrom password does not matched"
						return render(request,'seller-change-password.html',{'msg':msg})
				else:
					msg="old password  does not matched	"
					return render(request,'seller-change-password.html',{'msg':msg})
			except Exception as e:
				print(e)
				msg="please login frist"
				return render(request,'login.html',{'msg':msg})
		else:
			return render(request,'seller-change-password.html')

def seller_index(request):
	return render(request,'seller-index.html')

def seller_add_product(request):
	if request.method=="POST":
		product_seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			product_seller=product_seller,
			product_price=request.POST['product_price'],
			product_name=request.POST['product_name'],
			product_desc=request.POST['product_desc'],
			product_pic=request.FILES['product_pic'],
			)
		msg="Product Add Successfully"
		return render(request,'seller-add-product.html',{'msg':msg})
	else:
		return render(request,'seller-add-product.html')

def seller_view_product(request):
	product_seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(product_seller=product_seller)
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-detail.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_name=request.POST['product_name']
		product.product_desc=request.POST['product_desc']
		product.product_price=request.POST['product_price']
		try:
			product.product_pic=request.FILES['product_pic']
		except:
			pass
		product.save()
		msg="Product Updated successfully"
		return render(request,'seller-edit-product.html',{'product':product,'msg':msg})
	else:	
		return render(request,'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller-view-product')

def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	user=User()
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
	except:
		pass
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		Cart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass
	return render(request,'product-detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	msg="Product Added to Wishlist Successfully"
	wishlists=Wishlist.objects.filter(user=user)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')


def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
			user=user,
			product=product,
			product_price=product.product_price,
			product_qty=1,
			total_price=product.product_price,
		)
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price+i.delivery_charge
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request):
	cart=Cart.objects.get(pk=request.POST['pk'])
	product_qty=int(request.POST['product_qty'])
	product_price=cart.product_price
	total_price=product_qty*product_price
	cart.product_qty=product_qty
	cart.total_price=total_price
	cart.save()
	return redirect('cart')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})