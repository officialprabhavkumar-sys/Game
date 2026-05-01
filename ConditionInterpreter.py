
"""
This module contains the ConditionInterpreter,
which is responsible for interpreting conditions and returning boolean values indicating whether the conditions are met or not.
"""

from typing import Callable
from Logger import LogEntry

class ConditionInterpreter():
    """
    The ConditionInterpreter is responsible for interpreting conditions and returning boolean value,
    indicating whether the condition is met or not.
    It also allows for functions to be registered that can be used in conditions.
    All such functions must return a boolean value.
    All empty strings will return True.
    """
    
    __slots__ = ["registered_functions", ]
    
    FUNCTION_CALL_OPERATOR = "@"
    
    def __init__(self, registered_functions : dict[str, Callable[..., bool | int | str | float]]):
        self.registered_functions = registered_functions
    
    @staticmethod
    def interpret_as_bool(value : str) -> bool:
        if value.lower().strip() == "false":
            return False
        return bool(value)
    
    @staticmethod
    def handle_equals(first, second) -> bool:
        if first is None or second is None:
            return False
        return first == second
    
    @staticmethod
    def handle_not_equals(first, second) -> bool:
        if first is None or second is None:
            return False
        return first != second
    
    @staticmethod
    def handle_more_than(first, second) -> bool:
        if first is None or second is None:
            return False
        return first > second
    
    @staticmethod
    def handle_less_than(first, second) -> bool:
        if first is None or second is None:
            return False
        return first < second
    
    @staticmethod
    def handle_more_than_or_equals(first, second) -> bool:
        if first is None or second is None:
            return False
        return first >= second
    
    @staticmethod
    def handle_less_than_or_equals(first, second) -> bool:
        if first is None or second is None:
            return False
        return first <= second
    
    OPERATOR_HANDLERS = { # Do not reorder.
        "==" : handle_equals,
        ">=" : handle_more_than_or_equals,
        "<=" : handle_less_than_or_equals,
        "!=" : handle_not_equals,
        ">" : handle_more_than,
        "<" : handle_less_than,
    }
    
    TYPE_CLASSIFIERS = {
        "^" : int,
        "*" : float,
        "#" : str,
        "~" : interpret_as_bool
    }
    
    def interpret_type(self, value : str) -> int | float | str | bool:
        value = value.strip()
        return self.TYPE_CLASSIFIERS[value[0]](value[1::])
    
    def prepare_for_function_call(self, function_str : str) -> dict[str, str | dict] | None:
        function_str = function_str.strip()
        function_str = function_str[len(self.FUNCTION_CALL_OPERATOR)::] # Removing FUNCTION_CALL_OPERATOR
        function_name, function_args = function_str.split("(", 1)
        if not function_name in self.registered_functions:
            
            LogEntry("CONDITIONINTERPRETER", 1, f"No function by name \"{function_name}\" in function_call \"{function_str}\" found in registered function. Returning None.").push_to_queue()
            
            return None
        function_args = function_args.rstrip(")")
        function_args = [function_arg for function_arg in function_args.split(",") if function_arg]
        correct_function_args = {}
        for function_arg in function_args:
            function_arg_parts = function_arg.split("=")
            if len(function_arg_parts) != 2:
                
                LogEntry("CONDITIONINTERPRETER", 1, f"Function value for argument \"{function_arg}\" not found in function_call \"{function_str}\". Returning None.").push_to_queue()
                
                return None
            correct_function_args[function_arg_parts[0]] = self.interpret_type(function_arg_parts[1])
        return {
            "function_name" : function_name,
            "function_args" : correct_function_args
            }
    
    def get_result_for(self, condition : str) -> bool | int | float | str:
        
        condition = condition.strip()
        
        if not condition:
            return True
        
        for operator in self.OPERATOR_HANDLERS.keys():
            if operator in condition:
                condition_parts = [part.strip() for part in condition.split(operator, 1)]
                if len(condition_parts) < 2:
                    return False # condition is invalid.
                first = condition_parts[0]
                second = condition_parts[1]
                first = self.get_result_for(first) if self.FUNCTION_CALL_OPERATOR in first else self.interpret_type(first)
                second = self.get_result_for(second) if self.FUNCTION_CALL_OPERATOR in second else self.interpret_type(second)
                return self.OPERATOR_HANDLERS[operator](first, second) or False # If operator_handler returns None.
        if not self.FUNCTION_CALL_OPERATOR in condition:
            
            LogEntry("CONDITIONINTERPRETER", 1, f"Condition \"{condition}\" is invalid, no FUNCTION_CALL_OPERATOR \"{self.FUNCTION_CALL_OPERATOR}\" found. Returning False.").push_to_queue()
            
            return False #condition is invalid.
        prepared_arguments = self.prepare_for_function_call(condition)
        if prepared_arguments is None:
            return False # condition is invalid.
        function_name = prepared_arguments["function_name"]
        function_args = prepared_arguments["function_args"]
        if not isinstance(function_name, str) or not isinstance(function_args, dict): # type hint checker was throwing a tantrum.
            return False
        return self.registered_functions[function_name](**function_args)
    
    def interpret_condition(self, condition : str) -> bool:
        """
        Interprets a condition and returns a boolean value indicating whether the condition is met or not.
        The condition may contain : 
        either one function call or two function calls seperated by operators such as "==", "!=", ">", "<", ">=" and "<=".
        The functions must be registered in the registered_functions dictionary and the condition itself must be a string.
        
        Note:
        Multiple operators are not supported, a single condition may only have a single operator.
        """
        
        condition = condition.strip()
        
        if not condition:
            return True
        try: # For the sake of not stopping the whole game because of one bad conditional.
            return bool(self.get_result_for(condition))
        except Exception as e:
            
            LogEntry("CONDITION_INTERPRETER", 1, f"Condition \"{condition}\" caused error \"{str(e)}\". Error handled, returned False as condition evaluation.").push_to_queue()
            
            return False
 
def test_module():
    def test_module_return_true() -> bool:
        return True

    def test_module_return_false() -> bool:
        return False

    def test_module_return_0() -> int:
        return 0

    def test_module_return_1() -> int:
        return 1
    
    print("Testing module ConditionInterpreter.py")
    
    condition_interpreter = ConditionInterpreter({"return_true" : test_module_return_true, "return_false" : test_module_return_false, "return_0" : test_module_return_0, "return_1" : test_module_return_1})
    print(condition_interpreter.interpret_condition(""))
    print(condition_interpreter.interpret_condition("@return_true()"))
    print(condition_interpreter.interpret_condition("@return_1() == ^1"))
    print(condition_interpreter.interpret_condition("@return_0() < *2"))
    # needs more test cases.
    
    print("Test Complete.")

if __name__ == "__main__":
    test_module()