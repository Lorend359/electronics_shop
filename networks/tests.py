from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .admin import PartnerAdmin, clear_debt_to_supplier
from .models import Partner

User = get_user_model()


class PartnerModelTests(TestCase):
    def setUp(self):
        # Базовые объекты сети
        self.root = Partner.objects.create(
            name="Factory A",
            email="factory@example.com",
            country="RU",
            city="Moscow",
            street="Lenina",
            house_number="1",
        )

    def test_level_root_is_zero(self):
        self.assertEqual(self.root.level, 0)

    def test_three_levels_ok(self):
        network = Partner.objects.create(
            name="Retail Net",
            email="retail@example.com",
            country="RU",
            city="Moscow",
            street="Tverskaya",
            house_number="2",
            supplier=self.root,
        )
        ip = Partner.objects.create(
            name="IP Ivanov",
            email="ip@example.com",
            country="RU",
            city="Moscow",
            street="Arbat",
            house_number="3",
            supplier=network,
        )
        self.assertEqual(network.level, 1)
        self.assertEqual(ip.level, 2)

    def test_cycle_is_forbidden(self):
        a = Partner.objects.create(
            name="A",
            email="a@example.com",
            country="RU",
            city="Moscow",
            street="Main",
            house_number="1",
        )
        b = Partner.objects.create(
            name="B",
            email="b@example.com",
            country="RU",
            city="Moscow",
            street="Main",
            house_number="2",
            supplier=a,
        )
        # Создаём цикл: A -> B -> A
        a.supplier = b
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_depth_more_than_three_forbidden(self):
        a = self.root
        b = Partner.objects.create(
            name="B",
            email="b@example.com",
            country="RU",
            city="Mos",
            street="x",
            house_number="1",
            supplier=a,
        )
        c = Partner.objects.create(
            name="C",
            email="c@example.com",
            country="RU",
            city="Mos",
            street="x",
            house_number="2",
            supplier=b,
        )
        d = Partner(
            name="D",
            email="d@example.com",
            country="RU",
            city="Mos",
            street="x",
            house_number="3",
            supplier=c,
        )
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_negative_debt_forbidden(self):
        self.root.debt_to_supplier = Decimal("-1.00")
        with self.assertRaises(ValidationError):
            self.root.full_clean()


class PartnerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Пользователи
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="pass123",
            is_active=True,
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="pass123",
            is_active=True,
            is_staff=False,
        )

        # Партнёр
        self.root = Partner.objects.create(
            name="Factory A",
            email="factory@example.com",
            country="RU",
            city="Moscow",
            street="Lenina",
            house_number="1",
            debt_to_supplier=Decimal("100.00"),
        )

        self.list_url = reverse("partner-list")
        self.detail_url = lambda pk: reverse("partner-detail", args=[pk])

    def test_non_staff_forbidden(self):
        # Без авторизации → 401
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Авторизован, но не staff → 403
        self.client.force_authenticate(self.user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_and_create(self):
        self.client.force_authenticate(self.staff)
        # List
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Create
        payload = {
            "name": "Retail",
            "email": "r@example.com",
            "country": "RU",
            "city": "Moscow",
            "street": "Tverskaya",
            "house_number": "10",
            "supplier": self.root.pk,
        }
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["debt_to_supplier"], "0.00")  # default

    def test_patch_cannot_change_debt(self):
        self.client.force_authenticate(self.staff)
        old_debt = str(self.root.debt_to_supplier)
        resp = self.client.patch(
            self.detail_url(self.root.pk),
            {"debt_to_supplier": "999.99"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.root.refresh_from_db()
        self.assertEqual(str(self.root.debt_to_supplier), old_debt)

    def test_country_filter(self):
        self.client.force_authenticate(self.staff)
        # Добавим ещё партнёра в другой стране
        Partner.objects.create(
            name="Factory B",
            email="b@example.com",
            country="US",
            city="NY",
            street="5th Ave",
            house_number="100",
        )
        resp = self.client.get(self.list_url + "?country=RU")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["country"] == "RU" for p in resp.data["results"]))

    def test_api_returns_correct_level(self):
        # root -> level 0
        self.client.force_authenticate(self.staff)
        resp = self.client.get(self.detail_url(self.root.pk))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["level"], 0)


class AdminActionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = admin.site
        self.staff = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass123")
        self.partner1 = Partner.objects.create(
            name="P1",
            email="p1@example.com",
            country="RU",
            city="MSK",
            street="s1",
            house_number="1",
            debt_to_supplier=Decimal("10.00"),
        )
        self.partner2 = Partner.objects.create(
            name="P2",
            email="p2@example.com",
            country="RU",
            city="SPB",
            street="s2",
            house_number="2",
            debt_to_supplier=Decimal("5.50"),
        )

    def test_clear_debt_action(self):
        ma = PartnerAdmin(Partner, self.admin_site)
        request = self.factory.post("/", {})
        request.user = self.staff

        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        queryset = Partner.objects.filter(pk__in=[self.partner1.pk, self.partner2.pk])
        clear_debt_to_supplier(ma, request, queryset)

        self.partner1.refresh_from_db()
        self.partner2.refresh_from_db()
        self.assertEqual(self.partner1.debt_to_supplier, Decimal("0.00"))
        self.assertEqual(self.partner2.debt_to_supplier, Decimal("0.00"))
