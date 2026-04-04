"""
This module contains components that are used to apply effects to entities in the game.
"""

from Conditionals import BasicConditional, AdvancedConditional

from dataclasses import dataclass
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from Combat import EntityCombatState

@dataclass(slots = True) 
class EffectPacket:
    """
    All effects must be applied through an EffectPacket to the target.
    """
    
    effect_id : str
    duration : int
    magnitude : float
    source_entity : EntityCombatState | str # can be the entity_id of the source entity if out of combat, else should be EntityCombatState of the source entity.

class EffectBaseReference:
    """
    Container for holding the data of an effect.
    
    Attributes:
    1. effect_id : str : Id of the effect.
    2. effect_conditional : BasicConditional | AdvancedConditional : The actual effect that is applied to the entity.
    3. override_method : Literal["replace", "magnitude_add", "duration_add"] : Method for overriding existing effects.
    4. name : str : Display name of the effect.
    5. description : str : Description of the effect.
    """
    
    __slots__ = ["effect_id", "effect_conditional", "override_method", "name", "description"]
    
    def __init__(self, effect_id : str, effect_conditional : BasicConditional | AdvancedConditional, override_method : Literal["replace", "magnitude_add", "duration_add"], name : str, description : str):
        self.effect_id = effect_id
        self.effect_conditional = effect_conditional
        self.override_method = override_method
        self.name = name
        self.description = description
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "effect_id" : self.effect_id,
            "effect_conditional" : self.effect_conditional.to_dict(),
            "override_method" : self.override_method,
            "name" : self.name,
            "description" : self.description
        }

class Effect:
    """
    Container for holding the data of an effect applied to an entity.
    """
    
    __slots__ = ["effect_reference", "duration", "magnitude", "source_entity"]
    
    def __init__(self, effect_reference : EffectBaseReference, duration : int, magnitude : float, source_entity : EntityCombatState | str):
        self.effect_reference = effect_reference
        self.duration = duration
        self.magnitude = magnitude
        self.source_entity = source_entity
    
    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "effect_reference" : self.effect_reference.effect_id,
            "duration" : self.duration,
            "magnitude" : self.magnitude,
            "source_entity" : self.source_entity.entity_id if isinstance(self.source_entity, EntityCombatState) else self.source_entity
        }

class EffectRegistry:
    """
    Container for holding all the effectBaseReferences in the game.
    """
    
    __slots__ = ["effect_references", ]
    
    def __init__(self, effect_references : dict[str, EffectBaseReference]):
        self.effect_references = effect_references
    
    def get_effect_reference(self, effect_id : str) -> EffectBaseReference | None:
        """
        Returns the EffectBaseReference with the given effect_id if present, else Returns None.
        """
        
        if not effect_id in self.effect_references:
            return None
        return self.effect_references[effect_id]
    
    def __getattr__(self, effect_id : str) -> EffectBaseReference | None:
        return self.get_effect_reference(effect_id)
    
    def __contains__(self, effect_id : str) -> bool:
        return effect_id in self.effect_references
    
    def __len__(self) -> int:
        return len(self.effect_references)
    
    def __iter__(self):
        return iter(self.effect_references.values())
    
    def to_dict(self) -> dict[str, list[dict]]:
        return {"effect_references" : [effect_reference.to_dict() for effect_reference in self.effect_references.values()]}
        