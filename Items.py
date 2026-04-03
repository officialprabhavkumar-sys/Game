"""
This module contains the Item and Stack classes used to represent all item objects in the game.
"""

from Identity import Identity
from ItemComponents import Usable, Equippable, Armor, MeleeWeapon, RangedWeapon
from Registry import Registry

from copy import deepcopy

class Item:
    """
    Represents a single in-game item with it's core identity and optional behavior components.
    
    It contains :
    1. identity : Identity : Object containing name, object id and description of the item.
    2. usable : Usable : Optional component that allows an item to be used in game by the player.
    3. equippable : Equippable : Optional component that allows an item to be equipped.
    4. weight : float : The weight of the item.
    5. price : int : The price of the item according to the standard calculation unit.
    
    Items can be either stackable or unstackable depending on whether they contain attributes that make each instance unique.
    eg. Durability.
    """
    
    __slots__ = ["identity", "usable", "equippable", "weight", "price"]
    
    unstackable_equippable_components = (Armor, MeleeWeapon, RangedWeapon) #All equippable components that make an item unstackable.
    
    def __init__(self, identity : Identity, usable : Usable | None = None, equippable : Equippable | None = None, weight : float = 0, price : int = 1):
        self.identity = identity
        self.usable = usable
        self.equippable = equippable
        self.weight = weight
        self.price = price
    
    def copy(self, item_registry : Registry) -> Item:
        """
        Returns a copy of the object and automatically assigns new id.
        Requires Item Registry for new identity to be assigned to the object.
        """
        
        new_item = deepcopy(self)
        object_id_list = self.identity.object_id.split("_")
        object_type = object_id_list[0]
        object_name = object_id_list[1]
        new_item.identity.object_id = f"{object_type}_{object_name}_{item_registry.generate_next_int_id_for(object_type)}"
        return new_item
    
    def copy_and_set_id(self, new_object_id : str) -> Item:
        """
        Returns a copy of the object with it's object_id set to the provided new_object_id.
        """
        
        new_item = deepcopy(self)
        new_item.identity.object_id = new_object_id
        return new_item
    
    def __str__(self) -> str:
        
        return f"Id : {self.identity}\nUsable :{self.usable}\nEquippable : {self.equippable}"

    @property
    def is_stackable(self) -> bool:
        """
        Returns True if the item is stackable, else returns False.
        
        Internally checks for unstackable equippable's attributes.
        """
        
        if not self.equippable:
            return True
        
        if isinstance(self.equippable.item, self.unstackable_equippable_components):
            return False
        return True
    
    def to_dict(self) -> dict:
        return {
            "identity" : self.identity.to_dict(),
            "usable" : self.usable.to_dict() if self.usable else None,
            "equippable" : self.equippable.to_dict() if self.equippable else None,
            "weight" : self.weight,
            "price" : self.price
        }
    
class Stack:
    """
    Represents a collection of identical items grouped together as a single stack.
    
    A stack is used to efficiently manage multiple copies of the same item in an efficient manner.
    
    It contains :
    1. item : Item : A single instance of the item to be used as the base.
    2. amount : int : The number of items in the stack.
    """
    
    __slots__ = ["item", "amount"]
    
    def __init__(self, item : Item, amount : int):
        self.item = item
        self.amount = amount
    
    def merge(self, other : Stack, empty_other : bool = True) -> bool:
        """
        Merges the other stack's amount to current stack if item identity is same.
        If merge is successful returns True, else Returns False.
        
        Usage:
        empty_other : 
        If True, set's other's amount to 0.
        """
        
        if not self.can_merge(other):
            return False
        
        self.amount += other.amount
        
        if empty_other:
            other.amount = 0
            
        return True
    
    def can_merge(self, other : Stack) -> bool:
        """
        Returns True if other stack can be merged with current stack, else returns False.
        """
        
        return self.item.identity == other.item.identity
    
    def increase_amount(self, amount : int = 1) -> None:
        """
        Increases present amount by the specified amount.
        Absolute amount is used.
        """
        
        amount = abs(int(amount))
        
        self.amount += amount
    
    def decrease_amount(self, amount : int = 1) -> bool:
        """
        Returns True if the specified amount was successfully lowered from the present amount.
        Absolute amount is used.
        """
        
        amount = abs(int(amount))
        
        if (self.amount - amount) > 0:
            self.amount -= amount
            return True
        return False
    
    def take(self, item_registry : Registry) -> Item | None:
        """
        Lowers item amount from the stack by one and returns a deepcopy of the item.
        If amount <= 0, None will be returned.
        Requires Item Registry for new identity to be assigned to the object.
        """
        
        if self.amount <= 0:
            return None
        
        self.amount -= 1 # directly changing value to avoid unnecessary "if" checks of decrease_amount method.
        
        return self.item.copy(item_registry)
    
    def copy(self, item_registry : Registry) -> Stack:
        """
        Returns a copy of the stack.
        Requires Item Registry for new identity to be assigned to the object.
        """
        
        return Stack(self.item.copy(item_registry), self.amount)
    
    @property
    def weight(self) -> float:
        """
        Total weight of the items in the stack.
        """
        
        return self.item.weight * self.amount
    
    @property
    def is_empty(self) -> bool:
        """
        True if amount == 0, else False.
        """
        
        return self.amount == 0
    
    @property
    def can_take(self) -> bool:
        """
        True if amount > 0, else False.
        """
        
        return self.amount > 0

    def __str__(self) -> str:
        return f"Item : {self.item}\nAmount: {self.amount}\nWeight : {self.weight}"
    
    def to_dict(self) -> dict:
        return {
            "item" : self.item.to_dict(),
            "amount" : self.amount
        }