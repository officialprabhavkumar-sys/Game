"""
This module contains almost all the components that make up any entity and it's behaviour in the game.
"""

from Items import Item, Stack
from Inventory import Inventory

class EnergyContainer:
    """
    Generic container for any quantifiable entity resource.
    
    Attributes:
    1. absolute_maximum_amount : int : Hard capacity. Cannot be exceeded under any circumstances.
    2. current_amount : int : The current value of the resource.
    3. soft_maximum_amount : int : Base capacity before modifiers are applied.
    4. maximum_amount_override_mult : float : Multiplier applied to soft_maximum_amount.
    5. maximum_amount_override_absolute : int : Flat value added to soft_maximum_amount.
    6. oversaturation_dispersion_percentage : float : Percentage of soft_maximum_amount removed per tick when current amount exceeds soft_maximum_amount.
    
    Usage:
    absolute_maximum_amount is the hard capacity of the container.
    adjusted_maximum_amount will always be less than or equal to absolute_maximum_amount.
    maximum_amount_override_mult and maximum_amount_override_absolute are to be used for oversaturation mechanics.
    oversaturation_dispersion_percentage is the percentage amount relative to soft_maximum_amount decreased from current_maximum when current_amount is more than soft_maximum_amount.
    
    use adjusted_maximum_amount for maximum amount adjusted with overrides.
    use disperse_oversaturated method to decrease current_amount by the oversaturation_dispersion_percentage when current_amount is more than soft_maximum_amount.
    """
    
    __slots__ = ["absolute_maximum_amount", "current_amount", "soft_maximum_amount", "maximum_amount_override_mult", "maximum_amount_override_absolute", "oversaturation_dispersion_percentage"]
    
    def __init__(self, absolute_maximum_amount : int, current_amount : int, soft_maximum_amount : int | None = None, maximum_amount_override_mult : float = 1.0, maximum_amount_override_absolute : int = 0, oversaturation_dispersion_percentage : float = 0.01):
        self.absolute_maximum_amount = absolute_maximum_amount
        self.current_amount = current_amount
        self.soft_maximum_amount = soft_maximum_amount or absolute_maximum_amount
        self.maximum_amount_override_mult = maximum_amount_override_mult
        self.maximum_amount_override_absolute = maximum_amount_override_absolute
        self.oversaturation_dispersion_percentage = oversaturation_dispersion_percentage
    
    @property
    def adjusted_maximum_amount(self) -> int:
        """
        Practical hard capacity of the container.
        """
        
        return min(self.absolute_maximum_amount, int(self.soft_maximum_amount * self.maximum_amount_override_mult) + self.maximum_amount_override_absolute)

    def disperse_oversaturated(self) -> int:
        """
        Decreases current_amount by the oversaturation_dispersion_percentage when current_amount is more than soft_maximum_amount.
        This method does nothing if current_amount is less than soft_maximum_amount.
        Returns the amount of resource decreased.
        Resource is always decreased in integer values, never floats.
        Resource will not drop below soft_maximum_amount, only oversaturated amount will be decreased.
        
        Note:
        if soft_maximum_amount * self.oversaturation_dispersion_percentage < 1, no amount will be reduced.
        """
        
        if self.current_amount < self.soft_maximum_amount:
            return 0
        amount_to_reduce = abs(int(self.soft_maximum_amount * self.oversaturation_dispersion_percentage))
        amount_to_reduce = min(self.current_amount - self.soft_maximum_amount, amount_to_reduce) # never drop below soft_maximum_amount
        self.current_amount -= amount_to_reduce
        return amount_to_reduce
    
    def consume(self, amount : int) -> None:
        """
        Decreases current_amount by the amount specified.
        current_amount will never drop below zero when using this method.
        Absolute integer value of amount is used (amount specified can be +/- but it will be used like positive).
        """
        
        amount = abs(int(amount))
        self.current_amount = max(0, self.current_amount - amount)
    
    def add(self, amount : int) -> None:
        """
        Increases current_amount by amount specified.
        current_amount will never increase beyond adjusted_maximum_amount when using this method.
        Absolute integer value of amount is used (amount specified can be +/- but it will be used like positive).
        """
        
        amount = abs(int(amount))
        self.current_amount = min(self.adjusted_maximum_amount, self.current_amount + amount)
    
    def decrease_from_oversaturated_amount(self, amount : int) -> None:
        """
        Decreases the amount specified from the oversaturated amount.
        This method will never decrease the current_amount below soft_maximum_amount.
        Absolute integer value of amount is used (amount specified can be +/- but it will be used like positive).
        """
        
        amount = abs(int(amount))
        if self.current_amount < self.soft_maximum_amount:
            return
        self.current_amount = max(self.soft_maximum_amount, self.current_amount - amount)
    
    def can_consume(self, amount : int) -> bool:
        """
        Returns True if current_amount >= amount specified.
        Absolute integer value of amount is used (amount specified can be +/- but it will be used like positive).
        """
        
        amount = abs(int(amount))
        return self.current_amount >= amount
    
    @property
    def is_empty(self) -> bool:
        """
        True if current_amount == 0, else False.
        """
        
        return self.current_amount == 0
    
    @property
    def is_oversaturated(self) -> bool:
        """
        True if current_amount > soft_maximum_amount, else False.
        """
        
        return self.current_amount > self.soft_maximum_amount
    
    @property
    def is_full(self) -> bool:
        """
        True if current_amount equals soft_maximum_amount (base capacity before modifiers).
        Note: This does not check against adjusted_maximum_amount. 
        If you want to check if the container is at its practical maximum (after overrides), use is_fully_oversaturated.
        """
        
        return self.current_amount == self.soft_maximum_amount
    
    @property
    def is_fully_oversaturated(self) -> bool:
        """
        True if current_amount == adjusted_maximum_amount, else False.
        """
        
        return self.current_amount == self.adjusted_maximum_amount

    def to_dict(self) -> dict:
        return {
            "absolute_maximum_amount" : self.absolute_maximum_amount,
            "current_amount" : self.current_amount,
            "soft_maximum_amount" : self.soft_maximum_amount,
            "maximum_amount_override_mult" : self.maximum_amount_override_mult,
            "maximum_amount_override_absolute" : self.maximum_amount_override_absolute,
            "oversaturation_dispersion_percentage" : self.oversaturation_dispersion_percentage
        }

