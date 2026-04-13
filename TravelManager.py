"""
Contains the TravelManager which is responsible for managing the movement of NPCS and the player in the game.
"""

from Entities import Entity
from Maps import SubLocation

class Journey:
    """
    Container for holding information about an active journey.
    """
    
    __slots__ = ["journey_id", "travel_group", "path", "current_node", "progress", "is_active"]
    
    def __init__(self, journey_id : str, travel_group : dict[str, Entity], path : list[str], current_node : int = 0, progress : int = 0, is_active : bool = True):
        self.journey_id = journey_id
        self.travel_group = travel_group
        self.path = path # should be in correct order of connecting nodes.
        self.current_node = current_node
        self.progress = progress
        self.is_active = is_active

    @property
    def current_sublocation_id(self) -> str:
        return self.path[self.current_node]
    
    @property
    def next_sublocation_id(self) -> str | None:
        try:
            return self.path[self.current_node + 1]
        except IndexError:
            return None
    
    @property
    def is_finished(self) -> bool:
        return self.current_node == len(self.path) - 1
    
    def to_dict(self) -> dict:
        return {
            "journey_id" : self.journey_id,
            "travel_group" : list(self.travel_group.keys()),
            "path" : self.path,
            "current_node" : self.current_node,
            "progress" : self.progress,
            "is_active" : self.is_active
        }

class TravelManager:
    """
    Container and manager for all Journeys.
    """
    
    __slots__ = ["map_loader", "journeys", "npcs_in_journeys"]
    
    NODES_TRAVEL_TIMES_CACHE = {}
    
    def __init__(self, map_loader, journeys : dict[str, Journey] | None = None):
        self.map_loader = map_loader
        self.journeys = journeys or {}
        self.refresh_npcs_in_journeys()
    
    def refresh_npcs_in_journeys(self) -> None:
        """
        Refreshes npcs_in_journeys set.
        """
        
        npcs_in_journeys = set()
        
        for journey in self.journeys.values():
            for npc_id in journey.travel_group.keys():
                if npc_id in npcs_in_journeys:
                    raise RuntimeError(f"NPC \"{npc_id}\" can't be in two Journeys at once.")
                npcs_in_journeys.add(npc_id)
        self.npcs_in_journeys = npcs_in_journeys
    
    def remove_journey(self, journey_id : str) -> bool:
        """
        Removes journey by given journey_id.
        If journey was successfully removed returns True, else Returns False.
        """
        
        if not journey_id in self.journeys:
            return False
        for npc_id in self.journeys[journey_id].travel_group.keys():
            self.npcs_in_journeys.discard(npc_id)
        self.journeys.pop(journey_id)
        return True
    
    def add_journey(self, journey : Journey) -> None:
        if journey.journey_id in self.journeys:
            return
        for npc_id in journey.travel_group.keys():
            if npc_id in self.npcs_in_journeys:
                raise RuntimeError(f"NPC \"{npc_id}\" can't be in two Journeys at once.")
            self.npcs_in_journeys.add(npc_id)
        self.journeys[journey.journey_id] = journey
    
    def remove_npc_from_journey(self, journey_id : str, npc_id : str) -> bool:
        """
        Removes the specified npc from the specified journey.
        If npc was successfully removed returns True, else Returns False.
        """
        
        if not journey_id in self.journeys:
            return False
        journey_travel_group = self.journeys[journey_id].travel_group
        if not npc_id in journey_travel_group:
            return False
        self.npcs_in_journeys.discard(npc_id)
        journey_travel_group.pop(npc_id)
        if len(journey_travel_group) == 0:
            self.remove_journey(journey_id)
        return True
    
    def advance(self, amount : int = 1) -> None:
        """
        Advances Journeys by the given amount.
        Absolute amount is used.
        """
        
        amount = abs(amount)
        
        for journey_id, journey in list(self.journeys.items()):
            if journey.is_finished:
                self.remove_journey(journey_id)
                continue
            
            current_sublocation : SubLocation = self.map_loader.get_sublocation(journey.current_sublocation_id)
            if current_sublocation is None:
                self.remove_journey(journey_id)
                continue
            
            journey.progress += amount
            travel_cost = current_sublocation.size
            while journey.progress >= travel_cost:
                next_sublocation_id = journey.next_sublocation_id
                if next_sublocation_id is None:
                    self.remove_journey(journey_id)
                    break
                next_sublocation : SubLocation = self.map_loader.get_sublocation(next_sublocation_id)
                if next_sublocation is None:
                    self.remove_journey(journey_id)
                    break
                for entity_id in list(journey.travel_group.keys()):
                    entity = current_sublocation.get_entity(entity_id) # O(1)
                    if entity is None or not entity.is_alive:
                        self.remove_npc_from_journey(journey_id, entity_id)
                        continue
                    current_sublocation.remove_entity(entity_id)
                    next_sublocation.add_entity(entity)
                journey.current_node += 1
                journey.progress -= travel_cost
                travel_cost = next_sublocation.size
                current_sublocation = next_sublocation