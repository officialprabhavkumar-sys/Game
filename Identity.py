"""
This module contains the Identity component which is responsible for keeping all items and entities seperate and distinct.
"""
    
class Identity:
    """
    This component is necessary for all items and entities to stay distinct and easily referenceable.
    """
    
    __slots__ = ["name", "object_id", "description"]
    
    def __init__(self, name : str, object_id : str, description : str):
        self.name = name
        self.object_id = object_id # should be in form : ItemType_ItemName_ItemInstance and unique across all other object ids.
        self.description = description
    
    def to_dict(self) -> dict[str, str]:
        return {
            "name" : self.name,
            "object_id" : self.object_id,
            "description" : self.description,
        }
    
    @property
    def object_type(self) -> str:
        return self.object_id.split("_")[0]
    
    @property
    def root_object_id(self) -> str:
        root_object_id = self.object_id.split("_")
        return f"{root_object_id[0]}_{root_object_id[1]}"
    
    def __eq__(self, other : object) -> bool:
        if not isinstance(other, Identity):
            return NotImplemented
        return self.object_id == other.object_id
    
    def __str__(self) -> str:
        return f"name : {self.name}\nobject_id : {self.object_id}\ndescription : {self.description}\n"