class Stats:
    """
    Container for holding statistics of an entity.
    """
    
    __slots__ = ["health", "stamina", "strength", "agility"]
    
    def __init__(self, health : int, stamina : int, strength : int, agility : int):
        self.health = health
        self.stamina = stamina
        self.strength = strength
        self.agility = agility
    
    @property
    def is_alive(self) -> bool:
        """
        Returns True if health is more than 0, else returns False.
        """
        
        return self.health > 0
    
    def to_dict(self) -> dict:
        return {
            "health" : self.health,
            "stamina" : self.stamina,
            "strength" : self.strength,
            "agility" : self.agility
        }

class PhysicalCultivation:
    """
    Container for holding physical attributes of an entity.
    
    Attribute:
    1. name : str
    2. points_left : int : Unassigned points that can be assigned to any attribute.
    3. stats : Stats : Values for different stats.
    4. health : EnergyContainer : Health of the entity.
    5. stamina : EnergyContainer : Stamina of the entity.
    """
    
    __slots__ = ["name", "level", "points_left", "stats", "health", "stamina"]
    
    def __init__(self, name : str, level : int, points_left : int, stats : Stats, health : EnergyContainer, stamina : EnergyContainer):
        self.name = name
        self.level = level
        self.points_left = points_left
        self.stats = stats
        self.health = health
        self.stamina = stamina
    
    @property
    def is_alive(self) -> bool:
        """
        Returns True if health is more than 0, else returns False.
        """
        
        return self.stats.is_alive
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "level" : self.level,
            "points_left" : self.points_left,
            "stats" : self.stats.to_dict(),
            "health" : self.health.to_dict(),
            "stamina" : self.stamina.to_dict()
        }

