from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from orders.models import DiscountCode
from orders.forms import DiscountCodeForm

class DiscountCodeTests(TestCase):
    def test_fixed_discount_calculation(self):
        # 1. Fixed discount less than subtotal
        discount = DiscountCode.objects.create(code='FIXED10', discount_type='fixed', amount=Decimal('10.00'))
        self.assertEqual(discount.calculate_discount(Decimal('100.00')), Decimal('10.00'))

        # 2. Fixed discount greater than subtotal
        self.assertEqual(discount.calculate_discount(Decimal('5.00')), Decimal('5.00'))

    def test_percentage_discount_calculation(self):
        # 1. Percentage discount less than subtotal
        discount = DiscountCode.objects.create(code='PERC15', discount_type='percentage', amount=Decimal('15.00'))
        self.assertEqual(discount.calculate_discount(Decimal('200.00')), Decimal('30.00'))

        # 2. Percentage discount greater than subtotal (or exactly 100%)
        discount_100 = DiscountCode.objects.create(code='FREE', discount_type='percentage', amount=Decimal('100.00'))
        self.assertEqual(discount_100.calculate_discount(Decimal('50.00')), Decimal('50.00'))

    def test_discount_form_validation(self):
        # Percentage discount <= 100 is valid
        form_valid_perc = DiscountCodeForm(data={
            'code': 'VALID_PERC',
            'discount_type': 'percentage',
            'amount': '15.00'
        })
        self.assertTrue(form_valid_perc.is_valid())

        # Percentage discount > 100 is invalid
        form_invalid_perc = DiscountCodeForm(data={
            'code': 'INVALID_PERC',
            'discount_type': 'percentage',
            'amount': '105.00'
        })
        self.assertFalse(form_invalid_perc.is_valid())
        self.assertIn('__all__', form_invalid_perc.errors)
        self.assertEqual(
            form_invalid_perc.errors['__all__'][0],
            "Lo sconto percentuale non può essere superiore al 100%."
        )

        # Fixed discount > 100 is valid
        form_valid_fixed = DiscountCodeForm(data={
            'code': 'VALID_FIXED',
            'discount_type': 'fixed',
            'amount': '150.00'
        })
        self.assertTrue(form_valid_fixed.is_valid())
