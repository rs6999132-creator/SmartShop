
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Product



def index(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(
            name__icontains=query
        ) | products.filter(
            description__icontains=query
        )

    return render(request, 'index.html', {
        'products': products,
        'query': query,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product_detail.html', {
        'product': product
    })

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1 or quantity > product.stock:
        return render(request, 'product_detail.html', {
            'product': product,
            'error': 'Please select a valid quantity.'
        })

    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    new_quantity = cart.get(product_id_str, 0) + quantity

    if new_quantity > product.stock:
        return render(request, 'product_detail.html', {
            'product': product,
            'error': 'The requested quantity exceeds available stock.'
        })

    cart[product_id_str] = new_quantity
    request.session['cart'] = cart

    return redirect('cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    if product_id_str not in cart:
        return redirect('cart_detail')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        return redirect('cart_detail')

    if quantity <= 0:
        del cart[product_id_str]
    elif quantity <= product.stock:
        cart[product_id_str] = quantity
    else:
        return redirect('cart_detail')

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')



@require_POST
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')

