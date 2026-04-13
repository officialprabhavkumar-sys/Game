"""
This module contains all the components related to the world's economy.
"""

from Identity import Identity
from Tags import Tags

from collections import deque

class IndividualEconomyMemory:
    """
    Container to hold and process item prices and rates over a period of transactions.
    """
    
    __slots__ = ["memory", ]
    
    MAX_ENTRIES = 100 # Max number of entries kept for every individual item. Must be more than 0. 0 or less will crash while adding entry.
    
    def __init__(self, memory : dict[str, deque[int]]):
        self.memory = memory
    
    def add_entry(self, identity : Identity, price : int) -> None:
        """
        Adds the price to item's price history memory.
        If current number of entries of an item are full, removes the oldest price from memory.
        """
        
        root_object_id = identity.root_object_id
        if not root_object_id in self.memory:
            self.memory[root_object_id] = deque(maxlen = self.MAX_ENTRIES)
        
        self.memory[root_object_id].append(price)
    
    def get_avg_price_of(self, identity : Identity) -> int | None:
        """
        Returns the average price of item by the given id by history if present, else Returns None.
        """
        
        root_object_id = identity.root_object_id
        if not root_object_id in self.memory:
            return None
        
        item_memory = self.memory[root_object_id]
        item_memory_len = len(item_memory)
        
        if item_memory_len == 0:
            return None
        return int(sum(item_memory)/item_memory_len)

    def get_last_price_of(self, identity : Identity) -> int | None:
        """
        Returns the last price added to the memory for the item by the given id if present, else Returns None.
        """
        
        root_object_id = identity.root_object_id
        if not root_object_id in self.memory:
            return None
        
        item_memory = self.memory[root_object_id]
        if len(item_memory) == 0:
            return None
        return item_memory[-1]
    
    def get_weighed_price_of(self, identity : Identity) -> int | None:
        """
        Returns weighed price (recent prices are given more weight) for the item by the given id if present, else Returns None.
        """
        
        root_object_id = identity.root_object_id
        if not root_object_id in self.memory:
            return None
        
        item_memory = self.memory[root_object_id]
        item_memory_len = len(item_memory)
        
        if item_memory_len == 0:
            return None
        total_weights = 0
        weighed_price = 0
        for weight in range(item_memory_len):
            adjusted_weight = weight + 1
            weighed_price += item_memory[weight] * adjusted_weight
            total_weights += adjusted_weight
        return int(weighed_price / total_weights)
    
    def to_dict(self) -> dict:
        return {
            "memory" : {root_object_id : list(item_memory) for root_object_id, item_memory in self.memory.items()}
        }

class CurrencyBase:
    """
    Container for holding the base values of a currency.
    """
    
    __slots__ = ["identity", "value", "tags"]
    
    def __init__(self, identity : Identity, value : float, tags : Tags | None = None):
        self.identity = identity
        self.value = value
        self.tags = tags or Tags([])
    
    def set_value(self, value : float) -> bool:
        """
        Sets the value of the currency to the provided value.
        
        Returns True if the value was successfully set, else Returns False.
        """
        
        if value < 0:
            return False
        self.value = value
        return True
    
    @property
    def name(self) -> str:
        return self.identity.name
    
    def to_dict(self) -> dict[str, dict | float]:
        return {
            "identity" : self.identity.to_dict(),
            "value" : self.value,
            "tags" : self.tags.to_dict()
        }

class Currency:
    """
    Container for holding a specific amount of a currency.
    """
    
    __slots__ = ["currency_base", "amount"]
    
    def __init__(self, currency_base : CurrencyBase, amount : int):
        self.currency_base = currency_base
        self.amount = amount
    
    def copy(self) -> Currency:
        """
        Returns a copy of the Currency.
        """
        
        return Currency(self.currency_base, self.amount)
        
    @property
    def name(self) -> str:
        return self.currency_base.name
    
    @property
    def value(self) -> float:
        return self.currency_base.value
    
    def to_dict(self) -> dict[str, dict | int]:
        return {
            "currency_base" : self.currency_base.to_dict(),
            "amount" : self.amount
        }

class Coffer:
    """
    Container and Manager for all the currencies of an entity.
    """
    
    __slots__ = ["currencies"]
    
    def __init__(self, currencies : list[Currency]):
        self.currencies = {currency.name : currency  for currency in currencies}
    
    def can_take(self, currency_name : str, amount : int) -> bool:
        """
        Returns True if the amount specified can be removed from the specified currency, else Returns False.
        """
        
        if amount < 0:
            return False
        
        if not currency_name in self.currencies:
            return False
        
        return self.currencies[currency_name].amount >= amount
    
    def take(self, currency_name : str, amount : int) -> Currency | None:
        """
        Returns the specified currency if operation was successful, else Returns None.
        """
        
        if not self.can_take(currency_name, amount):
            return None
        self.currencies[currency_name].amount -= amount
        to_return = Currency(self.currencies[currency_name].currency_base, amount)
        if self.currencies[currency_name].amount == 0:
            self.currencies.pop(currency_name)
        return to_return
    
    def give(self, currency : Currency) -> None:
        """
        Adds the specified currency to the container.
        """
        if currency.amount < 0:
            raise ValueError(f"Cannot give negative amount \"{currency.amount}\" of currency \"{currency.name}\".")
        if currency.name in self.currencies:
            self.currencies[currency.name].amount += currency.amount
            return
        self.currencies[currency.name] = currency.copy()
    
    def has_currency(self, currency_name : str) -> bool:
        """
        Returns True if the currency by the name specified is present, else Returns False.
        """
        
        return currency_name in self.currencies
    
    def amount_of(self, currency_name : str) -> int:
        """
        Returns the amount of the currency specified present.
        """
        
        if not currency_name in self.currencies:
            return 0
        return self.currencies[currency_name].amount
    
    @property
    def total_value(self) -> float:
        return sum(currency.amount * currency.value for currency in self.currencies.values())
    
    def to_dict(self) -> dict:
        return {
            "currencies" : [currency.to_dict() for currency in self.currencies.values()]
        }