from django.db.models import Q
from django.shortcuts import render

from .models import Category, Product, Tag


def product_list(request):
    # Fetch all products, filter category and tags with joins to avoid N+1 queries in the template
    products = Product.objects.select_related("category").prefetch_related("tags")

    # Get filters from query params
    q = request.GET.get("q", "").strip()

    # Get the category from the request
    selected_category = request.GET.get("category", "")

    # Get the tag filters from the request, and filter non-numeric inputs
    selected_tag_ids = [t for t in request.GET.getlist("tags") if t.isdigit()]

    # Get the in-stock filter from the request
    in_stock_only = request.GET.get("in_stock")  # "1" when checked, else None

    # Filter products based on search query, based on multiple fields
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(manufacturer__icontains=q)
            | Q(category__name__icontains=q)
            | Q(tags__name__icontains=q)
            | Q(sku__icontains=q)
        )

    # Filter for in-stock only
    if in_stock_only:
        products = products.filter(stock__gt=0)

    # Filter for category and build tag list for the selected category.
    if selected_category.isdigit():  # Ignore non-numeric inputs for categories
        products = products.filter(category_id=selected_category)

        # Filter tags to hide irrelevant ones
        tags = Tag.objects.filter(product__category_id=selected_category).distinct()
    else:
        tags = Tag.objects.all()

    # Group tags by their group and order for displaying in the template
    tags = tags.order_by("group", "id")

    # Filter for tags - AND across groups, OR within a group
    if selected_tag_ids:
        selected_tags = Tag.objects.filter(id__in=selected_tag_ids)

        # Group tags by their group
        groups = {}
        for tag in selected_tags:
            groups.setdefault(tag.group, []).append(tag.id)

        # AND across groups, OR within a group
        for tag_ids in groups.values():
            products = products.filter(tags__in=tag_ids)

    # Remove duplicates that can occur from multiple tags matching the same product
    products = products.distinct()

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "tags": tags,
        "q": q,
        "in_stock_only": in_stock_only,
        "selected_category": selected_category,
        "selected_tag_ids": selected_tag_ids,
    }

    return render(request, "catalog/product_list.html", context)


def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return render(
            request,
            "catalog/product_detail.html",
            {"product": None, "error": "The specified item does not exist."},
        )
    return render(request, "catalog/product_detail.html", {"product": product})
