from django.shortcuts import render, redirect
from .models import Product, Category, Profile, City
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Max
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from .models import Product, Rating, Reservation
from .forms import RatingForm
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import ChatMessage


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # حفظ المستخدم الحالي
            product.save()
            return redirect('home')  # العودة إلى الصفحة الرئيسية
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # تحقق أن المستخدم الحالي هو من أضاف الإعلان
    if product.user != request.user:
        return HttpResponseForbidden("لا يمكنك تعديل هذا الإعلان.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form})



def search(request):
    query = request.POST.get('searched', '')  # جلب النص المدخل
    city_name = request.POST.get('city', '')  # جلب المدينة (إذا تم اختيارها)

    products = Product.objects.all()

    if query:  # إذا كان هناك نص بحث
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if city_name:  # إذا تم اختيار مدينة
        products = products.filter(city__name__icontains=city_name)

    cities = City.objects.all()  # جلب كل المدن

    return render(request, 'search.html', {
        'searched': products,
        'query': query,
        'cities': cities,
        'selected_city': city_name
    })


def update_info(request):
	if request.user.is_authenticated:
		# Get Current User
		current_user = Profile.objects.get(user__id=request.user.id)
		# Get Current User's Shipping Info
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		
		# Get original User Form
		form = UserInfoForm(request.POST or None, instance=current_user)
		# Get User's Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
		if form.is_valid() or shipping_form.is_valid():
			# Save original form
			form.save()
			# Save shipping form
			shipping_form.save()

			messages.success(request, "Your Info Has Been Updated!!")
			return redirect('home')
		return render(request, "update_info.html", {'form':form, 'shipping_form':shipping_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')



def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')
def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "User Has Been Updated!!")
			return redirect('home')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')


def category_summary(request):
	categories = Category.objects.all()
	return render(request, 'category_summary.html', {"categories":categories})	

def category(request, foo):
	# Replace Hyphens with Spaces
	foo = foo.replace('-', ' ')
	# Grab the category from the url
	try:
		# Look Up The Category
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("That Category Doesn't Exist..."))
		return redirect('home')


def product(request, pk):
    product = get_object_or_404(Product, id=pk)
    ratings = Rating.objects.filter(product=product)
    return render(request, 'product.html', {
        'product': product,
        'ratings': ratings
    })


def home(request):
	products = Product.objects.all()
	return render(request, 'home.html', {'products':products})


def about(request):
	return render(request, 'about.html', {})	

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# Do some shopping cart stuff
			current_user = Profile.objects.get(user__id=request.user.id)
			# Get their saved cart from database
			saved_cart = current_user.old_cart
			# Convert database string to python dictionary
			if saved_cart:
				# Convert to dictionary using JSON
				converted_cart = json.loads(saved_cart)
				# Add the loaded cart dictionary to our session
				# Get the cart
				cart = Cart(request)
				# Loop thru the cart and add the items from the database
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ("You Have Been Logged In!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error, please try again..."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out...Thanks for stopping by..."))
	return redirect('home')



def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
			return redirect('update_info')
		else:
			messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})
	


def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }
    


@login_required
def chat(request, product_id, receiver_id):
    product = get_object_or_404(Product, id=product_id)
    receiver = get_object_or_404(User, id=receiver_id)

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                product=product,
                sender=request.user,
                receiver=receiver,
                message=message
            )
            return redirect('chat', product_id=product.id, receiver_id=receiver.id)

    messages = ChatMessage.objects.filter(product=product, sender__in=[request.user, receiver], receiver__in=[request.user, receiver]).order_by('timestamp')
    
    return render(request, 'chat.html', {'product': product, 'messages': messages, 'receiver': receiver})


@login_required
def inbox(request):
    user_products = Product.objects.filter(user=request.user)
    
    # استعلام لتجميع المحادثات حسب آخر رسالة
    messages = ChatMessage.objects.filter(product__in=user_products).values(
        'product', 'sender'
    ).annotate(last_message=Max('timestamp')).order_by('-last_message')

    # جلب التفاصيل الكاملة لآخر رسالة
    last_messages = ChatMessage.objects.filter(
        timestamp__in=[msg['last_message'] for msg in messages]
    ).select_related('product', 'sender')
    
    context = {
        'messages': last_messages,
    }
    return render(request, 'inbox.html', context)


from .models import ChatMessage

def base_context(request):
    if request.user.is_authenticated:
        unread_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {'unread_count': unread_count}



def cart_add(request):
    cart = Cart(request)
    
    if request.method == 'POST' and request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        
        cart.add(product=product, quantity=product_qty)
        
        return JsonResponse({'qty': cart.__len__()})
    
    # في حالة طلب GET، أرجع استجابة افتراضية
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            try:
                rating = form.save(commit=False)
                rating.product = product
                rating.user = request.user
                rating.save()
                messages.success(request, 'تم إضافة تقييمك بنجاح!')
            except IntegrityError:
                messages.warning(request, 'لقد قمت بتقييم هذا المنتج من قبل!')
            return redirect('product', pk=product.id)
        else:
            messages.error(request, 'حدث خطأ أثناء إرسال التقييم.')
            print(form.errors)  # طباعة الأخطاء في الطرفية للتحقق

    return render(request, 'product.html', {'product': product, 'form': RatingForm()})



from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .forms import ReservationForm  # استيراد الفورم
from datetime import datetime

def reserve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # جلب جميع الحجوزات الخاصة بالمستخدم
    user_reservations = Reservation.objects.filter(user=request.user)

    if request.method == "POST":
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')

        # تحويل التواريخ إلى كائنات
        checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()

        # التحقق من وجود حجز متداخل
        overlapping_reservations = Reservation.objects.filter(
            product=product,
            checkin_date__lt=checkout_date,
            checkout_date__gt=checkin_date
        )

        if overlapping_reservations.exists():
            return JsonResponse({'error': 'هذا المنتج محجوز في هذه التواريخ.'}, status=400)

        # إنشاء الحجز
        try:
            reservation = Reservation(
                user=request.user,
                product=product,  # تعيين المنتج بشكل صريح
                checkin_date=checkin_date,
                checkout_date=checkout_date
            )
            reservation.save()
        except Exception as e:
            return JsonResponse({'error': f'حدث خطأ: {str(e)}'}, status=500)

        return JsonResponse({'success': 'تم الحجز بنجاح.'})

    # عرض صفحة الحجز مع الحجوزات
    return render(request, 'reserve_product.html', {
        'product': product,
        'user_reservations': user_reservations  # إرسال الحجوزات إلى القالب
    })


def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'user_reservations.html', {'reservations': reservations})