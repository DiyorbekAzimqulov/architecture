from unittest import TestCase
from datetime import date, timedelta
from .models import Batch, OrderLine
from .services import allocate
today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)
print(today, tomorrow, later)


def make_batch_and_order_line(sku: str, available_amount: int, quantity):
    batch = Batch(reference="B01", sku=sku, quantity=available_amount)
    line = OrderLine(orderid="O01", sku=sku, quantity=quantity)
    return batch, line


class AllocationTest(TestCase):

    def test_allocate_line_reduce_available_quantity(self):
        batch, line = make_batch_and_order_line("SMALL_TABLE", 100, 15)
        batch.allocate(line)

        self.assertEqual(batch.available_quantity(), 85)

# TODO We need not to be able to allocate if the sku of order line and batch are different,
#  also if available amount of goods less than the ordered quantity
    def test_cannot_allocate_if_sku_different(self):
        batch = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=today)
        line = OrderLine(orderid="O02", sku="COFFEE_TABLE", quantity=21)

        self.assertFalse(batch.can_allocate(line))

    def test_cannot_allocate_if_available_amount_is_less_than_order(self):
        batch, line = make_batch_and_order_line("SMALL_TABLE", 100, 150)

        self.assertFalse(batch.can_allocate(line))

    # TODO allocate if there is enough amount of goods

    def test_can_allocate_if_enough_amount(self):
        batch, line = make_batch_and_order_line("SMALL_TABLE", 100, 10)

        self.assertTrue(batch.can_allocate(line))

    # TODO can deallocate only allocated line from batch

    def test_can_only_deallocate_allocated_lines(self):
        batch, unallocated_line = make_batch_and_order_line("SMALL_TABLE", 100, 10)
        batch.allocate(unallocated_line)
        batch.deallocate(unallocated_line)

        self.assertEqual(batch.available_quantity(), 100)

    def test_not_allocate_two_same_line(self):
        batch, line = make_batch_and_order_line("SMALL_TABLE", 100, 10)
        batch.allocate(line)
        batch.allocate(line)
        self.assertEqual(batch.available_quantity(), 90)

    def test_prefers_current_stock_batches_for_shipment(self):
        in_stock_batch = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=None)
        in_shipment_batch = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=tomorrow)
        line = OrderLine(orderid="O1", sku="SMALL_CUSHION", quantity=10)
        allocate(line, [in_stock_batch, in_shipment_batch])

        self.assertEqual(in_stock_batch.available_quantity(), 90)
        self.assertEqual(in_shipment_batch.available_quantity(), 100)

    def test_prefers_fast_coming_good_allocation(self):
        today_stock = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=today)
        tomorrow_stock = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=tomorrow)
        later_stock = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=later)
        line = OrderLine(orderid="O1", sku="SMALL_CUSHION", quantity=10)
        allocate(line, [today_stock, tomorrow_stock, later_stock])
        self.assertEqual(today_stock.available_quantity(), 90)
        self.assertEqual(tomorrow_stock.available_quantity(), 100)
        self.assertEqual(later_stock.available_quantity(), 100)

    def test_allocated_batch_return_reference(self):
        in_stock_batch = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=None)
        in_shipment_batch = Batch(reference="B01", sku="SMALL_CUSHION", quantity=100, eta=tomorrow)
        line = OrderLine(orderid="O1", sku="SMALL_CUSHION", quantity=10)
        allocation = allocate(line, [in_stock_batch, in_shipment_batch])

        self.assertEqual(in_stock_batch.reference, allocation)