class QiCultivation:
    """
    Container for holding Qi Cultivation types.
    
    Attributes:
    1. name : str
    2. mortal : EnergyContainer
    3. immortal : EnergyContainer
    4. celestial : EnergyContainer
    """
    
    __slots__ = ["name", "level", "mortal", "immortal", "celestial"]
    
    def __init__(self, name : str, level : int, mortal : EnergyContainer, immortal : EnergyContainer, celestial : EnergyContainer):
        self.name = name
        self.level = level
        self.mortal = mortal
        self.immortal = immortal
        self.celestial = celestial
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "level" : self.level,
            "mortal" : self.mortal.to_dict(),
            "immortal" : self.immortal.to_dict(),
            "celestial" : self.celestial.to_dict()
        }

class SoulCultivation:
    """
    Container for holding Soul Cultivation attributes of an entity.
    
    Attributes:
    1. name : str
    2. soul : EnergyContainer
    """
    
    __slots__ = ["name", "level", "soul"]
    
    def __init__(self, name : str, level : int, soul : EnergyContainer):
        self.name = name
        self.level = level
        self.soul = soul
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "level" : self.level,
            "soul" : self.soul.to_dict()
        }

class Cultivation:
    """
    Container for holding PhysicalCultivation, QiCultivation, and SoulCultivation.
    
    Attributes:
    1. physical : PhysicalCultivation
    2. qi : QiCultivation
    3. soul : SoulCultivation
    """
    
    __slots__ = ["physical", "qi", "soul"]
    
    def __init__(self, physical : PhysicalCultivation, qi : QiCultivation, soul : SoulCultivation):
        self.physical = physical
        self.qi = qi
        self.soul = soul
    
    @property
    def is_alive(self) -> bool:
        """
        Returns True if physical cultivation's health is more than 0, else returns False.
        """
        
        return self.physical.is_alive
    
    def to_dict(self) -> dict:
        return {
            "physical" : self.physical.to_dict(),
            "qi" : self.qi.to_dict(),
            "soul" : self.soul.to_dict()
        }

class MovementNode:
    """
    This container holds the data for npcs to move around and change their places based on time.
    
    Attributes:
    1. node_id : str : Id of the node.
    2. hour : int : The hour the node starts to take affect.
    3. minute : int : The minue of the hour the node starts to take affect.
    4. sublocation : str : The sublocation where the npc is to be transported when the node is in affect.
    5. active : bool : A MovementNode is only used when it's active.
    """
    
    
    __slots__ = ["node_id", "hour", "minute", "sublocation", "active"]
    
    def __init__(self, node_id : str, hour : int, minute : int, sublocation : str, active : bool):
        self.node_id = node_id
        self.hour = hour
        self.minute = minute
        self.sublocation = sublocation
        self.active = active
    
    def to_dict(self) -> dict:
        return {
            "node_id" : self.node_id,
            "hour" : self.hour,
            "minute" : self.minute,
            "sublocation" : self.sublocation,
            "active" : self.active
        }

