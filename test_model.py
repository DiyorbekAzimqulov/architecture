from datetime import date, timedelta
import pytest

from model import Orderline, Batch, OutOfStock
from service import allocate


def make_order_line_n_batch(sku: str, batch_qty: int, line_qty: int, eta=None) -> tuple:
    order_line = Orderline("order-01", sku, quantity=line_qty)
    batch = Batch("batch-01", sku=sku, quantity=batch_qty, eta=eta)
    return batch, order_line


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 5)
    batch.allocate(line)
    assert batch.available_quantity, 5


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 5)
    can_allocate = batch.can_allocate(line)
    assert can_allocate, True
    


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 11)
    can_allocate = batch.can_allocate(line)
    assert can_allocate == False
    


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 10)
    can_allocate = batch.can_allocate(line)
    assert can_allocate


def test_can_only_deallocate_allocated_lines():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 1)
    batch.deallocate(line)
    assert batch.available_quantity == 10


def test_can_only_allocate_line_once():
    batch, line = make_order_line_n_batch("SMALL_CUSHION", 10, 1)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 9


def test_prefers_warehouse_batches_to_shipments():
    batch1 = Batch("B-01", "CUSHION", 10)
    batch2 = Batch("B-02", "CUSHION", 10, today)
    batch3 = Batch("B-03", "CUSHION", 10, tomorrow)
    line = Orderline("O-01", "CUSHION", 5)
    allocate(line, [batch1, batch2, batch3])
    assert batch1.available_quantity == 5
    assert batch2.available_quantity == 10
    assert batch3.available_quantity == 10

def test_prefers_earlier_batches():
    batch1 = Batch("B-01", "CUSHION", 10, today)
    batch2 = Batch("B-02", "CUSHION", 10, tomorrow)
    batch3 = Batch("B-03", "CUSHION", 10, later)
    line = Orderline("O-01", "CUSHION", 5)
    allocate(line, [batch1, batch2, batch3])
    assert batch1.available_quantity == 5
    assert batch2.available_quantity == 10
    assert batch3.available_quantity == 10

def test_allocate_function_returns_batch_reference():
    batch1 = Batch("B-01", "CUSHION", 10, today)
    line = Orderline("O-01", "CUSHION", 5)
    reference = allocate(line, [batch1])
    assert batch1.ref == reference


def test_raises_out_of_stock_exception_if_cannot_allocate(): 
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today) 
    allocate(Orderline('order1', 'SMALL-FORK', 10), [batch])
    with pytest.raises(OutOfStock, match='SMALL-FORK'): allocate(Orderline('order2', 'SMALL-FORK', 1), [batch])