import random
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin,AccessMixin
from django.db.models import F
from django.views.generic import DetailView,ListView,View,TemplateView,FormView
from django.db import transaction


class AboutTemplateView(TemplateView):
    template_name = 'shop/about.html'
    extra_context = {
        'site_section':'about'
    }


class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        self.category = None
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category'] = self.category
        context['site_section'] = 'product_list'
        products = Product.objects.exclude(image__isnull=True).exclude(image='')
        if len(products) >= 20:
            context['rand_products'] = random.sample(list(products), 20)
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['shop/product_partial.html']
        
        return ['shop/product_list.html']


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        is_product_in_cart = False

        if self.request.user.is_authenticated:
            is_product_in_cart = self.request.user.cart.filter(product=product).exists()

        context['is_product_in_cart'] = is_product_in_cart

        return context


class CartListView(LoginRequiredMixin,ListView):
    template_name = 'cart_list.html'
    context_object_name = 'cart'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = context['cart']
        context['form'] = kwargs.get('form', OrderForm())
        context['total'] = sum(product.get_cost() for product in cart)
        context['site_section'] = 'cart'

        return context


class CartAddProductView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        product = get_object_or_404(Product,id=id)

        if product.count == 0:
            return redirect(product.get_absolute_url())
        
        with transaction.atomic():
            cart_item, created = Cart.objects.get_or_create(
                user = request.user,
                product = product,
                defaults={'price': product.price, 'count': 1}
            )
            if not created:
                cart_item.count = F('count') + 1
                cart_item.save(update_fields=['count'])
                cart_item.refresh_from_db()
        
            product.count = F('count') - 1
            product.save(update_fields=['count'])
            product.refresh_from_db()

        return redirect('shop:cart_list')


class CartDeleteProductView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        cart_item = get_object_or_404(Cart,id=id,user=request.user)
        product = get_object_or_404(Product,id = cart_item.product_id)

        with transaction.atomic():
            product.count = F('count') + cart_item.count
            product.save(update_fields=['count'])
            product.refresh_from_db()
            cart_item.delete()

        return redirect('shop:cart_list')


class CartIncrementView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        cart_item = get_object_or_404(Cart,id=id,user=request.user)
        product = get_object_or_404(Product,id = cart_item.product_id)

        if product.count > 0:

            with transaction.atomic():
                cart_item.count = F('count') + 1
                product.count = F('count') - 1 
                product.save(update_fields=['count'])
                product.refresh_from_db()
                cart_item.save(update_fields=['count'])
                cart_item.refresh_from_db()

        return redirect('shop:cart_list')


class CartDecrementView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        cart_item = get_object_or_404(Cart,id=id,user=request.user)
        product = get_object_or_404(Product,id = cart_item.product_id)

        if cart_item.count > 1:

            with transaction.atomic():
                cart_item.count = F('count') - 1
                product.count = F('count') + 1 
                product.save(update_fields=['count'])
                product.refresh_from_db()
                cart_item.save(update_fields=['count'])
                cart_item.refresh_from_db()

        return redirect('shop:cart_list')


class OrderCreateView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        user = self.request.user
        cart = Cart.objects.filter(user=user).select_related('product')
        total = sum(item.get_cost() for item in cart)

        if user.account < total:
            return render(self.request,'shop/low_balance.html')

        form = OrderForm(request.POST)

        if form.is_valid():      
            with transaction.atomic():
                cd = form.cleaned_data
                apartment = None if cd['is_private'] else cd['apartment']

                order = Order.objects.create (
                    user = user,
                    street = cd['street'],
                    is_private = cd['is_private'],
                    building = cd['building'],
                    apartment = apartment,
                    price = total,

                )
                for item in cart:
                    ProductInOrder.objects.create (
                        product = item.product,
                        price = item.price,
                        order = order,
                        count = item.count,
                    )

                cart.delete()
                user.account = F('account') - total
                user.save(update_fields=['account'])
                user.refresh_from_db()
            
            return render(self.request,'shop/order_done.html',{'order_id':order.id})
        
      
        return render(request,'shop/cart_list.html',{
            'cart':cart,
            'form':form,
            'total':total,
            'site_section':'cart',
        })


class OrderListView(LoginRequiredMixin,ListView):
    template_name = 'shop/order_list.html'
    context_object_name = 'orders'
    extra_context = {
        'site_section':'order_list'
    }
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_delivered = False)


class OrderReceivedView(AccessMixin, FormView):
    template_name = 'shop/order_received.html'
    form_class = FeedbackForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        self.order = get_object_or_404(Order, id=self.kwargs['id'], user=request.user)

        if not self.order.is_delivered:
            self.order.is_delivered = True
            self.order.save(update_fields=['is_delivered'])

        self.products = Product.objects.filter(id__in=self.order.products.all().values('product_id'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.products
        context['order_id'] = self.order.id
        return context

    def form_valid(self, form):
        product_id = self.request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        if not self.order.products.filter(product=product).exists():
            return redirect('shop:order_list')

        cd = form.cleaned_data
        Feedback.objects.create(
            user=self.request.user,
            product=product,
            rating=cd['rating'],
            review=cd['review'],
        )

        ProductInOrder.objects.filter(product_id=product.id, order_id=self.order.id).delete()

        return self.render_to_response(self.get_context_data(form=self.form_class()))


class ReviewDeleteView(LoginRequiredMixin,View):
    def post(self,request,id,*args,**kwargs):
        feedback = get_object_or_404(Feedback,id=id,user=request.user)

        if feedback.review:
            feedback.review = None
            feedback.save(update_fields=['review'])

        return redirect(feedback.product.get_absolute_url())


