"""
This module contains the Inventory container that is used to hold all types of items in the game.
"""

from Items import Item, Stack
from Registry import Registry

class Inventory:
    
    __slots__ = ["capacity", "items", "stacks", "weight"]
    
    def __init__(self, capacity : int, items : dict[str, list[Item]] | None = None, stacks : dict[str, Stack] | None = None):
        self.capacity = capacity
        self.items = items or {}
        self.stacks = stacks or {}
        self.calculate_weight() #Always calculates the weight of items. Instantly loads any adjusted stats.
    
    def add_item(self, item : Item) -> bool:
        """
        Returns True if item was successfully added, else Returns False.
        """
        
        if item.weight + self.weight > self.capacity:
            return False
        
        item_type = item.identity.object_type
        
        if not item_type in self.items:
            self.items[item_type] = []
        
        self.items[item_type].append(item)
        self.weight += item.weight
        return True
        
    def add_stack(self, stack : Stack, item_registry : Registry, empty_other : bool = True) -> bool:
        """
        Returns True if stack was successfully added, else Returns False.
        Requires item_registry in case stack needs to be copied.
        
        Usage:
        empty_other:
            If True, the amount of stack provided is set to 0 after updating already present stack or copying the provided stack.
        """
        
        if stack.weight + self.weight > self.capacity:
            return False
        
        stack_id = stack.item.identity.object_id.split("_")
        stack_id = f"{stack_id[0]}_{stack_id[1]}"
        
        self.weight += stack.weight
        
        if not stack_id in self.stacks:
            self.stacks[stack_id] = stack.copy(item_registry)
            if empty_other:
                stack.amount = 0
            return True
        
        self.stacks[stack_id].merge(stack, empty_other)
        return True
    
    def can_add(self, item : Item | Stack) -> bool:
        """
        Returns True if Item / Stack can be added, else Returns False.
        """
        
        return self.weight + item.weight < self.capacity
    
    def get_item(self, item_id : str) -> Item | None:
        """
        Returns Item if present, else Returns None.
        """
        
        item_type = item_id.split("_")[0]
        if not item_type in self.items:
            return None
        for item in self.items[item_type]:
            if item.identity.object_id == item_id:
                return item
        return None
    
    def get_stack(self, stack_id : str) -> Stack | None:
        """
        Returns Stack if present, else Returns None.
        stack_id must be in the format of ItemType_ItemName
        """
        
        if not stack_id in self.stacks:
            return None
        return self.stacks[stack_id]
    
    def has_item(self, item_id : str) -> bool:
        """
        Returns True if the item_id is present in the inventory, else Returns False.
        """
        
        item_type = item_id.split("_")[0]
        if not item_type in self.items:
            return False
        return item_id in self.items[item_type]
    
    def has_stack(self, stack_id : str) -> bool:
        """
        Returns True if stack_id is present in the inventory, else Returns False.
        """
        
        return stack_id in self.stacks
    
    def remove_item(self, item_id : str) -> bool:
        """
        Returns True if item was successfully removed, else Returns False.
        """
        
        item_type = item_id.split("_")[0]
        if not item_type in self.items:
            return False
        
        to_remove = None
        for index, item in enumerate(self.items[item_type]):
            if item.identity.object_id == item_id:
                to_remove = index
                break
            
        if to_remove:
            self.weight -= self.items[item_type][to_remove].weight
            self.items[item_type].pop(to_remove)
            return True
        return False
    
    def remove_stack(self, stack_id : str) -> bool:
        """
        Returns True if stack was successfully removed, else Returns False.
        stack_id must be in the format of ItemType_ItemName
        """
        
        if not stack_id in self.stacks:
            return False
        self.weight -= self.stacks[stack_id].weight
        self.stacks.pop(stack_id)
        return True
    
    def remove_items_of_type(self, item_type : str) -> bool:
        """
        Returns True if all items of the type specified were removed, else Returns False.
        """
        
        if not item_type in self.items:
            return False
        self.items.pop(item_type)
        return True
    
    def can_add_objects(self, objects : list[Item | Stack]) -> bool:
        """
        Returns True if all objects from the given list can be added to the inventory, else returns False.
        """
        
        weight_after_adding_all = self.weight
        for item in objects:
            weight_after_adding_all += item.weight
        
        return weight_after_adding_all <= self.capacity
    
    def add_objects(self, objects : list[Item | Stack], item_registry : Registry, empty_other : bool = True, add_partial : bool = False) -> tuple[bool, int]:
        """
        Adds all objects to the inventory.
        
        Usage:
            1. objects : list of items and stacks that are to be added to the inventory.
            2. item_registry : Item's Registry.
            3. empty_other : If True, any Stack objects in objects list will be emptied after adding their amounts to inventory.
            4. add_partial : if True even if all the objects can't be added to the inventory,
            all those that can be, will be.
        
        Return:
            Returns a tuple with it's first element being a boolean which represents the success based on the parameters given.
            The second element is an integer which represents the number of elements successfully added to the inventory.
        First element will be True in two cases:
        If add_partial is False, it will be True if all elements were added.
        If add_partial is True, it will be True if even one element was added.
        """
        
        to_add = []
        weight_after_addition = self.weight
        for item in objects:
            weight_after_addition += item.weight
            if weight_after_addition > self.capacity:
                break
            to_add.append(item)
        
        to_add_len = len(to_add)
        
        if not add_partial:
            if to_add_len != len(objects):
                return (False, 0)
        
        for item in to_add:
            if isinstance(item, Item):
                self.add_item(item)
            else:
                self.add_stack(item, item_registry, empty_other)
        
        return (to_add_len > 0, to_add_len)
    
    def calculate_weight(self) -> None:
        """
        Calculates and assigns total weight of all the items to the weight attribute of the object.
        """
        
        weight = 0
        for items in self.items.values():
            for item in items:
                weight += item.weight
        
        for stack in self.stacks.values():
            weight += stack.weight
        
        self.weight = weight
    
    @property
    def is_full(self) -> bool:
        """
        Returns True if weight >= capacity.
        """
        
        return self.weight >= self.capacity
    
    def __str__(self) -> str:
        string = f"Capacity : {self.capacity}\nFilled : {self.weight}\n"
        if self.items:
            string += "Items :\n"
            for item_type in self.items.keys():
                string += item_type + " :\n"
                for item in self.items[item_type]:
                    string += item.__str__()
        
        if self.stacks:
            string += "Stacks :\n"
            for stack in self.stacks.values():
                string += stack.__str__()
        
        if not string:
            string += "Stack is empty"
        
        return string
    
    def to_dict(self) -> dict:
        return {
            "capacity" : self.capacity,
            "items" : {item_type : [item.to_dict() for item in self.items[item_type]] for item_type in self.items.keys()},
            "stacks" : {stack_id : self.stacks[stack_id].to_dict() for stack_id in self.stacks.keys()},
        }