
"""
This module contains all the components that make up any item and it's behaviours in the game.
"""

from Conditionals import BasicConditional, AdvancedConditional
from ConditionInterpreter import ConditionInterpreter
from Packets import PhysicalDamagePacket, ElementalDamagePacket, DamagePacket

from typing import Literal
from copy import deepcopy

class Usable:
    """
    Component necessary for player to use any item.
    Stores a BasicConditional or AdvancedConditional depending on tag provided, and hence has access to all of it's methods.
    Two additional optional arguments provided:
    1. conditional_type : Literal["basic", "advanced"] : Defines whether the conditional to be created is basic or advanced.
    2. conditional_args : dict : Contains all the arguments, ready to be passed to the specified conditional constructor.
    3. single_use : bool : Defines whether the item is single use or not.
    4. remove_upon_failure : bool : Ties directly to single_use. If single_use is False, this is ignored.
    Else, even upon the failure of the item to execute due to conditions not being satisfied,
    the item is to be removed from inventory.
    """
    
    __slots__ = ["durability", "conditional", "conditional_type", "single_use", "remove_upon_failure"]
    
    def __init__(self, conditional : BasicConditional | AdvancedConditional, conditional_type : Literal["basic", "advanced"], single_use : bool = True, remove_upon_failure : bool = False):
        self.conditional = conditional
        self.conditional_type = conditional_type
        self.single_use = single_use
        self.remove_upon_failure = remove_upon_failure #Ignored if single_use is False.
    
    def to_dict(self) -> dict:
        
        return {
            "conditional" : self.conditional.to_dict(),
            "conditional_type" : self.conditional_type,
            "single_use" : self.single_use,
            "remove_upon_failure" : self.remove_upon_failure
            }
    
    def __str__(self) -> str:
        return f"Conditional : {self.conditional}\nConditional Type : {self.conditional_type}\nsingle_use : {self.single_use}, remove_upon_failure : {self.remove_upon_failure}\n"
    
    def copy(self) -> Usable:
        """
        Returns a shallow-deep copy of the object.
        """
        
        return deepcopy(self)
    
class Durability:
    """
    Component necessary for any type of durability based item. 
    """
    
    __slots__ = ["max_durability", "current_durability"]
    
    def __init__(self, max_durability : int, current_durability : int | None):
        self.max_durability = max_durability
        self.current_durability = current_durability or max_durability
    
    def lower_durability(self, amount : int = 1):
        """
        Lowers the durability by amount specified. Default amount lowered is 1.
        Amount must be an int or be convertable to an int.
        Durability will never drop below zero when using this method.
        """
        
        amount = int(amount)
        self.current_durability = max(0, self.current_durability - amount)
    
    def increase_durability(self, amount : int = 1) -> None:
        """
        Increases the durability by the amount sepcified. Default amount increased is 1.
        Amount must be an int or be convertable to an int.
        Durability will never increase beyond max_durability when using this method.
        """
        
        amount = int(amount)
        self.current_durability = min(self.max_durability, self.current_durability + amount)
    
    def consume(self, amount : int) -> bool:
        """
        Lowers durability and returns True if item is broken, else returns False.
        """
        
        self.lower_durability(amount)
        return self.is_broken
    
    def repair_completely(self) -> None:
        """
        sets current_durability to max_durability.
        """
        
        self.current_durability = self.max_durability
    
    @property
    def durability_ratio(self) -> float:
        """
        current_durability / max_durability.
        """
                
        return self.current_durability / self.max_durability
    
    @property
    def is_broken(self) -> bool:
        """
        Returns True if current_durability == 0, else False
        """
        
        return self.current_durability == 0
    
    @property
    def is_full(self) -> bool:
        """
        Returns True if current_durability == max_durability, else False
        """
        
        return self.current_durability == self.max_durability
    
    @property
    def durability_percent(self) -> int:
        """
        Returns durability percentage as int.
        """
        
        return int(self.durability_ratio * 100)
    
    def to_dict(self) -> dict:
        return {
            "max_durability" : self.max_durability,
            "current_durability" : self.current_durability
            }

    def __str__(self) -> str:
        return f"Max Durability : {self.max_durability}\nCurrent Durability : {self.current_durability}\n"
    
