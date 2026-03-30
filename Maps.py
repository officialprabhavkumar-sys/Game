"""
This module contains the map and it's components.
"""

from Tags import Tags
from Inventory import Inventory
from Entities import Entity

class Map:
    """
    Container and the top most object for holding locations.
    
    Attributes:
    1. name : str : Name of the Map.
    2. locations : dict[str, Locations] : Dictionary containing Location names as key and corresponding Locations as values.
    3. description : str : Description of the Map.
    4. tags : Tags : Tags for the Map.
    """
    
    __slots__ = ["name", "locations", "description", "tags"]
    
    def __init__(self, name : str, locations : dict[str, Location], description : str, tags : Tags | None = None):
        self.name = name
        self.locations = locations
        self.description = description
        self.tags = tags or Tags([])
        
    def has_location(self, location_id : str) -> bool:
        """
        Returns True if location is present in the map, else Returns False.
        
        location_id must be in the format:
        MapName:LocationName:SublocationName
        and each part must be seperated by a colon ":"
        
        Note :
            location_id letter cases do no matter as they are all converted to lower-case.
        """
        
        location = location_id.split(":")[1].strip().lower()
        
        return location in self.locations
    
    def has_sublocation(self, location_id : str) -> bool:
        """
        Returns True if sublocation is present in the map, else Returns False.
        
        location_id must be in the format:
        MapName:LocationName:SublocationName
        and each part must be seperated by a colon ":"
        
        Note :
            location_id letter cases do no matter as they are all converted to lower-case.
        """
        
        location = location_id.split(":")[1].strip().lower()
        
        if not location in self.locations:
            return False
        
        return self.locations[location].has_sublocation(location_id)
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "locations" : [location.to_dict() for location in self.locations.values()],
            "description" : self.description,
            "tags" : self.tags.to_dict()
        }

class Location:
    """
    Container for holding sublocations.
    
    Attributes:
    1. name : str : Name of the Location.
    2. sublocations : dict[str, SubLocations] : Dictionary containing SubLocation names as key and corresponding sublocations as values.
    3. description : str : Description of the Location.
    4. tags : Tags : Tags for the Location.
    """
    
    __slots__ = ["name", "sublocations", "description", "tags"]
    
    def __init__(self, name : str, sublocations : dict[str, SubLocation], description : str, tags : Tags | None):
        self.name = name
        self.sublocations = sublocations
        self.description = description
        self.tags = tags or Tags([])
    
    def has_sublocation(self, location_id : str) -> bool:
        """
        Returns True if sublocation is present in the map, else Returns False.
        
        location_id must be in the format:
        MapName:LocationName:SublocationName
        and each part must be seperated by a colon ":"
        
        Note :
        location_id letter cases do no matter as they are all converted to lower-case.
        """
        
        sublocation = location_id.split(":")[2].strip()
        
        return sublocation in self.sublocations
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "sublocations" : [sublocation.to_dict() for sublocation in self.sublocations.values()],
            "description" : self.description,
            "tags" : self.tags.to_dict()
        }
    
class SubLocation:
    """
    The working layer of the game maps. Everything happens in SubLocations.
    
    Attributes:
    1. name : str : Name of the SubLocation.
    2. inventory : Inventory : SubLocation's inventory.
    3. entities : dict[str, Entity] : dictionary containing entity ids as keys and corresponding entities as values.
    4. description : str : Description of the SubLocation.
    5. tags : Tags : Tags for the SubLocation.
    """
    
    __slots__ = ["name", "inventory", "entities", "description", "tags"]
    
    def __init__(self, name : str, inventory : Inventory, entities : dict[str, Entity], description : str, tags : Tags | None = None):
        self.name = name
        self.inventory = inventory
        self.entities = entities
        self.description = description
        self.tags = tags or Tags([])
    
    def has_entity(self, entity_id : str) -> bool:
        """
        Returns True if entity by the entity_id is in the sublocation, else Returns False.
        """
        
        return entity_id in self.entities
    
    def get_entity(self, entity_id : str) -> Entity | None:
        """
        Returns the entity if entity by entity_id is present, else Returns None.
        """
        
        if not entity_id in self.entities:
            return None
        return self.entities[entity_id]
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "inventory" : self.inventory.to_dict(),
            "entities" : [entity.to_dict() for entity in self.entities.values()],
            "description" : self.description,
            "tags" : self.tags.to_dict()
        }