class MoveSet:
    """
    Container for holding MovementNode(s).
    It is used for npcs to move around and change their places based on time.
    
    Attributes:
    1. nodes : list[MovementNode] : List of MovementNodes(s).
    2. active : bool : MoveSet will only be used if it's active.
    3. priority_level : int : Defines the priority the MoveSet gets if two or more MoveSets are active at the same time.
    4.nodes_dict : dict[int, MovementNode] : Created from "initialize_nodes_dict" method. It is used in "get_node_for" method.
    """
    
    __slots__ = ["moveset_id", "nodes", "active", "priority_level", "sorted_keys", "nodes_dict"]
    
    def __init__(self, moveset_id : str, nodes : list[MovementNode], active : bool, priority_level : int = 0):
        self.moveset_id = moveset_id
        self.nodes = nodes
        self.active = active
        self.priority_level = priority_level
        self.initialize_nodes_dict()
    
    def initialize_nodes_dict(self) -> None:
        """
        Sorts the keys of and initializes nodes_dict.
        """
        nodes_dict = {((node.hour * 60) + node.minute) : node for node in self.nodes if node.active}
        self.sorted_keys = sorted(nodes_dict)
        self.nodes_dict = {time_key : nodes_dict[time_key] for time_key in self.sorted_keys}
    
    def get_node_for(self, hour : int, minute : int) -> MovementNode | None:
        """
        Returns the MovementNode to be used for the current time.
        A MovementNode is used until another MovementNode's time begins.
        If no MovementNode is present for the current time, returns the very last node entry.
        
        Note:
        If no active nodes are found, returns None.
        """
        
        if not self.nodes_dict:
            return None
        
        current_time = (hour * 60) + minute
        
        last_key = None
        
        for time_key in self.sorted_keys:
            if time_key <= current_time:
                last_key = time_key
            if time_key > current_time:
                break
            
        if isinstance(last_key, int):
            return self.nodes_dict[last_key]
        return self.nodes_dict[self.sorted_keys[-1]] # wrap-around.
        #That's alot of ifs. I don't like it, but it works and is easy to understand.
    
    @property
    def is_empty(self) -> bool:
        """
        Returns True if no active MovementNodes are preset.
        """
        
        return len(self.nodes_dict) == 0
    
    def to_dict(self) -> dict:
        return {
            "nodes" : [node.to_dict() for node in self.nodes],
            "active" : self.active
        }

class MoveSetsManager:
    """
    Container for holding and managing movesets.
    If two or more movesets with same priority_level have the same moveset_id, the very last one is used.
    """
    
    __slots__ = ["movesets", "usable_movesets"]
    
    def __init__(self, movesets : list[MoveSet]):
        self.movesets = movesets
        self.initialize_usable_movesets()
        
    def initialize_usable_movesets(self) -> None:
        """
        Initializes usable_movesets and groups them by priority_level.
        If two or more movesets with same priority_level have the same moveset_id, the very last one is used.
        """
        
        usable_movesets = {}
        for moveset in self.movesets:
            if not moveset.active or moveset.is_empty:
                continue
            if not moveset.priority_level in usable_movesets:
                usable_movesets[moveset.priority_level] = {}
            usable_movesets[moveset.priority_level][moveset.moveset_id] = moveset
        
        self.usable_movesets : dict[int, dict[str, MoveSet]] = {priority_level : usable_movesets[priority_level] for priority_level in sorted(usable_movesets, reverse = True)}
    
    def get_node_for(self, hour : int, minute : int) -> MovementNode | None:
        """
        Returns the MovementNode to be used for the current time.
        A MovementNode is used until another MovementNode's time begins.
        If no MovementNode is present for the current time, returns the very last node.
        
        Note:
        If no active nodes are found, returns None.
        If two or more MoveSets have have priority_level, the first one with a valid node will be used.
        """
        
        if not self.usable_movesets:
            return None
        
        if not 0 <= hour < 24:
            raise ValueError(f"Invalid hour : \"{hour}\". Hour must be between 0 <= hour < 24")
        if not 0 <= minute < 60:
            raise ValueError(f"Invalid Minute : \"{minute}\". Minute must be between 0 <= minute < 60.")
        
        for movesets in self.usable_movesets.values():
            for moveset in movesets.values():
                movement_node = moveset.get_node_for(hour, minute)
                if movement_node:
                    return movement_node
    
    def add_moveset(self, moveset : MoveSet, replace_usable_moveset : bool = True, replace_duplicate_from_movesets : bool = False) -> None:
        """
        Adds the given MoveSet to the movesets.
        
        Use:
        replace_usable_moveset : 
        If moveset's moveset_id matches the moveset id of a previous moveset with the same priority level,
        the newest one will be used.
        
        replace_duplicate_from_movesets :
        If True, If a previous moveset with the moveset id matching that of the provided moveset is found, it will be replaced.
        Else, the new moveset will be added to the movesets list without removing the previous duplicate one (If present).
        """
        
        if replace_duplicate_from_movesets: # handles replace_duplicate_movesets
            for index, previous_moveset in enumerate(self.movesets):
                if previous_moveset.moveset_id == moveset.moveset_id:
                    if previous_moveset.priority_level == moveset.priority_level:
                        self.movesets.pop(index)
                        break
                    
        self.movesets.append(moveset)
        
        if not moveset.active:
            return
        
        if not moveset.priority_level in self.usable_movesets:
            self.usable_movesets[moveset.priority_level] = {}
        
        if not replace_usable_moveset: # handles replace_usable_moveset == False
            if moveset.moveset_id in self.usable_movesets[moveset.priority_level]:
                return
        
        self.usable_movesets[moveset.priority_level][moveset.moveset_id] = moveset
    
    def remove_usable_moveset(self, moveset_id : str) -> bool:
        """
        Removes moveset by the moveset_id provided from the usable_movesets.
        If moveset is successfully removed, returns True, Else returns False.
        """
        removed = False
        
        for usable_movesets_dict in self.usable_movesets.values():
            if moveset_id in usable_movesets_dict:
                usable_movesets_dict.pop(moveset_id)
                removed = True
                break
        
        return removed

    def remove_moveset(self, moveset_id : str, remove_all : bool = False) -> bool:
        """
        Removes moveset by the moveset_id provided from the movesets list.
        If moveset is successfully removed, returnes True, Else returns False.
        
        Usage:
        remove_all :
        If True, removes all movesets with the moveset_id provided, Else removes the first match.
        """
        
        to_remove = []
        for index, moveset in enumerate(self.movesets):
            if moveset.moveset_id == moveset_id:
                to_remove.append(index)
                if not remove_all:
                    break
        
        to_remove.sort(reverse = True) # Reversing to keep indexes stable while removing entries.
        for index in to_remove:
            self.movesets.pop(index)
        
        return len(to_remove) > 0
    
    def to_dict(self) -> dict:
        return {
            "movesets" : [moveset.to_dict() for moveset in self.movesets]
        }

