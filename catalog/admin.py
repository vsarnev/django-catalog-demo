from django.contrib import admin

from .models import Category, Product, Tag


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "stock", "is_in_stock")
    list_filter = ("category", "tags")
    search_fields = ("name", "description", "manufacturer")
    filter_horizontal = ("tags",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    list_filter = ("group",)


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
