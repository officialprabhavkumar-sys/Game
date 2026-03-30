
"""
This module contains the Conditionals that are to be used by the ConditionalManager.
These are the objects that will be stored inside the ConditionalManager and used to check for conditions and return results.
A single condition is just a string that will handled by the ConditionInterpreter.
A single result object has the following attributes:
    command : str : function name as string,
    args : dict[str, Any] : dictionary of arguments to be passed to the function.
"""

from dataclasses import dataclass
from typing import Any, TypedDict

class ConditionResultPairDict(TypedDict):
    conditions: list[str]
    results: list[ConditionalResult]

@dataclass(slots = True, frozen = True)
class ConditionalResult():
    """
    A ConditionalResult is a data object that is meant to be used for storing the result of a conditional.
    """
    
    command : str
    args : dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "command" : self.command,
            "args" : self.args
        }

@dataclass(slots = True, frozen = True)
class PureConditional:
    """
    A pure data object that is meant to be used for storing condition-result pairs.
    It is meant to be used in the ConditionalManager for storing condition-result pairs individually for better organization.
    """
    
    conditions: list[str]
    results: list[ConditionalResult]
    
    def to_dict(self) -> dict:
        return {
            "conditions" : self.conditions,
            "results" : [result.to_dict() for result in self.results]
            }

class BasicConditional():
    """
    A basic conditional that can be used for simple condition-result pairs.
    It is meant to be used for simple tasks (e.g. Items.)
    If check_until_match is True, the conditions will be checked until a match is found,
    else they will be checked once and then flushed.
    """
    
    __slots__ = ["conditions", "results", "check_until_match"]
    
    def __init__(self, conditions : list[str], results : list[ConditionalResult], check_until_match : bool = True):
        self.conditions = conditions
        self.results = results
        self.check_until_match = check_until_match
    
    def to_pure_conditionals(self) -> list[PureConditional]:
        """
        Converts the BasicConditional to a list of PureConditionals.
        Since BasicConditionals only have one group of conditions and results,
        it will return a list with a single PureConditional.
        """
        
        return [PureConditional(self.conditions, self.results), ]
    
    def __str__(self) -> str:
        return f"conditions : {self.conditions}\nresults : {self.results}\n"
    
    def to_dict(self) -> dict:
        results = [{"command" : result.command, "args" : result.args} for result in self.results]
        return {
            "conditions" : self.conditions,
            "results" : results,
            "check_until_match" : self.check_until_match
        }

class AdvancedConditional:
    """
    An advanced conditional that can be used for more complex condition-result pairs.
    It is meant to be used for more complex tasks (e.g. Quests.)
    Conditions are grouped together in lists, and each list of conditions has a corresponding list of results.
    The conditions in a group are ANDed together, while the groups themselves are ORed together.
    If check_until_match is True, all groups will be checked until a match is found,
    else all of the groups will be checked once and then flushed.
    Once a match is found, 
    if get_first_match is True, the first matching group will be returned and the whole conditional will be flushed.
    If get_first_match is False, all groups will be checked and returned if they match before the conditional is flushed.
    
    Note:
    As soon as a match is found, the conditional will be flushed and removed from the ConditionalManager
    regardless of the value of get_first_match.
    The only difference is whether or not the rest of the groups will be checked and returned before the conditional is flushed.
    """
    
    __slots__ = ["conditions_results_pairs", "check_until_match", "get_first_match"]
    
    def __init__(self, conditions_results_pairs : list[ConditionResultPairDict], check_until_match : bool = True, get_first_match : bool = True):
        self.conditions_results_pairs = conditions_results_pairs
        self.check_until_match = check_until_match
        self.get_first_match = get_first_match #If True, the first matching condition will be returned and the whole conditional will be flushed. If False, rest of the conditions will also be checked and returned if they match before the conditional is flushed.
    
    def to_pure_conditionals(self) -> list[PureConditional]:
        """
        Converts the AdvancedConditional to a list of PureConditionals.
        """
        
        pure_conditionals = []
        for pair in self.conditions_results_pairs:
            pure_conditionals.append(PureConditional(pair["conditions"], pair["results"]))
        return pure_conditionals
        
    def __str__(self) -> str:
        string = "Conditional Result Pairs :\n"
        for conditional_result_pair in self.conditions_results_pairs:
            string += f"{conditional_result_pair}\n"
        string += f"check_until_match : {self.check_until_match}, get_first_match : {self.get_first_match}\n"
        return string
    
    def to_dict(self) -> dict:
        conditions_results_pairs = []
        for pair in self.conditions_results_pairs:
            results = []
            for result in pair["results"]:
                results.append({"command" : result.command, "args" : result.args})
            conditions_results_pairs.append({"conditions" : pair["conditions"], "results" : results})
        
        return {
            "conditions_results_pairs" : conditions_results_pairs,
            "check_until_match" : self.check_until_match,
            "get_first_match" : self.get_first_match
        }

def test_module():
    print("Testing Module Conditionals.py\n")
    conditional_result = ConditionalResult("function_1", {"key1" : "value1", "key2" : 2})
    basic_conditional = BasicConditional(["", ""], [conditional_result, ])
    advanced_conditional = AdvancedConditional([{"conditions" : ["", ""], "results" : [conditional_result, conditional_result]}])
    
    print("Basic Conditional : ", basic_conditional)
    print("Advanced Conditional : ", advanced_conditional)
    
    print("Converting to and loading from dictionary.")
    
    print("Basic Conditional : ", basic_conditional)
    print("Advanced Conditional : ", advanced_conditional)
    
    print(f"\nTest Complete.")

if __name__ == "__main__":
    test_module()