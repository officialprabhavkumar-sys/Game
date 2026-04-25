"""
Contains all the components necessary for a conversation in the game.
"""

from Conditionals import BasicConditional, AdvancedConditional
from ConditionInterpreter import ConditionInterpreter
from Entities import Entity
from Logger import LogEntry

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Maps import SubLocation

class Dialogue:
    """
    Container for dialogue data.
    """
    
    __slots__ = ["dialogue_id", "display_text", "display_conditions", "conditional"]
    
    def __init__(self, dialogue_id : str, display_text : str, display_conditions : list[str], conditional : BasicConditional | AdvancedConditional):
        self.dialogue_id = dialogue_id
        self.display_text = display_text
        self.display_conditions = display_conditions
        self.conditional = conditional
    
    def can_display(self, condition_interpreter : ConditionInterpreter) -> bool:
        if not self.display_conditions:
            return True
        return all(condition_interpreter.interpret_condition(condition) for condition in self.display_conditions)

class Conversation:
    """
    Container for holding together dialogues.
    """
    
    __slots__ = ["entry_text", "dialogues", "can_exit"]
    
    CONDITION_INTERPRETER : ConditionInterpreter | None = None
    
    def __init__(self, entry_text : str, dialogues : dict[str, Dialogue], can_exit : bool = True):
        self.entry_text = entry_text
        self.dialogues = dialogues
        self.can_exit = can_exit
    
    def get_all_displayable(self) -> dict[str, Dialogue]:
        """
        Returns all displayable dialogues.
        Requires CONDITION_INTERPRETER to be set to a valid ConditionInterpreter.
        """
        
        if self.CONDITION_INTERPRETER is None:
            
            LogEntry("CONVERSATION", 2, f"CONDITION_INTERPRETER not set before calling get_all_displayable method.").push_to_queue()
            
            raise RuntimeError("CONDITION_INTERPRETER not set.")
        
        displayable = {}
        for dialogue_id, dialogue in self.dialogues.items():
            if not dialogue.can_display(self.CONDITION_INTERPRETER):
                continue
            displayable[dialogue_id] = dialogue
        return displayable

class ConversationContext:
    """
    Container for holding the data related to the conversation between the Player and the interaction_source.
    """
    
    __slots__ = ["interaction_source", "current_conversation", "current_conversation_displayable", "current_conversation_displayable_enum"]
    
    def __init__(self, interaction_source : Entity | SubLocation, current_conversation : Conversation):
        self.interaction_source = interaction_source
        self.current_conversation = current_conversation
        self.refresh_displayable_and_enum()
    
    def refresh_displayable_and_enum(self) -> None:
        """
        Refreshes current_conversation_displayable and current_conversation_displayable_enum.
        """
        
        self.current_conversation_displayable = self.current_conversation.get_all_displayable()
        self.current_conversation_displayable_enum = {i : display_id for i, display_id in enumerate(self.current_conversation_displayable)}
    
    @property
    def can_exit(self) -> bool:
        return self.current_conversation.can_exit