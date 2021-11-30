from typing import List
from .models import Batch, OrderLine


def allocate(line: OrderLine, batches: List[Batch]):
    """

    :param line:
    :param batches:
    :return: allocation needs to be done for existing warehouse goods, not arrival ones
    """
    batch = next(b for b in sorted(batches) if b.can_allocate(line))
    batch.allocate(line)

    return batch.reference
