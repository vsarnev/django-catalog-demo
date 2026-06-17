from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Tag


class CatalogTests(TestCase):
    def setUp(self):
        self.wire = Category.objects.create(name="Wire & Cable")
        self.conduit = Category.objects.create(name="Conduit")

        self.copper = Tag.objects.create(name="Copper", group="Material")
        self.aluminum = Tag.objects.create(name="Aluminum", group="Material")
        self.g12 = Tag.objects.create(name="12 AWG", group="Gauge")
        self.g14 = Tag.objects.create(name="14 AWG", group="Gauge")
        self.nema = Tag.objects.create(name="NEMA 3R", group="Enclosure Rating")

        # P1: copper + 12 AWG, in wire category
        self.p1 = Product.objects.create(
            name="Copper 12",
            sku="C12",
            category=self.wire,
            stock=5,
            description="red copper building wire",
        )
        self.p1.tags.set([self.copper, self.g12])

        # P2: copper + 14 AWG, in wire category, out of stock
        self.p2 = Product.objects.create(
            name="Copper 14", sku="C14", category=self.wire, stock=0
        )
        self.p2.tags.set([self.copper, self.g14])

        # P3: aluminum + 12 AWG, in wire category
        self.p3 = Product.objects.create(
            name="Aluminum 12", sku="A12", category=self.wire, stock=3
        )
        self.p3.tags.set([self.aluminum, self.g12])

        # P4: Junction Box, NEMA 3R enclosure, in conduit category
        self.p4 = Product.objects.create(
            name="Junction Box", sku="JB1", category=self.conduit, stock=2
        )
        self.p4.tags.set([self.nema])

        self.url = reverse("catalog:product_list")

    def names(self, response):
        """Helper: the set of product names the view returned."""
        return {p.name for p in response.context["products"]}

    def test_search_matches_description(self):
        # copper is in P1 and P2's description
        names = self.names(self.client.get(self.url, {"q": "copper"}))
        self.assertEqual(names, {self.p1.name, self.p2.name})

    def test_tags_and_across_groups(self):
        # copper + 12 AWG tag should only give P1
        names = self.names(
            self.client.get(self.url, {"tags": [self.copper.id, self.g12.id]})
        )
        self.assertEqual(names, {self.p1.name})

    def test_tags_or_within_group(self):
        # copper OR aluminum (Material) gives P1, P2, P3
        names = self.names(
            self.client.get(self.url, {"tags": [self.copper.id, self.aluminum.id]})
        )
        self.assertEqual(names, {self.p1.name, self.p2.name, self.p3.name})

    def test_category_filter(self):
        # category wire should give P1, P2, P3
        names = self.names(self.client.get(self.url, {"category": self.wire.id}))
        self.assertEqual(names, {self.p1.name, self.p2.name, self.p3.name})

    def test_in_stock_filter(self):
        # in_stock should only give P1, P3, P4
        names = self.names(self.client.get(self.url, {"in_stock": "1"}))
        self.assertEqual(names, {self.p1.name, self.p3.name, self.p4.name})

    def test_search_for_sku(self):
        # searching for C12 should only return P1
        names = self.names(self.client.get(self.url, {"q": "C12"}))
        self.assertEqual(names, {self.p1.name})

    def test_hide_irrelevant_tags(self):
        # when category=wire, only show tags that apply to wire products
        response = self.client.get(self.url, {"category": self.wire.id})
        tags = set(response.context["tags"])
        self.assertIn(self.copper, tags)
        self.assertIn(self.aluminum, tags)
        self.assertIn(self.g12, tags)
        self.assertIn(self.g14, tags)

        self.assertNotIn(self.nema, tags)

    def test_category_and_tags(self):
        # category wire and aluminum tag should give only P3
        names = self.names(
            self.client.get(
                self.url, {"category": self.wire.id, "tags": [self.aluminum.id]}
            )
        )
        self.assertEqual(names, {self.p3.name})

    def test_tag_and_in_stock(self):
        # copper and in stock should only give P1
        names = self.names(
            self.client.get(self.url, {"tags": [self.copper.id], "in_stock": "1"})
        )
        self.assertEqual(names, {self.p1.name})

    def test_no_duplicate_rows(self):
        # copper matches p1 on both its name and its Copper tag
        response = self.client.get(self.url, {"q": "copper"})
        self.assertEqual(len(response.context["products"]), 2)

    def test_non_numeric_category(self):
        # category filter with non-numeric value should return all products, not error
        names = self.names(self.client.get(self.url, {"category": "abc"}))
        self.assertEqual(names, {self.p1.name, self.p2.name, self.p3.name, self.p4.name})

    def test_non_numeric_tags(self):
        # tags filter with non-numeric value should return all products, not error
        names = self.names(self.client.get(self.url, {"tags": "abc"}))
        self.assertEqual(names, {self.p1.name, self.p2.name, self.p3.name, self.p4.name})

    def test_invalid_pk(self):
        # product detail with an invalid pk should return error
        url = reverse("catalog:product_detail", args=(999,))
        response = self.client.get(url)
        self.assertContains(response, "The specified item does not exist.")
