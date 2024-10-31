import sqlite3
DATABASE = 'rpn_calculator.db'
VALID_OPERATORS = ['+', '-', '*', '/'] 


class RpnCalculatorController:
    """A controller for handling all rpn calculator functions"""

    def __init__(self):
        self.init_db()
    def init_db(self):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stack_id TEXT UNIQUE,
                    stack_data TEXT
                )
            ''')
            conn.commit()

    def evaluate_rpn(self, op, stack_id):
        """Evaluate the specified operator on the top two values of the stack."""
        # Check if the operator is valid
        if op not in VALID_OPERATORS:
            return {"error": "Invalid operator. Must be one of: " + ', '.join(VALID_OPERATORS)}, 400
        
        # Get the current stack
        stack = self.get_stack(stack_id)
        if stack is None:
            return {"error": f"Stack '{stack_id}' not found."}, 404

        # Check if there are at least two operands in the stack
        if len(stack) < 2:
            return {"error": "Not enough operands in the stack to perform the operation."}, 400

        # Pop the top two operands
        b = int(stack.pop())  # Second operand
        a = int(stack.pop())  # First operand

        # Perform the operation based on the operator
        if op == '+':
            result = a + b
        elif op == '-':
            result = a - b
        elif op == '*':
            result = a * b
        elif op == '/':
            if b == 0:
                return {"error": "Division by zero is not allowed."}, 400
            result = a / b
        
        # Push the result back onto the stack
        stack.append(str(result))
        return {"result": str(result), "current_stack": stack}, 200
    
    def get_operand_list():
            """Return supported RPN operand list."""
            return ['+', '-', '*', '/'] 

    def get_new_stack_id(self):
        """Get the next available stack ID."""
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM stacks')
            count = cursor.fetchone()[0]
        return count + 1
        
    def create_stack(self, new_stack):
        """Save a stack to the database."""
        stack_id = self.get_new_stack_id()
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO stacks (stack_id, stack_data) VALUES (?, ?)', (stack_id, ','.join(map(str, new_stack))))
            conn.commit()
        return stack_id

    def get_stack(self, stack_id):
        """Retrieve the current state of a specified stack from the database."""
        ops_list=self.get_operand_list()
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT stack_data FROM stacks WHERE stack_id = ?', (stack_id,))
            row = cursor.fetchone()
            if row:
                return [
                    x.strip() for x in row[0].split(',')
                    if x.strip() and (x.strip().isdigit() or x.strip() in ops_list)
                ]  # Convert string back to list of integers
            return None


    def get_all_stacks(self):
        ops_list=self.get_operand_list()
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT stack_id, stack_data FROM stacks')
            stacks = cursor.fetchall()
        return [
            {
                "stack_id": stack_id,
                # Ensure only valid integers are included in the current stack
                "current_stack": [x for x in stack_data.split(',') if x.strip() and (x.strip().isdigit() or x.strip() in ops_list)]
            }
            for stack_id, stack_data in stacks
        ]


    def update_stack(self, stack_id, stack_data):
        """Update an existing stack in the database."""
        with sqlite3.connect(DATABASE) as conn:
            filtered_stack_data = self.get_stack(stack_id)
            cursor = conn.cursor()
            cursor.execute('UPDATE stacks SET stack_data = ? WHERE stack_id = ?', (','.join(map(str, filtered_stack_data)), stack_id))
            conn.commit()
        return stack_id

        
    def delete_stack(self, stack_id):
        """Delete a specified stack from the database."""
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stacks WHERE stack_id = ?', (stack_id,))
            conn.commit()
        return stack_id