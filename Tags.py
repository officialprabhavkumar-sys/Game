"""
This module contains the Tag component for adding tags to any object in the game.
"""

class Tags:
    """
    This component is necessary for adding tags to any object in the game.
    All tags are stored in lower-case.
    """
    
    __slots__ = ["tags", ]
    
    def __init__(self, tags : list[str] | set[str]):
        self.tags = set([tag.lower() for tag in tags])
    
    def add_tag(self, tag : str) -> None:
        """
        Adds a tag to tags.
        """
        
        self.tags.add(tag.lower())
    
    def update(self, *tags : str) -> None:
        """
        adds all the new tags.
        """
        
        for tag in tags:
            self.tags.add(tag.lower())
    
    def has_any(self, *tags : str) -> bool:
        """
        Returns True if any tag from the given tags is present.
        Returns False if no tags are given.
        """
        
        for tag in tags:
            if tag in self.tags:
                return True
        return False
    
    def has_all(self, tags : list[str] | set[str]) -> bool:
        """
        Returns True only if all the tags in the given tags are present.
        Returns True if no tags are given.
        """
        
        for tag in tags:
            if not tag in self.tags:
                return False
        return True
    
    def remove_tag(self, tag : str) -> bool:
        """
        If tag is present it is removed and returns True else returns False.
        """
        
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def copy(self) -> Tags:
        """
        Returns a deep copy of tags.
        """
        
        return Tags({str(tag) for tag in self.tags})
    
    def __contains__(self, tag : str) -> bool:
        return tag in self.tags
    
    def __len__(self) -> int:
        return len(self.tags)
    
    def __iter__(self):
        return iter(self.tags)
    
    def to_dict(self) -> dict:
        return {"tags" : list(self.tags)}