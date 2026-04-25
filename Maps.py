"""
This module contains the map and it's components.
"""

from Tags import Tags
from Inventory import Inventory
from Entities import Entity
from Conversation import Conversation
from Logger import LogEntry

import heapq
from typing import Any, TypeAlias

BasicDataType : TypeAlias = bool | int | float | str

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
        
        sublocation = location_id.split(":")[2].strip().lower()
        
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
    4. exits : dict[str, str] : Dictionary holding Sublocation's display name -> SubLocation's id for moving around.
    5. description : str : Description of the SubLocation.
    6. tags : Tags : Tags for the SubLocation.
    7. sublocation_options : Conversation : Conversation containing options related to sublocation.
    """
    
    SIZE_TAGS = {
        "__SMALL__" : 50,
        "__MEDIUM__" : 150,
        "__LARGE__" : 500,
        "__VERY LARGE__" : 2000,
        "__GIGANTIC__" : 10000,
        "__OPEN__" : 1000000 # I mean at this point, who cares how big a space is?
    }
    
    basic_data_types = (bool, int, float, str)
    
    __slots__ = ["name", "inventory", "entities", "exits", "description", "tags", "sublocation_options", "exit_ids", "other_data"]
    
    def __init__(self, name : str, inventory : Inventory, entities : dict[str, Entity], exits : dict[str, str], description : str, tags : Tags | None = None, sublocation_options : Conversation | None = None, other_data : dict[str, Any] | None = None):
        self.name = name
        self.inventory = inventory
        self.entities = entities
        self.exits = exits
        self.description = description
        self.tags = tags or Tags([])
        self.sublocation_options = sublocation_options
        self.other_data = other_data or {}
        self.exit_ids = set(self.exits.values())
    
    def add_entity(self, entity : Entity) -> None:
        """
        Adds the given entity to sublocation's entities.
        """
        
        self.entities[entity.identity.object_id] = entity
    
    def remove_entity(self, entity_id : str) -> bool:
        """
        Removes entity by entity_id.
        Returns True if entity is successfully removed, else Returns False.
        """
        
        return not self.entities.pop(entity_id, None) is None
    
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
    
    def get_and_remove_entity(self, entity_id : str) -> Entity | None:
        """
        Returns the entity by entity_id if present, else Returns None.
        """
        
        return self.entities.pop(entity_id, None)
    
    def recompute_exit_ids(self) -> None:
        """
        Recomputes exit_ids set used in pathfinding operations.
        """
        
        self.exit_ids = set(self.exits.values())
    
    def has_other_data(self, other_data_id : str) -> bool:
        """
        Returns True if any other_data_id is in other_data, else Returns False.
        """
        
        return other_data_id in self.other_data
    
    def verify_data_value_is_basic(self, data_value : Any) -> bool:
        """
        Verifies whether data_value is basic type or not.
        basic types include:
        bool, int, float, str, dictionary of string keys and values of before mentioned types or list or tuple consisting of the before mentioned types.
        
        Note:
        dictionaries, lists, tuples can be nested with other dictionaries, lists or tuples as long as the actual data is basic type.
        """
        
        if isinstance(data_value, self.basic_data_types):
            return True
        elif isinstance(data_value, dict):
            return all([all([isinstance(key, str) for key in data_value.keys()]), self.verify_data_value_is_basic(list(data_value.values()))])
        elif isinstance(data_value, (list, tuple)):
            return all([self.verify_data_value_is_basic(value) for value in data_value])
        else:
            return False
        
    def add_to_other_data(self, other_data_id : str, other_data_value : BasicDataType | dict[BasicDataType, BasicDataType] | list[BasicDataType] | tuple[BasicDataType], replace : bool = True) -> None:
        """
        Adds other_data_value to other_data by other_data_id.
        other_data_value MUST be a basic data type such as : bool, int, float, str or tuple or list or dictionary consisting of the following.
        If any other data is found in the value, data storing is aborted.
        """
        
        if other_data_id in self.other_data and not replace:
            return
        
        try:
            other_data_id = str(other_data_id)
        except:
            LogEntry("SUBLOCATION", 1, f"other_data_id could not be converted to string. Aborting data addition to other_data for sublocation by name \"{self.name}\"")
            return
        
        if not self.verify_data_value_is_basic(other_data_value):
            try:
                LogEntry("SUBLOCATION", 0, f"Could not add \"{other_data_value}\" to other_data for sublocation by name \"{self.name}\". Data is not basic type.")
            except:
                LogEntry("SUBLOCATION", 0, f"Could not add some data (Data could also not be converted to string) to other_data for sublocation by name \"{self.name}\". Data is not basic type.")
            return
        
        self.other_data[other_data_id] = other_data_value
    
    def get_other_data(self, other_data_id : str) -> Any:
        """
        Returns value if other_data_id is present in other_data else returns None.
        Use has_other_data to reliabily verify data presence.
        """
        
        return self.other_data.get(other_data_id, None)
    
    @property
    def size(self) -> int:
        """
        Size of the SubLocation.
        """
        
        for size_tag in self.SIZE_TAGS.keys():
            if size_tag in self.tags:
                return self.SIZE_TAGS[size_tag]
        return self.SIZE_TAGS["__SMALL__"]
    
    @property
    def is_open(self) -> bool:
        return not "__LOCKED__" in self.tags
    
    @property
    def is_locked(self) -> bool:
        return "__LOCKED__" in self.tags
    
    @property
    def has_options(self) -> bool:
        return not self.sublocation_options is None
    
    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "inventory" : self.inventory.to_dict(),
            "entities" : [entity.to_dict() for entity in self.entities.values()],
            "exits" : self.exits,
            "description" : self.description,
            "tags" : self.tags.to_dict()
        }

class PathFinder:
    """
    Utility for finding the optimal path between two sublocations.
    """
    
    __slots__ = ["map_loader", "cache", "map_version", "version_mapping"]
    
    def __init__(self, map_loader, cache : dict[tuple[str, str], tuple[int, list[str]] | None] | None = None, map_version : int | None = None, version_mapping : dict[tuple[str, str], int] | None = None):
        self.map_loader = map_loader
        self.cache = cache or {} # Only caches optimal size paths.
        self.map_version = map_version or 0
        self.version_mapping = version_mapping or {}
    
    def increase_map_version(self) -> None:
        """
        Increases map_version.
        """
        
        self.map_version += 1
        
        LogEntry("PATHFINDER", 0, f"Map version increased to : {self.map_version}.").push_to_queue()
    
    def _find_optimal_size_path(self, start : str, target : str) -> tuple[int, list[str]] | None:
        """
        Finds the optimal path for reaching the target from the start.
        Returns None if no path is found.
        
        Pathfinding algorithm : Dijkstra
        """

        visited = {}
        queue = []
        heapq.heappush(queue, (0, start, None))
        
        if self.map_loader.get_sublocation(start) is None or self.map_loader.get_sublocation(target) is None: # Initial sanity checks.
            return None
        
        while queue:
            cost, current_node, parent_node = heapq.heappop(queue)
            if current_node in visited:
                continue
            visited[current_node] = parent_node
            if current_node == target:
                path_taken = []
                while current_node is not None:
                    path_taken.append(current_node)
                    current_node = visited[current_node]
                return cost, path_taken[::-1]
            current_sublocation = self.map_loader.get_sublocation(current_node) # already checked that current_sublocation is not None when current_sublocation was exit_sublocation below when adding it to the queue.
            for exit_sublocation_id in current_sublocation.exits.values():
                if exit_sublocation_id in visited:
                    continue
                exit_sublocation = self.map_loader.get_sublocation(exit_sublocation_id)
                if exit_sublocation is None or exit_sublocation.is_locked:
                    continue
                heapq.heappush(queue, (cost + exit_sublocation.size, exit_sublocation_id, current_node))
        
        LogEntry("PATHFINDER", 0, f"No open path found between Sublocations \"{start}\" -> \"{target}\".").push_to_queue()
        
        return None
    
    def find_optimal_size_path(self, start : str, target : str) -> tuple[int, list[str]] | None:
        """
        Finds the optimal path for reaching the target from the start by size.
        Returns None if no path is found.
        
        Pathfinding algorithm : Dijkstra
        """
        
        entry = (start, target)
        if entry in self.cache:
            path = self.cache[entry]
            if self.version_mapping.get(entry, -1) == self.map_version:
                return path
            if path is None or not self.verify_path_full(path[1]):
                self.cache[entry] = (self._find_optimal_size_path(start, target))
        else:
            self.cache[entry] = self._find_optimal_size_path(start, target)
        self.version_mapping[entry] = self.map_version
        return self.cache[entry]
    
    def verify_path_connections(self, path : list[str]) -> bool:
        """
        Verifies path connections.
        Time Complexity : O(N)
        """
        
        path_length = len(path)
        if path_length == 1:
            return True
        for pointer in range(path_length - 1):
            current_node = self.map_loader.get_sublocation(path[pointer])
            if current_node is None:
                return False
            if not path[(pointer + 1)] in current_node.exit_ids:
                return False
        return True
    
    def verify_path_is_open(self, path : list[str]) -> bool:
        """
        Verifies all nodes of the given path are open.
        Time Complexity : O(N)
        """
        
        path_length = len(path)
        if path_length == 1:
            return True
        for pointer in range(1, path_length):
            next_node_id = path[pointer]
            next_node = self.map_loader.get_sublocation(next_node_id)
            if next_node is None:
                return False
            if next_node.is_locked: # O(1) operation
                return False
        return True
    
    def verify_path_full(self, path : list[str]) -> bool:
        """
        Verifies all nodes of the given path are connected and open.
        Time Complexity : O(N)
        """
        
        path_length = len(path)
        if path_length == 1:
            return True
        current_node_id = path[0]
        current_node = self.map_loader.get_sublocation(current_node_id)
        if current_node is None:
            return False
        for pointer in range(1, path_length):
            next_node_id = path[pointer]
            next_node = self.map_loader.get_sublocation(next_node_id)
            if next_node is None or next_node.is_locked:
                return False
            if not next_node_id in current_node.exit_ids:
                return False
            current_node = next_node
        return True
    
    def remove_invalid_path_caches(self) -> int:
        """
        Removes all invalid paths from cache (all paths that return None).
        Returns the number of invalid paths removed.
        """
        
        invalid_paths_removed = 0
        for parameters, path in list(self.cache.items()):
            if path is None or not self.verify_path_full(path[1]):
                self.cache.pop(parameters)
                self.version_mapping.pop(parameters)
                invalid_paths_removed += 1
                continue
            
        LogEntry("PATHFINDER", 0, f"\"{invalid_paths_removed}\" Invalid paths removed from cache.").push_to_queue()
        
        return invalid_paths_removed
    
    def reset_caches(self) -> None:
        """
        Resets pathfinder cache, version_mapping and map_version.
        """

        map_version_before_reset = self.map_version
        
        self.cache.clear()
        self.version_mapping.clear()
        self.map_version = 0
        
        LogEntry("PATHFINDER", 0, f"Caches Reset. Map Version before reset : \"{map_version_before_reset}\"").push_to_queue()
    
    def to_dict(self) -> dict:
        return {
            "cache" : self.cache,
            "version_mapping" : self.version_mapping,
            "map_version" : self.map_version
        }