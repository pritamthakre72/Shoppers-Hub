from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# def home(request):
#  return render(request, 'app/home.html')

class ProductView(View):
	def get(self, request):
		totalitem = 0
		topwears = Product.objects.filter(category='TW')
		bottomwears = Product.objects.filter(category='BW')
		mobiles = Product.objects.filter(category='M')
		laptop = Product.objects.filter(category='L')
		if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
		content = {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'laptop':laptop, 'totalitem':totalitem}
		return render(request, 'app/home.html', content)

def search(request):
    totalitem = 0
    query = request.GET.get('query')
    if query:
        if len(query) > 78:
            products = []
        else:
            products = Product.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__icontains=query)
            )
    else:
        products = Product.objects.none()

    # Check if there are no products found or if the query is empty
    if not query or not products:
        messages.error(request, "No products found or please enter a query to search.")
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
    
    params = {'products': products, 'query': query, 'totalitem': totalitem}
    return render(request, 'app/search.html', params)


class ProductDetails(View):
	def get(self, request, pk):
		totalitem = 0
		product = Product.objects.get(pk=pk)
		item_already_in_cart = False
		if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
			item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
		return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})

@login_required
def add_to_cart(request):
	user=request.user
	product_id = request.GET.get('prod_id')
	product = Product.objects.get(id=product_id)
	Cart(user=user, product=product).save()
	return redirect('/cart')

@login_required
def show_cart(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len (Cart.objects.filter(user=request.user))
		user = request.user
		cart = Cart.objects.filter(user=user)
		# print(cart)
		amount = 0.0
		shipping_amount = 70.0
		total_amount = 0.0
		cart_product = [p for p in Cart.objects.all() if p.user == user]
		# print(cart_product)
		if cart_product:
			for p in cart_product:
				tempamount = (p.quantity * p.product.discounted_price)
				amount += tempamount
				totalamount = amount + shipping_amount
				return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': totalamount, 'amount':amount, 'totalitem':totalitem})
		else:
			return render(request, 'app/emptycart.html')


def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		print(prod_id)
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity += 1
		c.save()
		amount = 0.0
		shipping_amount = 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount

		data = {
			'quantity': c.quantity,
			'amount': amount,
			'totalamount': amount + shipping_amount
		}
		return JsonResponse(data)

def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		print(prod_id)
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity -= 1
		c.save()
		amount = 0.0
		shipping_amount = 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount

		data = {
			'quantity': c.quantity,
			'amount': amount,
			'totalamount': amount + shipping_amount
		}
		return JsonResponse(data)

def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0
		shipping_amount = 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount

		data = {
			'amount': amount,
			'totalamount': amount + shipping_amount
		}
		return JsonResponse(data)

def buy_now(request):   
	return render(request, 'app/buynow.html')

@login_required
def address(request):
	totalitem = 0
	add = Customer.objects.filter(user=request.user)
	if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
	return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary', 'totalitem':totalitem})

@login_required
def orders(request):
	totalitem = 0
	op = OrderPlaced.objects.filter(user=request.user)
	if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
	return render(request, 'app/orders.html', {'order_placed':op, 'totalitem':totalitem})

# def change_password(request):
#  return render(request, 'app/passwordchange.html')

def mobile(request, data=None):
	totalitem = 0
	if data == None:
		mobiles = Product.objects.filter(category='M')
	elif data == 'Android' or data == 'iPhone':
		mobiles = Product.objects.filter(category='M').filter(brand=data)
	elif data == 'below':
		mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
	elif data == 'above':
		mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
	if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
	return render(request, 'app/mobile.html', {'mobiles': mobiles, 'totalitem':totalitem})

def topwears(request, data=None):
	totalitem = 0
	if data == None:
		topwears = Product.objects.filter(category='TW')
	elif data == 'Men' or data == 'Women':
		topwears = Product.objects.filter(category='TW').filter(brand=data)
	elif data == 'below':
		topwears = Product.objects.filter(category='TW').filter(discounted_price__lt=400)
	elif data == 'above':
		topwears = Product.objects.filter(category='TW').filter(discounted_price__gt=400)
	if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
	return render(request, 'app/topwears.html', {'topwears': topwears, 'totalitem':totalitem})

class CustomerRegistrationView(View):
	def get(self, request):
		form = CustomerRegistrationForm()
		return render(request, 'app/customerregistration.html', {'form': form})

	def post(self, request):
		form = CustomerRegistrationForm(request.POST)
		if form.is_valid():
			messages.success(request, 'Thanks for Registering with Us')
			form.save()
		return render(request, 'app/customerregistration.html', {'form': form})

@login_required
def checkout(request):
	totalitem = 0
	user = request.user
	add = Customer.objects.filter(user=user)
	cart_items = Cart.objects.filter(user=request.user)
	amount = 0.0
	shipping_amount = 70.0
	totalamount = 0.0  # Initialize totalamount
	cart_product = [p for p in Cart.objects.all() if p.user == request.user]
	
	if cart_product:
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount
		totalamount = amount + shipping_amount
	if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
	return render(request, 'app/checkout.html', {'add':add, 'totalcost':totalamount, 'cart_items':cart_items, 'totalitem':totalitem})

# def profile(request):
#  return render(request, 'app/profile.html')

@login_required
def payment_done(request):
	user = request.user
	custid = request.GET.get('custid')
	# print("Customer ID", custid)
	customer = Customer.objects.get(id=custid)
	cart = Cart.objects.filter(user = user)
	# print(customer)
	for c in cart:
		OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
		print("Order Saved")
		c.delete()
		print("Cart Item Deleted")
	return redirect("orders")

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
	totalitem = 0
	def get(self, request):
		form = CustomerProfileForm()
		if request.user.is_authenticated:
			totalitem = len (Cart.objects.filter(user=request.user))
		return render(request, 'app/profile.html', {'form':form, 'active': 'btn-primary', 'totalitem':totalitem})
 
	def post(self, request):
		form = CustomerProfileForm(request.POST)
		if form.is_valid():
			usr = request.user
			name = form.cleaned_data['name']
			locality = form.cleaned_data['locality']
			city = form.cleaned_data['city']
			zipcode = form.cleaned_data['zipcode']
			state = form.cleaned_data['state']
			reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
			reg.save()
			messages.success(request, 'Congratulations !! Profile Updated Successfully')
		return render(request, 'app/profile.html', {'form':form, 'active': 'btn-primary'})   
	