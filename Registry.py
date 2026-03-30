"""
This module contains the Registry class.
"""

class Registry:
    """
    Registry is used to keep track of and generate new ids for items, entities and any other category of objects alike.
    """
    
    __slots__ = ["category", "registry"]
    
    def __init__(self, category : str = "Unknown", registry : dict[str, int] | None = None):
        self.category = category
        self.registry = registry or {} # no verification of registry values.
    
    def generate_next_int_id_for(self, object_name : str) -> int:
        """
        Generates the next int id for the object specified and increases that object's count.
        """
        
        if not object_name in self.registry:
            self.registry[object_name] = 1
            return 1
        self.registry[object_name] += 1
        return self.registry[object_name]
    
    def get_count_of(self, object_name : str) -> int:
        """
        Gets the count of the object specified. If object is not found, returns 0.
        """
        
        if not object_name in self.registry:
            return 0
        return self.registry[object_name]
    
    def to_dict(self) -> dict:
        
        return {
            "category" : self.category,
            "registry" : self.registry
        }
    
    def __str__(self) -> str:
        string = f"Category : {self.category}\nRegistry :\n"
        if not self.registry:
            string += "No objects registered."
            return string
        n = 1
        for object_name, count in self.registry.items():
            string += f"{n}) {object_name} : {count}\n"
            n += 1
        return string

def test_module() -> None:
    print("Testing module \"Registry.py\"")
    registry = Registry("Items_Registry_1", {"a" : 1})
    print(registry)
    print(registry.get_count_of("a"))
    print(registry.get_count_of("b"))
    print(registry.generate_next_int_id_for("a"))
    print(registry.generate_next_int_id_for("b"))
    print(registry)
    print(registry.to_dict())
    print("Module test complete.")

if __name__ == "__main__":
    test_module()