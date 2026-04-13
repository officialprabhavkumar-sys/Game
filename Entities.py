"""
This module contains the Entity class used to represent all entities in the game.
"""

from Identity import Identity
from Tags import Tags
from EntityComponents import Loadout, Cultivation, MoveSetsManager
from Inventory import Inventory

class Entity:
    """
    Represents an entity with it's identity, cultivation and movesets.
    
    Attributes:
    1. identity : Identity : Identity of the entity.
    2. loadout : Loadout : Entity's loadout.
    3. inventory : Inventory : The entity's inventory. The whole inventory will be droppen upon the death of an npc.
    3. cultivation : Cultivation : Cultivation (power) of the entity.
    4. MoveSetsManager : Movement data of the entity through out the day.
    5. tags : Tags : Tags of the entity (Used for grouping and special events).
    """
    
    def __init__(self, identity : Identity, loadout : Loadout, inventory : Inventory, cultivation : Cultivation, movesets_manager : MoveSetsManager | None = None, tags : Tags | None = None, trading_inventory : Inventory | None = None):
        self.identity = identity
        self.loadout = loadout
        self.inventory = inventory
        self.cultivation = cultivation
        self.movesets_manager = movesets_manager or MoveSetsManager([])
        self.tags = tags or Tags([])
        self.trading_inventory = trading_inventory # can be None
    
    @property
    def is_alive(self) -> bool:
        """
        Returns True if entity's health is above 0.
        """
        
        return self.cultivation.is_alive
    
    def to_dict(self) -> dict:
        return {
            "identity" : self.identity.to_dict(),
            "loadout" : self.loadout.to_dict(),
            "inventory" : self.inventory.to_dict(),
            "cultivation" : self.cultivation.to_dict(),
            "movesets_manager" : self.movesets_manager.to_dict(),
            "tags" : self.tags.to_dict(),
            "trading_inventory" : self.trading_inventory.to_dict() if self.trading_inventory else None
        }