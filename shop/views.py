from django.shortcuts import render,redirect,get_object_or_404,get_list_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db.models import F


def product_list_view(request,category_slug=None):

    category = None
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category,slug = category_slug)
        products = products.filter(category=category)
        
    context = {
        'category':category,
        'categories':categories,
        'products':products,
        'site_section':'product_list',
    }
    return render(request,'shop/product_list.html',context)


def product_detail_view(request,slug):

    product = get_object_or_404(Product,slug=slug)
    is_product_in_cart = False

    if request.user.is_authenticated:
        cart = request.user.cart.all()
        for pr in cart:
            if pr.product == product:
                is_product_in_cart = True

    context = {
      'product':product,
      'is_product_in_cart':is_product_in_cart,  

    }

    return render(request,'shop/product_detail.html',context)


@login_required
def cart_view(request):
    cart = ProductInCart.objects.filter(user=request.user)
    total = 0

    for item in cart:
        total += item.get_cost()

    context = {
        'cart':cart,
        'total':total,
        'site_section':'cart',
        'form':OrderForm(),
    }
    return render(request,'shop/cart.html',context)


@login_required
def cart_add_product_view(request,id):
    product = get_object_or_404(Product,id=id)
    ProductInCart.objects.create(product=product,user=request.user,price=product.price)
    product.count = F('count') - 1
    product.save()
    return redirect(product.get_absolute_url())


@login_required
def cart_delete_product_view(request,id):
    product_in_cart = get_object_or_404(ProductInCart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)
    product.count = F('count') + product_in_cart.count
    product.save()
    product_in_cart.delete()
    return redirect('shop:cart')


@login_required
def cart_increment_view(request,id):

    product_in_cart = get_object_or_404(ProductInCart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)

    if product.count == 0:
        return redirect('shop:cart')
    
    product_in_cart.count = F('count') + 1
    product.count = F('count') - 1 
    product.save()
    product_in_cart.save()
    return redirect('shop:cart')


@login_required
def cart_decrement_view(request,id):

    product_in_cart = get_object_or_404(ProductInCart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)

    if product_in_cart.count == 1:
        return redirect('shop:cart')
    
    product_in_cart.count = F('count') - 1
    product.count = F('count') + 1 
    product.save()
    product_in_cart.save()
    return redirect('shop:cart')

@login_required
@require_POST
def order_create_view(request):

    form = OrderForm(request.POST)

    if form.is_valid():

        cd = form.cleaned_data
        user = request.user
        cart = get_list_or_404(user.cart)
        total = Decimal(request.POST['total'].replace(',','.'))

        if cart:

            if user.account > total:

                apartment = cd['apartment']
                if cd['is_private']:
                    apartment = None

                new_order = Order.objects.create(

                                user = user,
                                street = cd['street'],
                                is_private = cd['is_private'],
                                building = cd['building'],
                                apartment = apartment,
                                price = total,    
                            )
            
                for item in cart:
                    ProductInOrder.objects.create(
                        product = item.product,
                        price = item.price,
                        order = new_order,
                        count = item.count,
                    )

                ProductInCart.objects.filter(user = user).delete()
                user.account = F('account') - total
                user.save()
                return render(request,'shop/order_done.html',{'order_id':new_order.id})
            
          
            return render(request,'shop/low_balance.html')
        
    return redirect('shop:cart')

@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user, is_delivered = False)

    context = {
        'orders':orders,
        'site_section':'order_list'
    }

    return render(request,'shop/order_list.html',context)


@login_required
def order_recieved_view(request,id):

    form = UsersProductsForm()

    if request.method == 'POST':
        form = UsersProductsForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product,id = request.POST['product_id'] )
            cd = form.cleaned_data
            UsersProducts.objects.create(
                user = request.user,
                product = product,
                rating = cd['rating'],
                review = cd['review'],
            )
            ProductInOrder.objects.filter(product_id = product.id).delete()
            form = UsersProductsForm()

    order = get_object_or_404(Order,id=id)
    if not order.is_delivered:
        order.is_delivered = True
        order.save()
    products = Product.objects.filter(id__in = order.products.all().values('product_id'))

    context = {
        'form':form,
        'products':products,
        'order_id':order.id,
    }
    return render(request,'shop/order_recieved.html',context)


def about_view(request):
    return render(request,'shop/about.html',{'site_section':'about'})

@require_POST
def review_delete_view(request,id):
    feedback = get_object_or_404(UsersProducts,id=id)
    product = get_object_or_404(Product,id = feedback.product_id)
    feedback.review = None
    feedback.save()
    return redirect(product.get_absolute_url())