class ElementalProtection:
    """
    Component necessary for an armor to have protection attributes against an element.
    Each and every element that the armor must protect against must have one and only one ElementalProtection object for it.
    ElementalProtection takes the following arguments:
    1. element : str : Element the protection is for.
    2. conditions : list[str] : List of strings containing conditions for the DamageProtection to apply.
    3. magnitude : int : Raw amount deducted from the element damage.
    4. max_magnitude : int : Maximum amount that can be deducted by the armor piece from the element damage.
    5. percentage : float : Percentage amount deducted from element damage.
    
    Working:
    If percentage is not None/0 it will be applied to the elemental damage first.
    Then if the damage from the element is not 0, the magnitude will be applied (if present).
    If max_magnitude is not None/0 then the total damage reduced will never exceed max_magnitude.
    If max_magnitude is 0, max_magnitude is disabled.
    """
    
    __slots__ = ["element", "conditions", "magnitude", "max_magnitude", "percentage"]
    
    def __init__(self, element : str, conditions : list[str] | None = None, magnitude : int = 0, max_magnitude : int = 0, percentage : float = 0):
        self.element = element
        self.conditions = conditions or []
        self.magnitude = magnitude
        self.max_magnitude = max_magnitude
        self.percentage = percentage
    
    def merge(self, other : ElementalProtection, merge_effectiveness : float = 1.0, merge_other_conditions : bool = True, override_with_other_max_magnitude : bool = False) -> bool:
        """
        Merges the other ElementalProtection with the current if elements are same.
        If merge is successful, returns True, Else returns False.
        
        Usage:
        merge_effectiveness_mult:
            add's other ElementalProtection's protections to current with provided efficiency.
            eg. current protection += other's protections * merge_effectiveness_mult
            
        merge_other_conditions:
            Merges the conditions from the other ElementalProtection with the current one.
            
        override_with_other_max_magnitude:
            sets current ElementalProtection's max_magnitude to the other ElementalProtection's max_magnitude.
        """
        
        if self.element != other.element:
            return False
        
        self.magnitude += other.magnitude * merge_effectiveness
        self.percentage += other.magnitude * merge_effectiveness
        
        if merge_other_conditions:
            self.conditions.extend(other.conditions)
        
        if override_with_other_max_magnitude:
            self.max_magnitude = other.max_magnitude
    
    def __str__(self) -> str:
        return f"Element : {self.element}\n Conditions : {self.conditions}\nFlat Reduction : {self.magnitude}\nMax Reduction : {self.max_magnitude or "Infinite"}\nPercentage Reduction : {self.percentage}\n"
    
    def to_dict(self) -> dict:
        return {
            "element" : self.element,
            "conditions" : self.conditions,
            "magnitude" : self.magnitude,
            "max_magnitude" : self.max_magnitude,
            "percentage" : self.percentage
            }
    
