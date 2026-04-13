
"""
This module contains all the various packets used to transfer data between different systems in the game.

Note:
The only packet not included in this module is the EffectPacket.
"""

from dataclasses import dataclass

class PhysicalDamagePacket:
    """
    The most basic DamagePacket component.
    
    Attributes:
    1. slice_damage : int
    2. pierce_damage : int
    3. crush_damage : int
    """
    
    __slots__ = ["slice_damage", "pierce_damage", "crush_damage"]
    
    def __init__(self, slice_damage : int = 0, pierce_damage : int = 0, crush_damage : int = 0):
        self.slice_damage = int(slice_damage)
        self.pierce_damage = int(pierce_damage)
        self.crush_damage = int(crush_damage)

    @property
    def is_empty(self) -> bool:
        if self.slice_damage or self.pierce_damage or self.crush_damage:
            return False
        return True
    
    def to_dict(self) -> dict:
        return {
            "slice_damage" : self.slice_damage,
            "pierce_damage" : self.pierce_damage,
            "crush_damage" : self.crush_damage
        }

@dataclass(slots = True) 
class ElementalDamagePacket:
    """
    Each ElementalDamagePacket must contain the following attributes:
    1. element : str : Defines the type of elemental data (e.g. Fire, Lightning, etc.).
    2. amount : int : The amount of damage of the specified type.
    
    Note:
    It is necessary for the element to be entered correctly
    for the target's resistances/protection against the specific element to be used.
    """
    
    element : str
    amount : int
    
    @property
    def is_empty(self) -> bool:
        """
        Returns True if amount == 0, else False
        """
        
        return self.amount == 0
    
    def to_dict(self) -> dict:
        return {
            "element" : self.element,
            "amount" : self.amount
        }

class DamagePacket:
    """
    All damaging actions must be applied through a DamagePacket before being applied to the target.
    
    Each DamagePacket can have the following attributes:
    1. physical_damage_packet : PhysicalDamagePacket : A PhysicalDamagePacket for any non-elemental damage.
    2. elemental_damage_packets : list[ElementalDamagePacket] : A list of ElementalDamagePacket(s) to be resolved.
    """
    
    __slots__ = ["physical_damage_packet", "elemental_damage_packets"]
    
    def __init__(self, physical_damage_packet : PhysicalDamagePacket | None = None, elemental_damage_packets : list[ElementalDamagePacket] | None = None):
        self.physical_damage_packet = physical_damage_packet or PhysicalDamagePacket()
        self.elemental_damage_packets = elemental_damage_packets or []
    
    @property
    def is_empty(self) -> bool:
        """
        Returns True if DamagePacket contains no damage across any type.
        """
        
        empty = self.physical_damage_packet.is_empty
        if empty:
            for elemental_damage_packet in self.elemental_damage_packets:
                if not elemental_damage_packet.is_empty:
                    empty = False
                    break
        return empty
    
    def to_dict(self) -> dict:
        return {
            "physical_damage_packet" : self.physical_damage_packet.to_dict(),
            "elemental_damage_packet" : [elemental_damage_packet.to_dict() for elemental_damage_packet in self.elemental_damage_packets]
        }