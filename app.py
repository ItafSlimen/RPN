
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, reqparse, fields
from werkzeug.exceptions import BadRequest
from rpn_calculator_controller import RpnCalculatorController


# Create Flask APP
app = Flask(__name__)
api = Api(app, version='1.0', title='RPN API | Itaf Ben SLIMEN',
          description='RPN API', default='rpn', default_label='RPN API')


# Create Stack Input
create_stack_input = api.model('create_stack_input', {
'stack': fields.String(
    required=True,
    description="A list of numbers and operands seperated by space",
    example="3 4 +"
)
})


# LIST OF OPERAND
rpn_ctrl = RpnCalculatorController()
@api.route('/rpn/op')
class Operators(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal error')
    def get(self):
        """List all the operand."""
        try:
            result = rpn_ctrl.get_operand_list()
            return result, 200
        except ValueError as e:
            raise BadRequest(str(e))


# APPLY OPERAND TO STACK
@api.route('/rpn/op/<op>/stack/<int:stack_id>')
class OperatorsStack(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Invalid input')
    def post(self, op, stack_id):
        """Apply an operand to a stack"""
        try:
            return rpn_ctrl.evaluate_rpn(op, stack_id)
        except ValueError as e:
            raise BadRequest(str(e))


# CREATE NEW STACK & GET ALL STACKS
@api.route('/rpn/stack')
class RPNCalculatorStack(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal error')
    def get(self):
        """List the available stacks"""
        try:
            all_stacks_list = rpn_ctrl.get_all_stacks()
            return {'all_stacks_list': all_stacks_list}, 200
        except ValueError as e:
            raise BadRequest(str(e))

    @api.expect(create_stack_input)   
    @api.response(201, 'Created')
    @api.response(400, 'Invalid input')
    def post(self):
        """Create a new stack"""
        data = request.get_json()
        new_stack = data.get('stack')
        try:
            stack_id = rpn_ctrl.create_stack(new_stack)
            return {'stack_id': stack_id}, 201
        except ValueError as e:
            raise BadRequest(str(e))
        

# GET & UPDATE & DELETE BY ID
@api.route('/rpn/stack/<int:stack_id>')
class RPNCalculatorStackById(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Not found')
    def get(self, stack_id):
        """Get a stack by id"""
        try:
            stack = rpn_ctrl.get_stack(stack_id)
            return stack, 200
        except ValueError as e:
            raise BadRequest(str(e))
        
    @api.expect(create_stack_input)
    @api.response(200, 'Success')
    @api.response(400, 'Invalid input')
    def post(self, stack_id):
        """Push a new value to a stack"""
        data = request.get_json()
        stack = data.get('stack')
        try:
            updated_stack = rpn_ctrl.update_stack(stack_id, stack)
            return {'updated_stack': updated_stack}, 200
        except ValueError as e:
            raise BadRequest(str(e))
        
    @api.response(200, 'Success')
    @api.response(404, 'not found')
    def delete(self, stack_id):
        """Delete a stack"""

        try:
            deleted_stack = rpn_ctrl.delete_stack(stack_id)
            return {'deleted_stack': deleted_stack}, 200
        except ValueError as e:
            raise BadRequest(str(e))
        
if __name__ == '__main__':
    app.run('127.0.0.1', port=5500, debug= True)