class Armor:
    """
    Component necessary for an item to act as an armor piece.
    Takes the following attributes:
    1. max_durability : int : Maximum durability of the armor piece.
    2. current_durability : int : The current duability of the armor piece.
    3. slice_protection : int : Protection against slice damage.
    4. crush_protection : int : Protection against crush damage.
    5. elemental_protections : list[ElementalProtection] : list of ElementalProtection objects for specific elements.
    
    Important method:
    take_damage(damage : DamagePacket, interpreter : ConditionInterpreter)
    Takes DamagePacket and a ConditionInterpreter, returns a modified DamagePacket and modifies the armor itself appropriately.
    
    Note:
    If there are two or more packets for elemental_protection of the same element, the last packet is used.
    """
    
    __slots__ = ["durability", "conditions", "slice_protection", "pierce_protection", "crush_protection", "elemental_protections"]
    
    basic_protections = {"slice_protection", "pierce_protection", "crush_protection"}
    basic_damages_to_protections = {"slice_damage" : "slice_protection", "pierce_damage" : "pierce_protection", "crush_damage" : "crush_protection"}
    
    def __init__(self, max_durability : int, current_durability : int | None = None, conditions : list[str] | None = None, slice_protection : int = 0, pierce_protection : int = 0, crush_protection : int = 0, elemental_protections : list[ElementalProtection] | None = None):
        self.durability = Durability(max_durability, current_durability)
        self.conditions = conditions or []
        self.slice_protection = slice_protection
        self.pierce_protection = pierce_protection
        self.crush_protection = crush_protection
        self.elemental_protections = {elemental_protection.element : elemental_protection for elemental_protection in elemental_protections} if elemental_protections else {}
    
    def _get_effective_physical_protection(self, protection : str) -> int:
        """
        Returns the effective protection of the armor for the specified physical protection.
        """
        
        if protection not in self.basic_protections:
            raise KeyError(f"\"{protection}\" is not a valid basic_protection.")
        
        effective_protection = getattr(self, protection) * self.durability.durability_ratio
        
        return int(effective_protection)
    
    def _get_effective_elemental_protection(self, protection : str, amount : int) -> int:
        """
        Returns the effective protection of the armor for the specified element.
        """
        
        if not protection in self.elemental_protections:
            return 0
        
        durability_ratio = self.durability.durability_ratio
        
        elemental_protection = self.elemental_protections[protection] # gets the ElementalProtection
        percentage_protection = elemental_protection.percentage * amount # damage protection by percentage attribute.
        total_protection = percentage_protection + elemental_protection.magnitude # adds raw damage protection with the percentage protection
        
        if elemental_protection.max_magnitude:
            max_protection = elemental_protection.max_magnitude * durability_ratio # maximum protection offered by armor at current durability
        else:
            max_protection = float('inf') # max_protection disabled.
            
        effective_protection = total_protection * durability_ratio # corrected damage provided by armor at current durability
        effective_protection = min(max_protection, effective_protection) # checking damage protection doesn't surpass limit.
        
        return int(effective_protection)
    
    def _take_physical_damage(self, damage : PhysicalDamagePacket) -> PhysicalDamagePacket:
        """
        Calculates and modifies PhysicalDamagePacket and armor's durability by the appropriate amount.
        """
        
        for damage_type, protection_type in self.basic_damages_to_protections.items(): # cycles through all basic_damages.
            damage_amount = getattr(damage, damage_type) # gets damage amount from PhysicalDamagePacket
            if damage_amount == 0: # if damage is 0 then there's no point in doing unnecessary work.
                continue
            protection_amount = self._get_effective_physical_protection(protection_type) # gets effective protection.
            damage_left = max(0, damage_amount - protection_amount) # calculates damage left. damage left cannot be less than 0.
            protection_provided = damage_amount - damage_left # calculates protection provided.
            self.durability.lower_durability(protection_provided) # lowers durability of armor based on protection provided.
            setattr(damage, damage_type, damage_left) # corrects PhysicalDamagePacket's damage type to the lowered amount.
        return damage
    
    def _take_elemental_damage(self, damage : ElementalDamagePacket, interpreter : ConditionInterpreter) -> ElementalDamagePacket:
        """
        Calculates and modifies ElementalDamagePacket and armor's durability by the appropriate amount.
        """
        if damage.element in self.elemental_protections:
            protection = self.elemental_protections[damage.element]
            for condition in protection.conditions: # checking all the conditions and making sure all of them are fulfilled.
                if not interpreter.interpret_condition(condition):
                    return damage
        protection_amount = self._get_effective_elemental_protection(damage.element, damage.amount) # gets effective protection.
        damage_left = max(0, damage.amount - protection_amount) # calculates damage left. damage left cannot be less than 0.
        protection_provided = damage.amount - damage_left # calculates protection provided.
        self.durability.lower_durability(protection_provided) # lowers durability of armor based on protection provided.
        setattr(damage, "amount", damage_left) # corrects PhysicalDamagePacket's damage type to the lowered amount.
        return damage
    
    def take_damage(self, damage : DamagePacket, interpreter : ConditionInterpreter) -> DamagePacket:
        """
        Takes and modifies DamagePacket and armor attributes.
        """
        
        if self.durability.is_broken:
            return damage
        self._take_physical_damage(damage.physical_damage_packet) # resolving PhysicalDamagePacket.
        
        #resolving all ElementalDamagePacket(s).
        for element_damage_packet in damage.elemental_damage_packets:
            if self.durability.is_broken:
                return damage
            self._take_elemental_damage(element_damage_packet, interpreter)
        return damage
    
    def __str__(self) -> str:
        string = f"Durability : {self.durability}\nSlice Protection : {self.slice_protection}\nPierce Protection : {self.pierce_protection}\nCrush Protection : {self.crush_protection}\nElemental Protections :\n"
        for elemental_protection in self.elemental_protections.values():
            string += f"{elemental_protection}\n"
        if not self.elemental_protections:
            string += "None\n"
        return string
    
    def to_dict(self) -> dict:
        return {
            "durability" : self.durability.to_dict(),
            "slice_protection" : self.slice_protection,
            "pierce_protection" : self.pierce_protection,
            "crush_protection" : self.crush_protection,
            "elemental_protections" : [elemental_protection.to_dict() for elemental_protection in self.elemental_protections.values()]
            }
        
