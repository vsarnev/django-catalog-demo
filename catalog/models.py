from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)  # Wire, Conduit, Junction Box, etc.

    def __str__(self):
        return self.name


class Tag(models.Model):
    class Group(models.TextChoices):
        MATERIAL = "Material"
        GAUGE = "Gauge"
        AMPERAGE = "Amperage"
        VOLTAGE = "Voltage"
        INSULATION = "Insulation"
        TRADE_SIZE = "Trade Size"
        ENCLOSURE_RATING = "Enclosure Rating"
        ENVIRONMENTAL_RATING = "Environmental Rating"

    name = models.CharField(max_length=50)  # Copper, 12AWG, 20A, etc.
    group = models.CharField(
        max_length=50, choices=Group.choices, blank=True
    )  # Material, Gauge, Amperage, etc.

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)  # 1" Rigid Galvanized Conduit, etc.
    description = models.TextField(
        blank=True
    )  # Rigid galvanized steel conduit (RMC) for harsh environments.
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT
    )  # FK to Category, PROTECT stops category deletion if products reference it
    tags = models.ManyToManyField(
        Tag, blank=False
    )  # M2M to Tag, blank=False means a product must have at least one tag
    stock = models.PositiveIntegerField(default=0)  # stock count, 0 means out of stock
    sku = models.CharField(max_length=100, unique=True)  # ALL-RGC1, etc.
    manufacturer = models.CharField(max_length=100, blank=True)  # Leviton, etc.

    class Meta:
        # Order products alphabetically by name by default
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        # Allows templates to directly check the property instead of comparing stock > 0 themselves
        return self.stock > 0
