my_data = {'name': 'Alice', 'age': 30}
alias_data = my_data # Both variables now refer to the same dictionary object

# Modify the dictionary using my_data
my_data['age'] = 31
print(f"my_data: {my_data}")       # Output: my_data: {'name': 'Alice', 'age': 31}
print(f"alias_data: {alias_data}") # Output: alias_data: {'name': 'Alice', 'age': 31}

# Modify the dictionary using alias_data
alias_data['city'] = 'Tokyo'
print(f"my_data: {my_data}")       # Output: my_data: {'name': 'Alice', 'age': 31, 'city': 'Tokyo'}
print(f"alias_data: {alias_data}") # Output: alias_data: {'name': 'Alice', 'age': 31, 'city': 'Tokyo'}