class Ammo:
    """
    Component necessary for an item to act as ammo.
    """
    
    __slots__ = ["ammo_type", "use_cost", "slice_damage", "pierce_damage", "crush_damage", "accuracy", "elemental_damages"]
    
    def __init__(self, ammo_type : str, use_cost : dict[Literal["qi", "soul_qi", "health", "essence"], int] = None, slice_damage : int = 0, pierce_damage : int = 0, crush_damage : int = 0, accuracy : float = 1.0, elemental_damages : dict[str, int] | None = None):
        self.ammo_type = ammo_type
        self.use_cost = use_cost or {} # cost of using the ammo such as qi, soul_qi, health or essence mapping to an int.
        self.slice_damage = slice_damage
        self.pierce_damage = pierce_damage
        self.crush_damage = crush_damage
        self.accuracy = accuracy # must be a float less than or equals to 1. It will be used as a multiplier for accuracy of the ranged weapon.
        self.elemental_damages = elemental_damages or {} # mapping of element : amount.
    
    def generate_damage_packet(self) -> DamagePacket:
        """
        Returns a new DamagePacket based on the ammo's attributes.
        """
        
        physical_damage_packet = PhysicalDamagePacket(slice_damage = self.slice_damage, pierce_damage = self.pierce_damage, crush_damage = self.crush_damage)
        elemental_damage_packets = [ElementalDamagePacket(element = element, amount = amount) for element, amount in self.elemental_damages.items()]
        damage_packet = DamagePacket(physical_damage_packet = physical_damage_packet, elemental_damage_packets = elemental_damage_packets)
        return damage_packet

    def __str__(self) -> str:
        string = f"Ammo Type : {self.ammo_type}\nUse Cost : {self.use_cost}\nSlice Damage : {self.slice_damage}\nPierce Damage : {self.pierce_damage}\nCrush Damage : {self.crush_damage}\nAccuracy : {self.accuracy}\nElemental Damages :\n"

        for element, damage in self.elemental_damages.items():
            string += f"{element} : {damage}\n"
            
        if not self.elemental_damages:
            string += "None\n"
            
        return string
    
    def to_dict(self) -> dict:
        return {
            "ammo_type" : self.ammo_type,
            "use_cost" : self.use_cost,
            "slice_damage" : self.slice_damage,
            "pierce_damage" : self.pierce_damage,
            "crush_damage" : self.crush_damage,
            "accuracy" : self.accuracy,
            "elemental_damage" : self.elemental_damages
        }
        
