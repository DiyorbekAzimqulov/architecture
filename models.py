from typing import Set, List
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    quantity: int


class Batch:

    def __init__(self, reference, sku, quantity, eta=None):
        self.reference = reference
        self.sku = sku
        self.purchased_quantity = quantity
        self.eta = eta
        self._allocations = set()

    def __eq__(self, other):
        if isinstance(other, Batch):
            return self.reference == other.reference
        return False

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return False
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def available_quantity(self):
        return self.purchased_quantity - sum(line.quantity for line in self._allocations)

    def can_allocate(self, line: OrderLine):
        return line.sku == self.sku and self.available_quantity() >= line.quantity

    def deallocate(self, line):
        if line in self._allocations:
            self._allocations.remove(line)
