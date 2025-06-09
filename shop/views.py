from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import F
from django.core.paginator import Paginator


def product_list_view(request,category_slug=None):

    category = None
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category,slug = category_slug)
        products = products.filter(category=category)
    
    paginator = Paginator(products,8)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)

    context = {
        'category':category,
        'categories':categories,
        'page_obj':page_obj,
        'site_section':'product_list',
    }

    if request.headers.get('HX-Request'):
        return render(request,'shop/product_partial.html',context)
    
    return render(request,'shop/product_list.html',context)


def product_detail_view(request,slug):

    product = get_object_or_404(Product,slug=slug)
    is_product_in_cart = False

    if request.user.is_authenticated:
        is_product_in_cart = request.user.cart.filter(product=product).exists()

    context = {
      'product':product,
      'is_product_in_cart':is_product_in_cart,  

    }

    return render(request,'shop/product_detail.html',context)


@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).select_related('product')
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
    if product.count == 0:
        return redirect(product.get_absolute_url())
    
    cart_item, created = Cart.objects.get_or_create(
        user = request.user,
        product = product,
        defaults={'price': product.price, 'count': 1}
    )
    if not created:
        cart_item.count = F('count') + 1
        cart_item.save()
        cart_item.refresh_from_db()
   
    product.count = F('count') - 1
    product.save()
    product.refresh_from_db()
    return redirect('shop:cart')


@login_required
def cart_delete_product_view(request,id):
    product_in_cart = get_object_or_404(Cart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)
    product.count = F('count') + product_in_cart.count
    product.save()
    product.refresh_from_db()
    product_in_cart.delete()
    return redirect('shop:cart')


@login_required
def cart_increment_view(request,id):

    product_in_cart = get_object_or_404(Cart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)

    if product.count == 0:
        return redirect('shop:cart')
    
    product_in_cart.count = F('count') + 1
    product.count = F('count') - 1 
    product.save()
    product.refresh_from_db()
    product_in_cart.save()
    product_in_cart.refresh_from_db()
    return redirect('shop:cart')


@login_required
def cart_decrement_view(request,id):

    product_in_cart = get_object_or_404(Cart,id=id)
    product = get_object_or_404(Product,id = product_in_cart.product_id)

    if product_in_cart.count == 1:
        return redirect('shop:cart')
    
    product_in_cart.count = F('count') - 1
    product.count = F('count') + 1 
    product.save()
    product.refresh_from_db()
    product_in_cart.save()
    product_in_cart.refresh_from_db()
    return redirect('shop:cart')

@login_required
@require_POST
def order_create_view(request):

    form = OrderForm(request.POST)

    if form.is_valid():

        cd = form.cleaned_data
        user = request.user
        cart = Cart.objects.filter(user=request.user).select_related('product')
        total = sum(item.get_cost() for item in user.cart.all())

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

                Cart.objects.filter(user = user).delete()
                user.account = F('account') - total
                user.save()
                user.refresh_from_db()
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
            order = get_object_or_404(Order, id=id, user=request.user)
            if not order.products.filter(product=product).exists():
                return redirect('shop:order_list')

            cd = form.cleaned_data
            Feedback.objects.create(
                user = request.user,
                product = product,
                rating = cd['rating'],
                review = cd['review'],
            )
            ProductInOrder.objects.filter(product_id = product.id, order_id=id).delete()
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


@login_required
@require_POST
def review_delete_view(request,id):
    feedback = get_object_or_404(Feedback,id=id,user=request.user)
    product = get_object_or_404(Product,id = feedback.product_id)
    feedback.review = None
    feedback.save()
    return redirect(product.get_absolute_url())