class MeleeWeapon:
    """
    Main component of a melee weapon.
    """
    
    __slots__ = ["durability", "use_cost", "slice_damage", "pierce_damage", "crush_damage", "elemental_damages"]
    
    def __init__(self, max_durability : int, current_durability : int, use_cost : dict[Literal["qi", "soul_qi", "health", "essence"], int] | None = None, slice_damage : int = 0, pierce_damage : int = 0, crush_damage : int = 0, elemental_damages : dict[str, int] | None = None):
        self.durability = Durability(max_durability, current_durability)
        self.use_cost = use_cost or {} # cost of using the weapon such as qi, soul_qi, health or essence mapping to an int.
        self.slice_damage = slice_damage
        self.pierce_damage = pierce_damage
        self.crush_damage = crush_damage
        self.elemental_damages = elemental_damages or {}
    
    def generate_damage_packet(self) -> DamagePacket:
        """
        Returns a new DamagePacket based on the weapon's attributes.
        """
        
        durability_ratio = self.durability.durability_ratio
        physical_damage_packet = PhysicalDamagePacket(slice_damage = self.slice_damage * durability_ratio, pierce_damage = self.pierce_damage * durability_ratio, crush_damage = self.crush_damage * durability_ratio)
        elemental_damage_packets = [ElementalDamagePacket(element = element, amount = amount * durability_ratio) for element, amount in self.elemental_damages.items()]
        damage_packet = DamagePacket(physical_damage_packet = physical_damage_packet, elemental_damage_packets = elemental_damage_packets)
        return damage_packet
    
    def __str__(self) -> str:
        string = f"Durability : {self.durability}\nUse Cost : {self.use_cost}\nSlice Damage : {self.slice_damage}\nPierce Damage : {self.pierce_damage}\nCrush Damage : {self.crush_damage}\nElemental Damages :\n"

        for element, damage in self.elemental_damages.items():
            string += f"{element} : {damage}\n"
        
        if not self.elemental_damages:
            string += "None\n"
        
        return string
    
    def to_dict(self) -> dict:
        
        return {
            "durability" : self.durability.to_dict(),
            "use_cost" : self.use_cost,
            "slice_damage" : self.slice_damage,
            "pierce_damage" : self.pierce_damage,
            "crush_damage" : self.crush_damage,
            "elemental_damages" : self.elemental_damages
        }
        
