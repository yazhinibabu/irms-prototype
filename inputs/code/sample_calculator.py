"""
Sample calculator module for testing IRMS
"""

def add(a, b):
    return a + b

def divide(a, b):
    return a / b

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class Calculator:
    def __init__(self):
        self.history = []
    
    def add_to_history(self, operation):
        self.history.append(operation)
    
    def get_history(self):
        return self.history
