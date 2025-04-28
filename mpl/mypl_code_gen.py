"""IR code generator for converting MyPL to VM Instructions. 

NAME: <Caleb Lefcort>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mpl.mypl_token import *
from mpl.mypl_ast import *
from mpl.mypl_var_table import *
from mpl.mypl_frame import *
from mpl.mypl_opcode import *
from mpl.mypl_vm import *

length_types = ['length_intarray', 'length_doublearray', 'length_stringarray', 'length_boolarray','length_string']
class CodeGenerator (Visitor):

    def __init__(self, vm):
        """Creates a new Code Generator given a VM. 
        
        Args:
            vm -- The target vm.
        """
        # the vm to add frames to
        self.vm = vm
        # the current frame template being generated
        self.curr_template = None
        # for var -> index mappings wrt to environments
        self.var_table = VarTable()
        # struct name -> StructDef for struct field info
        self.struct_defs = {}


    
    def add_instr(self, instr):
        """Helper function to add an instruction to the current template."""
        self.curr_template.instructions.append(instr)
    
    #used to generate the function id from the information in the fun_def node
    def get_fun_id(self, fun_def):
        id = fun_def.fun_name.lexeme
        for param in fun_def.params:
            id += '_'
            id += param.data_type.type_name.lexeme
            if param.data_type.is_array:
                id += 'array'
        return id

        
    def visit_program(self, program):
        for struct_def in program.struct_defs:
            struct_def.accept(self)
        for fun_def in program.fun_defs:
            fun_def.accept(self)

    
    def visit_struct_def(self, struct_def):
        # remember the struct def for later
        self.struct_defs[struct_def.struct_name.lexeme] = struct_def
        length_types.append('length_'+ struct_def.struct_name.lexeme +'array')

        
    def visit_fun_def(self, fun_def):
        self.curr_template = VMFrameTemplate(self.get_fun_id(fun_def), len(fun_def.params))
        self.var_table.push_environment()
        for param in fun_def.params:
            self.var_table.add(param.var_name.lexeme)
            self.add_instr(STORE(self.var_table.get(param.var_name.lexeme)))
        for stmt in fun_def.stmts:
            stmt.accept(self)
        if fun_def.return_type.type_name.lexeme == 'void':
            self.add_instr(PUSH(None))
            self.add_instr(RET())
        self.var_table.pop_environment()
        self.vm.add_frame_template(self.curr_template)
        

    def visit_return_stmt(self, return_stmt):
        return_stmt.expr.accept(self)
        self.add_instr(RET())

        
    def visit_var_decl(self, var_decl):
        self.var_table.add(var_decl.var_def.var_name.lexeme)
        if var_decl.expr:
            var_decl.expr.accept(self)
        else:
            self.add_instr(PUSH(None))
        self.add_instr(STORE(self.var_table.get(var_decl.var_def.var_name.lexeme)))
            
        
    def visit_assign_stmt(self, assign_stmt):
        if len(assign_stmt.lvalue) == 1:    
            if assign_stmt.lvalue[0].array_expr:
                self.add_instr(LOAD(self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)))
                assign_stmt.lvalue[0].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(STORE(self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)))
        else:
            self.add_instr(LOAD(self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)))
            if assign_stmt.lvalue[0].array_expr:
                assign_stmt.lvalue[0].array_expr.accept(self)
                self.add_instr(GETI())
            for var_ref in assign_stmt.lvalue[1:-1]:
                self.add_instr(GETF(var_ref.var_name.lexeme))
                if var_ref.array_expr:
                    var_ref.array_expr.accept(self)
                    self.add_instr(GETI())
            if assign_stmt.lvalue[-1].array_expr:
                self.add_instr(GETF(assign_stmt.lvalue[-1].var_name.lexeme))
                assign_stmt.lvalue[-1].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(SETF(assign_stmt.lvalue[-1].var_name.lexeme))


    def visit_while_stmt(self, while_stmt):
        jump_index = len(self.curr_template.instructions)
        while_stmt.condition.accept(self)
        jump_end = JMPF(-1)
        self.add_instr(jump_end)
        self.var_table.push_environment()
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        self.var_table.pop_environment()
        self.add_instr(JMP(jump_index))
        self.add_instr(NOP())
        jump_end.operand = len(self.curr_template.instructions) -1

        
    def visit_for_stmt(self, for_stmt):
        self.var_table.push_environment()
        for_stmt.var_decl.accept(self)
        jump_index = len(self.curr_template.instructions)
        for_stmt.condition.accept(self)
        jump_end = JMPF(-1)
        self.add_instr(jump_end)
        self.var_table.push_environment()
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.var_table.pop_environment()
        for_stmt.assign_stmt.accept(self)
        self.add_instr(JMP(jump_index))
        self.add_instr(NOP())
        jump_end.operand = len(self.curr_template.instructions) -1
        self.var_table.pop_environment()

    
    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.condition.accept(self)
        jump_next = JMPF(-1)
        self.add_instr(jump_next)
        self.var_table.push_environment()
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        self.var_table.pop_environment()
        jump_end = JMP(-1)
        self.add_instr(jump_end)
        jump_next.operand = len(self.curr_template.instructions)
        if if_stmt.else_ifs:
            for else_if in if_stmt.else_ifs:
                else_if.condition.accept(self)
                jump_next_elif = JMPF(-1)
                self.add_instr(jump_next_elif)
                self.var_table.push_environment()
                for stmt in else_if.stmts:
                    stmt.accept(self)
                self.var_table.pop_environment()
                self.add_instr(jump_end)
                jump_next_elif.operand = len(self.curr_template.instructions)
        if if_stmt.else_stmts:
            self.var_table.push_environment()
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.var_table.pop_environment()
        self.add_instr(NOP())
        jump_end.operand = len(self.curr_template.instructions) -1
            
    
    def visit_call_expr(self, call_expr):
        for arg in call_expr.args:
            arg.accept(self)
        if call_expr.fun_id in ['print_string','print_int','print_double','print_bool']:
            self.add_instr(WRITE())
        elif call_expr.fun_id == 'itos_int':
            self.add_instr(TOSTR())
        elif call_expr.fun_id == 'dtos_double':
            self.add_instr(TOSTR())
        elif call_expr.fun_id == 'itod_int':
            self.add_instr(TODBL())
        elif call_expr.fun_id == 'stod_string':
            self.add_instr(TODBL())
        elif call_expr.fun_id == 'stoi_string':
            self.add_instr(TOINT())
        elif call_expr.fun_id == 'dtoi_double':
            self.add_instr(TOINT())
        elif call_expr.fun_id == 'input':
            self.add_instr(READ())
        elif call_expr.fun_id in length_types:
            self.add_instr(LEN())
        elif call_expr.fun_id == 'get_int_string':
            self.add_instr(GETC())
        else:
            self.add_instr(CALL(call_expr.fun_id))

        
    def visit_expr(self, expr):
        if expr.op:
            if expr.op.lexeme == '>=' or expr.op.lexeme == '>':
                expr.rest.accept(self)
                expr.first.accept(self)
                if expr.op.lexeme == '>=':
                    self.add_instr(CMPLE())
                if expr.op.lexeme == '>':
                    self.add_instr(CMPLT())
            else:
                expr.first.accept(self)
                expr.rest.accept(self)
                if expr.op.lexeme == '+':
                    self.add_instr(ADD())
                if expr.op.lexeme == '-':
                    self.add_instr(SUB())
                if expr.op.lexeme == '/':
                    self.add_instr(DIV())
                if expr.op.lexeme == '*':
                    self.add_instr(MUL())
                if expr.op.lexeme == 'and':
                    self.add_instr(AND())
                if expr.op.lexeme == 'or':
                    self.add_instr(OR())
                if expr.op.lexeme == '==':
                    self.add_instr(CMPEQ())
                if expr.op.lexeme == '!=':
                    self.add_instr(CMPNE())
                if expr.op.lexeme == '<=':
                    self.add_instr(CMPLE())
                if expr.op.lexeme == '<':
                    self.add_instr(CMPLT())
        else:
            expr.first.accept(self)
        if expr.not_op:
            self.add_instr(NOT())

            
    def visit_data_type(self, data_type):
        # nothing to do here
        pass

    
    def visit_var_def(self, var_def):
        # nothing to do here
        pass

    
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

        
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)

        
    def visit_simple_rvalue(self, simple_rvalue):
        val = simple_rvalue.value.lexeme
        if simple_rvalue.value.token_type == TokenType.INT_VAL:
            self.add_instr(PUSH(int(val)))
        elif simple_rvalue.value.token_type == TokenType.DOUBLE_VAL:
            self.add_instr(PUSH(float(val)))
        elif simple_rvalue.value.token_type == TokenType.STRING_VAL:
            val = val.replace('\\n', '\n')
            val = val.replace('\\t', '\t')
            self.add_instr(PUSH(val))
        elif val == 'true':
            self.add_instr(PUSH(True))
        elif val == 'false':
            self.add_instr(PUSH(False))
        elif val == 'null':
            self.add_instr(PUSH(None))

    
    def visit_new_rvalue(self, new_rvalue):
        if new_rvalue.array_expr:
            new_rvalue.array_expr.accept(self)
            self.add_instr(ALLOCA())
        elif new_rvalue.type_name.lexeme in self.struct_defs:
            self.add_instr(ALLOCS())
            for count, expr in enumerate(new_rvalue.struct_params):
                self.add_instr(DUP())
                expr.accept(self)
                self.add_instr(SETF(self.struct_defs[new_rvalue.type_name.lexeme].fields[count].var_name.lexeme))

    
    def visit_var_rvalue(self, var_rvalue):
        self.add_instr(LOAD(self.var_table.get(var_rvalue.path[0].var_name.lexeme)))
        if var_rvalue.path[0].array_expr:
            var_rvalue.path[0].array_expr.accept(self)
            self.add_instr(GETI())
        for var_ref in var_rvalue.path[1:]:
            self.add_instr(GETF(var_ref.var_name.lexeme))
            if var_ref.array_expr:
                var_ref.array_expr.accept(self)
                self.add_instr(GETI())


                