class RangedWeapon:
    """
    Main component of a ranged weapon.
    """
    
    __slots__ = ["durability", "use_cost", "slice_damage_mult", "pierce_damage_mult", "crush_damage_mult", "elemental_damages_mult"]
    
    basic_damage_types_to_mult = {
        "slice_damage" : "slice_damage_mult",
        "pierce_damage" : "pierce_damage_mult",
        "crush_damage" : "crush_damage_mult"
    }
    
    def __init__(self, max_durability : int, current_durability : int, use_cost : dict[Literal["qi", "soul_qi", "health", "essence"], int] | None= None, slice_damage_mult : float = 1.0, pierce_damage_mult : float = 1.0, crush_damage_mult : float = 0, elemental_damages_mult : dict[str, float] | None = None):
        self.durability = Durability(max_durability, current_durability)
        self.use_cost = use_cost or {} # cost of using the weapon such as qi, soul_qi, health or essence mapping to an int.
        self.slice_damage_mult = slice_damage_mult
        self.pierce_damage_mult = pierce_damage_mult
        self.crush_damage_mult = crush_damage_mult
        self.elemental_damages_mult = elemental_damages_mult or {}
    
    def generate_damage_packet(self, ammo : Ammo) -> DamagePacket:
        damage_packet = ammo.generate_damage_packet() # gets base DamagePacket generated by the ammo
        
        durability_ratio = self.durability.durability_ratio
        
        for basic_damage_type in damage_packet.physical_damage_packet.__slots__: # applies physical damage type modifications.
            amount = getattr(damage_packet.physical_damage_packet, basic_damage_type)
            new_damage_amount = amount * getattr(self, self.basic_damage_types_to_mult[basic_damage_type]) * durability_ratio
            setattr(damage_packet.physical_damage_packet, basic_damage_type, new_damage_amount)
        
        for elemental_damage_packet in damage_packet.elemental_damage_packets: # modifies ElementalDamagePacket(s) if specified element is in elemental_damages_mult.
            if elemental_damage_packet.element in self.elemental_damages_mult:
                elemental_damage_packet.amount = elemental_damage_packet.amount * self.elemental_damages_mult[elemental_damage_packet.element] * durability_ratio
        
        return damage_packet
    
    def __str__(self) -> str:
        string = f"Durability : {self.durability}\nUse Cost : {self.use_cost}\nSlice Damage Multiplier : {self.slice_damage_mult}\nPierce Damage Multiplier : {self.pierce_damage_mult}\nCrush Damage Multiplier : {self.crush_damage_mult}\nElemental Damage Multipliers :\n"

        for element, damage_mult in self.elemental_damages_mult.items():
            string += f"{element} : x{damage_mult}\n"
        
        if not self.elemental_damages_mult:
            string += "None\n"
        
        return string
    
    def to_dict(self) -> dict:
        return {
            "durability" : self.durability.to_dict(),
            "use_cost" : self.use_cost,
            "slice_damage_mult" : self.slice_damage_mult,
            "pierce_damage_mult" : self.pierce_damage_mult,
            "crush_damage_mult" : self.crush_damage_mult,
            "elemental_damages_mult" : self.elemental_damages_mult
        }

class Equippable:
    """
    Component necessary for an item to be equipped.
    The item can have certains conditions that need to be fulfilled in order for them to be equipped.
    Equippable item can be an instance of:
    1. Armor.
    2. MeleeWeapon.
    3. RangedWeapon.
    4. Ammo.
    """
    
    __slots__ = ["equip_slot", "conditions", "item"]
    
    def __init__(self, equip_slot : str, item : Armor | MeleeWeapon | RangedWeapon | Ammo, conditions : list[str] | None = None):
        self.equip_slot = equip_slot
        self.conditions = conditions or []
        self.item = item
    
    @property
    def is_armor(self) -> bool:
        """
        Returns True if item is an instance of Armor class.
        """
        
        return isinstance(self.item, Armor)
    
    @property
    def is_weapon(self) -> bool:
        """
        Returns True if item is an instance of MeleeWeapon or RangedWeapon.
        """
        
        return isinstance(self.item, (MeleeWeapon, RangedWeapon))
    
    def is_melee_weapon(self) -> bool:
        """
        Returns True if item is an instance of MeleeWeapon.
        """
        
        return isinstance(self.item, MeleeWeapon)
    
    def is_ranged_weapon(self) -> bool:
        """
        Returns True if item is an instance of RangedWeapon.
        """
        
        return isinstance(self.item, RangedWeapon)
    
    @property
    def is_ammo(self) -> bool:
        """
        Returns True if item is an instance of Ammo class.
        """
        
        return isinstance(self.item, Ammo)
    
    def has_valid_equip_slot(self, all_equip_slots : list[str]) -> bool:
        """
        Returns True if the item's equip_slot is in all_equip_slots.
        """
        
        return self.equip_slot in all_equip_slots
    
    def can_be_equipped(self, condition_interpreter : ConditionInterpreter) -> bool:
        """
        Returns True if all conditions necessary for equipping the item are True.
        """
        
        for condition in self.conditions:
            if not condition_interpreter.interpret_condition(condition):
                return False
        return True
    
    def __str__(self) -> str:
        return f"Equip Slot : {self.equip_slot}\nConditions : {self.conditions}\nItem : {self.item}\n"
    
    def to_dict(self) -> dict:
        return {
            "equip_slot" : self.equip_slot,
            "conditions" : self.conditions,
            "item" : self.item.to_dict()
        }