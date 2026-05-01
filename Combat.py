"""
This module contains all the classes necessary for combat.
"""

from Entities import Entity

class EntityCombatState:
    """
    Object used in CombatManager for simulating combat.
    Contains and handles combat related attributes and methods.
    
    Attributes:
    1. entity : Entity : The base entity engaged in combat.
    2. target : Entity : The entity that is the current target of this entity.
    """
    
    __slots__ = ["entity", "target"]
    
    def __init__(self, entity : Entity, target : Entity | None = None):
        self.entity = entity
        self.target = target
    
    @property
    def entity_id(self) -> str:
        """
        Entity object id.
        """
        
        return self.entity.identity.object_id

class CombatGroup:
    """
    Container for holding the different EntityCombatStates belonging to a single group.
    Every group will battle every other group in a free for all.
    """
    pass

class CombatManager:
    """
    Main working object for simulating combat between multiple CombatGroups.
    """
    
    pass