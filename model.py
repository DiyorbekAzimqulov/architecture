from typing import Optional, Set
from datetime import date
from dataclasses import dataclass

@dataclass(frozen=True)
class Orderline:
    ref: str
    sku: str
    quantity: int


class OutOfStock(Exception):
    pass


class Batch:

    def __init__(self, reference : str, sku: str, quantity: int, eta: Optional[date] = None):
        self.ref = reference
        self.sku = sku
        self._purchased_quantity = quantity
        self.eta = eta
        self._allocations = set() # Set[Orderline]
    
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference
    
    def __hash__(self):
        return hash(self.reference)
    
    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
    
    def can_allocate(self, line: Orderline) -> bool:
        """
        line only can be allocated if sku matches and required quantity is less than or equal to available quantity
        """
        return self.sku == line.sku and self.available_quantity >= line.quantity

    def deallocate(self, line: Orderline):
        if line in self._allocations:
            self._allocations.remove(line)
    
    def allocate(self, line: Orderline):
        if self.can_allocate(line):
            self._allocations.add(line)
    
    @property
    def allocated_quantity(self):
        return sum([line.quantity for line in self._allocations])
    
    @property
    def available_quantity(self):
        return self._purchased_quantity - self.allocated_quantity
        