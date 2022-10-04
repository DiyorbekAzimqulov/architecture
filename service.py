from typing import List
from model import Orderline, Batch, OutOfStock


def allocate(line: Orderline, batches: List[Batch]) -> str:
    """
    allocates line to warehouse batch or earliest batch 
    """
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"We are out of stock for sku {line.sku}")

    batch.allocate(line)
    return batch.ref
