
"""
This module contains the ConditionalManager class, which is responsible for managing all conditionals in the game.
It stores conditionals and provides methods for adding, removing, and checking them for matches.
"""

from Conditionals import ConditionalResult, PureConditional, BasicConditional, AdvancedConditional
from ConditionInterpreter import ConditionInterpreter

from dataclasses import dataclass
from queue import Queue

@dataclass(slots=True)
class ConditionalBlock:
    """
    The data object that will be stored inside and used by the ConditionalManager.
    """
    
    pure_conditionals: list[PureConditional]
    check_until_match: bool = True
    get_first_match: bool = True #Only used for AdvancedConditionals, but set to True by default for BasicConditionals.
    
    def to_AdvancedConditional(self) -> AdvancedConditional:
        """
        Converts the ConditionalBlock to an AdvancedConditional.
        """
        
        return AdvancedConditional([{"conditions" : pure_conditional.conditions, "results" : pure_conditional.results} for pure_conditional in self.pure_conditionals], self.check_until_match, self.get_first_match)

    def to_dict(self) -> dict:
        return {
            "conditionals" : [pure_conditional.to_dict() for pure_conditional in self.pure_conditionals],
            "check_until_match" : self.check_until_match,
            "get_first_match" : self.get_first_match
        }
    
class ConditionalManager():
    """
    The ConditionalManager is responsible for managing all conditionals in the game.
    It stores conditionals and provides methods for adding, removing, and checking them for matches.
    """
    
    __slots__ = ["condition_interpreter", "command_queue", "conditionals", "_total_conditionals"]
    
    def __init__(self, command_queue : Queue, condition_interpreter : ConditionInterpreter):
        self.condition_interpreter = condition_interpreter
        self.command_queue = command_queue
        self.conditionals : dict[int, ConditionalBlock] = {}
        self._total_conditionals = 0
    
    def add_conditional(self, conditional : BasicConditional | AdvancedConditional) -> None:
        """
        Adds a conditional to the manager. The conditional can be either a BasicConditional or an AdvancedConditional.
        """
        pure_conditionals = conditional.to_pure_conditionals()
        check_until_match = conditional.check_until_match
        get_first_match = getattr(conditional, "get_first_match", True)
            
        self.conditionals[self._generate_id()] = ConditionalBlock(pure_conditionals, check_until_match, get_first_match)
    
    def remove_conditional(self, block_id : int) -> bool:
        """
        Removes a conditional from the manager by its block_id.
        Returns True if the conditional was successfully removed, False if the block_id was not found.
        """
        
        if block_id not in self.conditionals:
            return False
        del self.conditionals[block_id]
        return True
    
    def add_matched_to_queue(self, debug : bool = False) -> None:
        """
        Adds all matched results to command queue.
        """
        
        to_remove = []
        
        for block_id, block in list(self.conditionals.items()):
            match_found = False
            for pure_conditional in block.pure_conditionals:
                if all(self.condition_interpreter.interpret_condition(condition) for condition in pure_conditional.conditions):
                    for result in pure_conditional.results:
                        self.command_queue.put(result)
                    match_found = True
                    if block.get_first_match:
                        break
            if match_found or not block.check_until_match:
                to_remove.append(block_id)
        for block_id in to_remove:
            del self.conditionals[block_id]
        if debug:
            print(f"Conditions matched : {len(to_remove)}")
    
    def check_and_return_results(self, conditional : BasicConditional | AdvancedConditional) -> list[dict]:
        """
        Checks and returns the results of a conditional instead of putting it in command queue.
        """
        
        pure_conditionals = conditional.to_pure_conditionals()
        get_first_match = getattr(conditional, "get_first_match", True)
        results = []
        for pure_conditional in pure_conditionals:
            for condition in pure_conditional.conditions:
                if not self.condition_interpreter.interpret_condition(condition):
                    break
            else:
                results.extend(pure_conditional.results)
                if get_first_match:
                    break
        return results
    
    def _generate_id(self) -> int:
        """
        Returns the next available block_id for a new conditional.
        """
        
        self._total_conditionals += 1
        return self._total_conditionals
    
    def clear_conditionals(self) -> None:
        """
        Clears all conditionals from the manager.
        """
        
        self.conditionals.clear()
        self._total_conditionals = 0
    
    def __str__(self) -> str:
        string = "Control Blocks :\n"
        for generated_id, control_block in self.conditionals.items():
            string += f"{generated_id} : {control_block}\n"
        return string
    
    def to_dict(self) -> dict:
        conditionals = {"Basic" : [], "Advanced" : []}
        for conditional in self.conditionals.values():
            if len(conditional.pure_conditionals) == 1:
                conditionals_dict = conditional.to_dict()
                check_until_match = conditionals_dict["check_until_match"]
                conditional_dict = conditionals_dict["conditionals"][0]
                conditional_dict["check_until_match"] = check_until_match
                conditionals["Basic"].append(conditional_dict)
            else:
                conditionals["Advanced"].append(conditional.to_dict())
        return conditionals

def test_module():
    print("Testing Module ConditionalManager.py\n")
    condition_interpreter = ConditionInterpreter({})
    command_queue = Queue()
    conditional_manager = ConditionalManager(command_queue, condition_interpreter)
    conditional_result = ConditionalResult("function_1", {"arg1" : "value1", "arg2" : 2})
    basic_conditional = BasicConditional(["", ""], [conditional_result])
    advanced_conditional = AdvancedConditional([{"conditions" : ["", ""], "results" : [conditional_result, conditional_result]}])
    conditional_manager.add_conditional(basic_conditional)
    conditional_manager.add_conditional(advanced_conditional)
    print(conditional_manager)
    conditional_manager.add_matched_to_queue(True)
    print(conditional_manager)
    print(f"\nTest Complete.")

if __name__ == "__main__":
    test_module()