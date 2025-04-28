"""Semantic Checker Visitor for semantically analyzing a MyPL program.

NAME: <Caleb Lefcort>
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mpl.mypl_error import *
from mpl.mypl_token import Token, TokenType
from mpl.mypl_ast import *
from mpl.mypl_symbol_table import SymbolTable


BASE_TYPES = ['int', 'double', 'bool', 'string']
#modified to be function ids insted of names
BUILT_INS = ['print_string','print_int','print_double','print_bool', 'input', 'itos_int', 'itod_int', 'dtos_double', 'dtoi_double', 'stoi_string', 'stod_string',
            'get_int_string']
#needed for the length built in
length_types = ['length_intarray', 'length_doublearray', 'length_stringarray', 'length_boolarray','length_string']
class SemanticChecker(Visitor):
    """Visitor implementation to semantically check MyPL programs."""

    def __init__(self):
        self.structs = {}
        self.functions = {}
        self.symbol_table = SymbolTable()
        self.curr_type = None


    # Helper Functions

    def error(self, msg, token):
        """Create and raise a Static Error."""
        if token is None:
            raise StaticError(msg)
        else:
            m = f'{msg} near line {token.line}, column {token.column}'
            raise StaticError(m)


    def get_field_type(self, struct_def, field_name):
        """Returns the DataType for the given field name of the struct
        definition.

        Args:
            struct_def: The StructDef object 
            field_name: The name of the field

        Returns: The corresponding DataType or None if the field name
        is not in the struct_def.

        """
        for var_def in struct_def.fields:
            if var_def.var_name.lexeme == field_name:
                return var_def.data_type
        return None
    
    #used to generate the function id from the information in the fun_def node
    def get_fun_id(self, fun_def):
        id = fun_def.fun_name.lexeme
        for param in fun_def.params:
            id += '_'
            id += param.data_type.type_name.lexeme
            if param.data_type.is_array:
                id += 'array'
        return id

        
    # Visitor Functions
    
    def visit_program(self, program):
        # check and record struct defs
        for struct in program.struct_defs:
            struct_name = struct.struct_name.lexeme
            if struct_name in self.structs:
                self.error(f'duplicate {struct_name} definition', struct.struct_name)
            self.structs[struct_name] = struct
            length_types.append('length_'+ struct_name +'array')
        # check and record function defs
        for fun in program.fun_defs:
            #fun_name = fun.fun_name.lexeme
            id = self.get_fun_id(fun)
            if id in self.functions: 
                self.error(f'duplicate {id} definition', fun.fun_name)
            if id in BUILT_INS or id in length_types:
                self.error(f'redefining built-in function', fun.fun_name)
            if id == 'main' and fun.return_type.type_name.lexeme != 'void':
                self.error('main without void type', fun.return_type.type_name)
            if fun.fun_name.lexeme == 'main' and fun.params: 
                self.error('main function with parameters', fun.fun_name)
            self.functions[id] = fun
        # check main function
        if 'main' not in self.functions:
            self.error('missing main function', None)
        # check each struct
        for struct in self.structs.values():
            struct.accept(self)
        # check each function
        for fun in self.functions.values():
            fun.accept(self)
        
        
    def visit_struct_def(self, struct_def):
        self.symbol_table.push_environment()
        for field in struct_def.fields:
            field.accept(self)
            field_type = self.curr_type.type_name.lexeme
            if field_type == 'void':
                self.error('void struct field', self.curr_type.type_name)
        self.symbol_table.pop_environment()


    def visit_fun_def(self, fun_def):
        self.symbol_table.push_environment()
        fun_def.return_type.accept(self)
        self.symbol_table.add('return', self.curr_type)
        for param in fun_def.params:
            param.accept(self)
        for stmt in fun_def.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()

        
    def visit_return_stmt(self, return_stmt):
        return_stmt.expr.accept(self)
        if self.curr_type.type_name.lexeme != 'void' and self.curr_type.type_name.lexeme != self.symbol_table.get('return').type_name.lexeme:
            self.error('Static Error: return type does not match function return', self.curr_type.type_name)

            
    def visit_var_decl(self, var_decl):
        var_decl.var_def.accept(self)
        lhs = self.curr_type
        if var_decl.expr:
            var_decl.expr.accept(self)
            if self.curr_type.type_name.lexeme != 'void' and (lhs.type_name.lexeme != self.curr_type.type_name.lexeme or lhs.is_array != self.curr_type.is_array):
                self.error('lhs and rhs types do not match', lhs.type_name)
        
        
    def visit_assign_stmt(self, assign_stmt):
        if not self.symbol_table.exists(assign_stmt.lvalue[0].var_name.lexeme):
            self.error("use before def",self.curr_type.type_name)
        lvalue_type = self.symbol_table.get(assign_stmt.lvalue[0].var_name.lexeme)
        i = 0
        if len(assign_stmt.lvalue) > 1:
            if self.symbol_table.get(assign_stmt.lvalue[i].var_name.lexeme).type_name.lexeme not in self.structs:
                self.error('struct not defined', self.curr_type.type_name)
            struct_def = self.structs[self.symbol_table.get(assign_stmt.lvalue[i].var_name.lexeme).type_name.lexeme]    
            while i < len(assign_stmt.lvalue) - 1:
                struct_fields = []
                for j in struct_def.fields:
                    struct_fields.append(j.var_name.lexeme)
                if assign_stmt.lvalue[i+1].var_name.lexeme not in struct_fields:
                    self.error('field not in struct', self.curr_type.type_name)
                lvalue_type = self.get_field_type(struct_def,assign_stmt.lvalue[i+1].var_name.lexeme)
                if i < len(assign_stmt.lvalue) - 2:
                    if lvalue_type.is_array and assign_stmt.lvalue[i+1].array_expr == None:
                        self.error('array not indexed', self.curr_type.type_name)
                    struct_def = self.structs[self.get_field_type(struct_def,assign_stmt.lvalue[i+1].var_name.lexeme).type_name.lexeme]
                i = i+1
        if assign_stmt.lvalue[-1].array_expr:
            assign_stmt.lvalue[-1].array_expr.accept(self)
            if self.curr_type.type_name.lexeme != 'int':
                self.error('invalid array iterator', self.curr_type.type_name)
            if len(assign_stmt.lvalue) == 1:
                array_type = self.symbol_table.get(assign_stmt.lvalue[-1].var_name.lexeme)
            else:
                array_type = self.get_field_type(struct_def, assign_stmt.lvalue[-1].var_name.lexeme)
            lvalue_type = DataType(False, array_type.type_name)
        assign_stmt.expr.accept(self)
        if (lvalue_type.type_name.lexeme != self.curr_type.type_name.lexeme or lvalue_type.is_array != self.curr_type.is_array) and self.curr_type.type_name.lexeme != 'void':
            self.error('lhs and rhs types do not match', self.curr_type.type_name)
        
            
    def visit_while_stmt(self, while_stmt):
        self.symbol_table.push_environment()
        while_stmt.condition.accept(self)
        if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
            self.error('while condition is not a bool', self.curr_type.type_name)
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
                
    def visit_for_stmt(self, for_stmt):
        self.symbol_table.push_environment()
        for_stmt.var_decl.accept(self)
        if self.curr_type.type_name.lexeme not in ['int', 'double']:
            self.error('invalid iterator type', self.curr_type.type_name)
        for_stmt.condition.accept(self)
        if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
            self.error('for condition is not a bool', self.curr_type.type_name)
        for_stmt.assign_stmt.accept(self)
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()

        
        
    def visit_if_stmt(self, if_stmt):
        self.symbol_table.push_environment()
        if_stmt.if_part.condition.accept(self)
        if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
            self.error('for condition is not a bool', self.curr_type.type_name)
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        for else_if in if_stmt.else_ifs:
            self.symbol_table.push_environment()
            else_if.condition.accept(self)
            if self.curr_type.type_name.lexeme != 'bool' or self.curr_type.is_array:
                self.error('for condition is not a bool', self.curr_type.type_name)
            for stmt in else_if.stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()
        if if_stmt.else_stmts != []:
            self.symbol_table.push_environment()
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()

    def visit_call_expr(self, call_expr):
        id = call_expr.fun_name.lexeme
        for arg in call_expr.args:
            arg.accept(self)
            id += '_'
            id += self.curr_type.type_name.lexeme
            if self.curr_type.is_array:
                id += 'array'
        call_expr.fun_id = id
        if id not in self.functions and id not in BUILT_INS and id not in length_types:
            self.error('function not defined', self.curr_type.type_name)
        if id in self.functions and (id in BUILT_INS or id in length_types):
            self.error('Built in function double defined', self.curr_type.type_name)
        if id in self.functions:
            fun_def = self.functions[id]
            if len(fun_def.params) != len(call_expr.args):
                self.error('Invalid number of function params', self.curr_type.type_name)
            for i in range(len(fun_def.params)):
                call_expr.args[i].accept(self)
                if fun_def.params[i].data_type.type_name.lexeme != self.curr_type.type_name.lexeme and self.curr_type.type_name.lexeme != 'void':
                    self.error('Invlaid paramater type', call_expr.fun_name)
            self.curr_type = fun_def.return_type
        elif(id == 'print_string' or id == 'print_int' or id == 'print_double' or id == 'print_bool'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme not in BASE_TYPES or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
        elif(id == 'input'):
            if len(call_expr.args) != 0:
                self.error('Invalid number of function params', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.STRING_TYPE,'string',1,1))
        elif(id == 'itos_int'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.STRING_TYPE,'string',1,1))
        elif(id == 'itod_int'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.DOUBLE_TYPE,'double',1,1))
        elif(id == 'dtos_double'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'double' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.STRING_TYPE,'string',1,1))
        elif(id == 'dtoi_double'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'double' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.INT_TYPE,'int',1,1))
        elif(id == 'stoi_string'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.INT_TYPE,'int',1,1))
        elif(id == 'stod_string'):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.DOUBLE_TYPE,'double',1,1))
        elif(id in length_types):
            if len(call_expr.args) != 1:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'string' and self.curr_type.is_array == False:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.INT_TYPE,'int',1,1))
        elif(id == 'get_int_string'):
            if len(call_expr.args) != 2:
                self.error('Invalid number of function params', self.curr_type.type_name)
            call_expr.args[0].accept(self)
            if self.curr_type.type_name.lexeme != 'int' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            call_expr.args[1].accept(self)
            if self.curr_type.type_name.lexeme != 'string' or self.curr_type.is_array:
                self.error('Invalid paramater type', self.curr_type.type_name)
            self.curr_type = DataType(False,Token(TokenType.STRING_TYPE,'string',1,1))
        

    def visit_expr(self, expr):
        expr.first.accept(self)
        lhs_type = self.curr_type
        if expr.op:
            expr.rest.accept(self)
            rhs_type = self.curr_type
            if lhs_type.type_name.lexeme != rhs_type.type_name.lexeme and lhs_type.type_name.lexeme != 'void' and rhs_type.type_name.lexeme != 'void':
                self.error('expr types do not match', expr.op)
            if expr.op.lexeme == '+':
                if lhs_type.type_name.lexeme not in ['string', 'int', 'double'] or rhs_type.type_name.lexeme == 'void' or lhs_type.type_name.lexeme == 'void':
                    self.error(f'invalid use of {expr.op.lexeme}', expr.op)
                else:
                    self.curr_type = lhs_type
            elif expr.op.lexeme == '-' or expr.op.lexeme == '/' or expr.op.lexeme == '*':
                if lhs_type.type_name.lexeme not in ['int', 'double'] or rhs_type.type_name.lexeme == 'void' or lhs_type.type_name.lexeme == 'void':
                    self.error(f'invalid use of {expr.op.lexeme}', expr.op)
                else:
                    self.curr_type = lhs_type
            elif expr.op.lexeme == '>=' or expr.op.lexeme == '<=' or expr.op.lexeme == '<' or expr.op.lexeme == '>':
                if lhs_type.type_name.lexeme not in ['string','int','double'] or rhs_type.type_name.lexeme == 'void' or lhs_type.type_name.lexeme == 'void':
                    self.error(f'invalid use of {expr.op.lexeme}', expr.op)
                else:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', 1, 1))
            elif expr.op.lexeme == 'and' or expr.op.lexeme == 'or':
                if lhs_type.type_name.lexeme not in ['bool'] or rhs_type.type_name.lexeme == 'void' or lhs_type.type_name.lexeme == 'void':
                    self.error(f'invalid use of {expr.op.lexeme}', expr.op)
                else:
                    self.curr_type = lhs_type
            elif expr.op.lexeme == '==' or expr.op.lexeme == '!=':
                if lhs_type.type_name.lexeme not in ['string','bool','int', 'double', 'void'] and lhs_type.type_name.lexeme not in self.structs and rhs_type.type_name.lexeme != 'void' and lhs_type.type_name.lexeme != 'void':
                    self.error(f'invalid use of {expr.op.lexeme}', expr.op)
                else:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', 1, 1))
        if expr.not_op:
            if self.curr_type.type_name.lexeme != 'bool':
                self.error('invalid use of not op', self.curr_type.type_name)

        

    def visit_data_type(self, data_type):
        # note: allowing void (bad cases of void caught by parser)
        name = data_type.type_name.lexeme
        if name == 'void' or name in BASE_TYPES or name in self.structs:
            self.curr_type = data_type
        else: 
            self.error(f'invalid type "{name}"', data_type.type_name)
            
    
    def visit_var_def(self, var_def):
        var_def.data_type.accept(self)
        var_name = var_def.var_name.lexeme
        if self.symbol_table.exists_in_curr_env(var_name):
            self.error(f'duplicate {var_name} definition', var_def.var_name)
        else:
            self.symbol_table.add(var_def.var_name.lexeme, self.curr_type)
        

        
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)
        
    
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)
        

    def visit_simple_rvalue(self, simple_rvalue):
        value = simple_rvalue.value
        line = simple_rvalue.value.line
        column = simple_rvalue.value.column
        type_token = None 
        if value.token_type == TokenType.INT_VAL:
            type_token = Token(TokenType.INT_TYPE, 'int', line, column)
        elif value.token_type == TokenType.DOUBLE_VAL:
            type_token = Token(TokenType.DOUBLE_TYPE, 'double', line, column)
        elif value.token_type == TokenType.STRING_VAL:
            type_token = Token(TokenType.STRING_TYPE, 'string', line, column)
        elif value.token_type == TokenType.BOOL_VAL:
            type_token = Token(TokenType.BOOL_TYPE, 'bool', line, column)
        elif value.token_type == TokenType.NULL_VAL:
            type_token = Token(TokenType.VOID_TYPE, 'void', line, column)
        self.curr_type = DataType(False, type_token)

        
    def visit_new_rvalue(self, new_rvalue):
        if new_rvalue.array_expr:
            if new_rvalue.type_name.lexeme not in self.structs and new_rvalue.type_name.lexeme not in BASE_TYPES:
                self.error('invalid array type', new_rvalue.type_name)
            new_rvalue.array_expr.accept(self)
            if self.curr_type.type_name.lexeme != 'int':
                self.error('invalid array size type', self.curr_type.type_name)
            self.curr_type = DataType(True, new_rvalue.type_name)
        else:
            if new_rvalue.type_name.lexeme not in self.structs:
                self.error('struct not defined',self.curr_type.type_name)
            struct_def = self.structs[new_rvalue.type_name.lexeme]
            if len(struct_def.fields) != len(new_rvalue.struct_params):
                self.error('Invalid number of struct params',self.curr_type.type_name)
            for i in range(len(struct_def.fields)):
                new_rvalue.struct_params[i].accept(self)
                if struct_def.fields[i].data_type.type_name.lexeme != self.curr_type.type_name.lexeme and self.curr_type.type_name.lexeme != 'void':
                    self.error('Invlaid paramater type', new_rvalue.type_name)
            self.curr_type = DataType(False, new_rvalue.type_name)
        
            
    def visit_var_rvalue(self, var_rvalue):
        if not self.symbol_table.exists(var_rvalue.path[0].var_name.lexeme):
            self.error("use before def",self.curr_type.type_name)
        self.curr_type = self.symbol_table.get(var_rvalue.path[0].var_name.lexeme)
        i = 0
        if len(var_rvalue.path) > 1:
            if self.symbol_table.get(var_rvalue.path[i].var_name.lexeme).type_name.lexeme not in self.structs:
                self.error('struct not defined',self.curr_type.type_name)
            struct_def = self.structs[self.symbol_table.get(var_rvalue.path[i].var_name.lexeme).type_name.lexeme]    
            while i < len(var_rvalue.path) - 1:
                struct_fields = []
                for j in struct_def.fields:
                    struct_fields.append(j.var_name.lexeme)
                if var_rvalue.path[i+1].var_name.lexeme not in struct_fields:
                    self.error('field not in struct',self.curr_type.type_name)
                self.curr_type = self.get_field_type(struct_def,var_rvalue.path[i+1].var_name.lexeme)
                if i < len(var_rvalue.path) - 2:
                    if self.curr_type.is_array and var_rvalue.path[i+1].array_expr == None:
                        self.error('array not indexed', self.curr_type.type_name)
                    struct_def = self.structs[self.get_field_type(struct_def,var_rvalue.path[i+1].var_name.lexeme).type_name.lexeme]
                i = i+1
        if  var_rvalue.path[-1].array_expr:
            var_rvalue.path[-1].array_expr.accept(self)
            if self.curr_type.type_name.lexeme != 'int':
                self.error('invalid array iterator', self.curr_type.type_name)
            if len(var_rvalue.path) == 1:
                array_type = self.symbol_table.get(var_rvalue.path[-1].var_name.lexeme)
            else:
                array_type = self.get_field_type(struct_def, var_rvalue.path[-1].var_name.lexeme)
            self.curr_type = DataType(False, array_type.type_name)


    
        