class Loadout:
    """
    Container for holding Items or Stacks by the entity to be used.
    """
    
    __slots__ = ["slots"]
    
    def __init__(self, slots : dict[str, Item | Stack]):
        self.slots = slots
    
    def has_slot(self, slot : str) -> bool:
        """
        Returns True if slot is present, else returns False.
        """
        
        return slot in self.slots
    
    def is_free(self, slot : str) -> bool:
        """
        Returns True if slot is free, else returns False.
        """
        
        if not slot in self.slots:
            return False
        return self.slots[slot] is None
    
    def get_item(self, slot : str) -> Item | Stack | None:
        """
        Returns the item at the provided slot.
        Returns None if slot is not present.
        """
        
        if not slot in self.slots:
            return None
        return self.slots[slot]
    
    def is_equipped(self, item_id : str) -> bool:
        """
        Returns True if item_id is equipped in any slot, else returns False.
        """
        
        for slot in self.slots:
            item = self.slots[slot]
            if item is None:
                continue
            elif isinstance(item, Item):
                if item.identity.object_id == item_id:
                    return True
            elif isinstance(item, Stack):
                if item.item.identity.object_id == item_id:
                    return True
        return False
    
    def to_dict(self) -> dict:
        slots = {}
        for slot in self.slots:
            item = self.slots[slot]
            if item is None:
                slots[slot] = None
            elif isinstance(item, Item):
                slots[slot] = item.identity.object_id
            else:
                slots[slot] = item.item.identity.object_id
        return slots
    
class TradeManager:
    """
    
    """
    
    __slots__ = ["trade_inventory", "buying_multiplier", "selling_multiplier"]
    
    def __init__(self, trade_inventory : Inventory, buying_multiplier : float = 1.0, selling_multiplier : float = 1.0):
        self.trade_inventory = trade_inventory
        self.buying_multiplier = buying_multiplier
        self.selling_multiplier = selling_multiplier