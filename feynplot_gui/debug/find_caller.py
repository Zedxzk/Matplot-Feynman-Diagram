# feynplot_gui\debug\find_caller.py

import inspect
import os

def get_caller_info(depth: int = 2, base_path: str = None) -> dict:
    """
    Retrieves information about the function at a specific depth in the call stack.

    Args:
        depth (int): The number of stack frames to go back from the point where
                     inspect.stack() is called.
                     - depth=0: The current frame (get_caller_info itself).
                     - depth=1: The direct caller of get_caller_info.
                     - depth=2: The caller of the function that called get_caller_info.
        base_path (str, optional): The base path to make the file path relative to.
                                   If None, the full path is used.

    Returns:
        dict: A dictionary containing 'file', 'line', and 'function' of the frame,
              or default 'N/A' values if the depth is out of range.
    """
    try:
        frame_info = inspect.stack()[depth]
        
        full_filename = os.path.normpath(frame_info.filename) # Normalize full path
        lineno = frame_info.lineno
        function_name = frame_info.function
        
        # Calculate relative path if base_path is provided
        if base_path and full_filename.startswith(os.path.normpath(base_path)):
            # Ensure base_path ends with a separator for correct relative path calculation
            normalized_base_path = os.path.normpath(base_path)
            if not normalized_base_path.endswith(os.sep):
                normalized_base_path += os.sep
            
            # Use os.path.relpath if available and suitable, otherwise manual slicing
            # relpath is robust for cases with ".."
            try:
                display_filename = os.path.relpath(full_filename, base_path)
            except ValueError: # Handle cases where paths don't share a common root (e.g., different drives)
                display_filename = full_filename.replace(normalized_base_path, '')
                if display_filename == full_filename: # If replacement failed, keep full path
                    display_filename = full_filename 
        else:
            display_filename = full_filename # Fallback to full path if no base or doesn't start with base

        return {
            "file": display_filename,
            "line": lineno,
            "function": function_name
        }
    except IndexError:
        return {
            "file": "N/A",
            "line": -1,
            "function": "N/A"
        }

def print_caller_info(start_depth: int = 1, max_depth: int = 5, message: str = "Call Stack:", base_path: str = None) -> None:
    """
    Prints information about the call stack, recursively up to a specified maximum depth.
    This is a convenience function for direct debugging output.

    Args:
        start_depth (int): The initial number of stack frames to go back to start printing.
        max_depth (int): The maximum number of stack frames to print, starting from `start_depth`.
        message (str): An optional prefix message for the output.
        base_path (str, optional): The base path to make file paths relative to.
                                   If None, full paths are used. This should typically be
                                   your project's root directory.
    """
    print(f"--- {message} ---")
    current_stack = inspect.stack()
    
    for i in range(start_depth, start_depth + max_depth):
        try:
            frame_info = current_stack[i]
            info = inspect.getframeinfo(frame_info.frame)
            
            # Use the get_caller_info with depth adjusted for the loop and base_path
            # get_caller_info(i) from here means get_caller_info is looking at its caller (i-1) in this loop.
            # So the depth parameter to get_caller_info needs to be 'i' itself.
            caller_details = get_caller_info(depth=i, base_path=base_path) 
            
            # Indent based on stack level for readability
            indent = "  " * (i - start_depth)
            print(f"{indent}File: {caller_details['file']}, Line: {caller_details['line']}, Function: {caller_details['function']}")
        except IndexError:
            print(f"{'  ' * (i - start_depth)}--- End of stack ---")
            break
    print(f"-------------------\n")


# Example Usage
if __name__ == "__main__":
    # Define a hypothetical project root for testing relative paths
    # In a real app, you might derive this from __file__ or a config.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    print(f"Simulated Project Root: {PROJECT_ROOT}\n")

    def function_c():
        print("Inside function_c")
        print_caller_info(start_depth=1, max_depth=3, message="Call Stack from function_c (Relative)", base_path=PROJECT_ROOT)

    def function_b():
        print("Inside function_b")
        function_c()

    def function_a():
        print("Inside function_a")
        function_b()

    def test_top_level_call():
        print("Calling test_top_level_call")
        function_a()

    test_top_level_call()

    print("\n--- Testing direct call from main (Relative) ---")
    print_caller_info(start_depth=1, max_depth=3, message="Call Stack from main (Relative)", base_path=PROJECT_ROOT) 
    
    class MyClass:
        def my_method_inner(self):
            print("Inside MyClass.my_method_inner")
            print_caller_info(start_depth=1, max_depth=3, message="Call Stack from my_method_inner (Relative)", base_path=PROJECT_ROOT)

        def my_method_outer(self):
            print("Inside MyClass.my_method_outer")
            self.my_method_inner()

    print("\n--- Testing default depth in a class method (Relative) ---")
    obj = MyClass()
    obj.my_method_outer()

    print("\n--- Testing without base_path (Full Paths) ---")
    def single_caller_test_full_path():
        print("Inside single_caller_test_full_path")
        print_caller_info(start_depth=1, max_depth=1, message="Single Caller Test (Full Path)")
    
    single_caller_test_full_path()