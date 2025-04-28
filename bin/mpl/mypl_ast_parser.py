"""MyPL AST parser implementation.

NAME: <Caleb Lefcort>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mpl.mypl_error import *
from mpl.mypl_token import *
from mpl.mypl_lexer import *
from mpl.mypl_ast import *


class ASTParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser, returning a Program AST node."""
        program_node = Program([], [])
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def(program_node)
            else:
                self.fun_def(program_node)
        self.eat(TokenType.EOS, 'expecting EOF')
        return program_node

        
    #----------------------------------------------------------------------
    # Helper functions
    #----------------------------------------------------------------------

    def error(self, message):
        """Raises a formatted parser error.

        Args:
            message -- The basic message (expectation)

        """
        lexeme = self.curr_token.lexeme
        line = self.curr_token.line
        column = self.curr_token.column
        err_msg = f'{message} found "{lexeme}" at line {line}, column {column}'
        raise ParserError(err_msg)


    def advance(self):
        """Moves to the next token of the lexer."""
        self.curr_token = self.lexer.next_token()
        # skip comments
        while self.match(TokenType.COMMENT):
            self.curr_token = self.lexer.next_token()

            
    def match(self, token_type):
        """True if the current token type matches the given one.

        Args:
            token_type -- The token type to match on.

        """
        return self.curr_token.token_type == token_type

    
    def match_any(self, token_types):
        """True if current token type matches on of the given ones.

        Args:
            token_types -- Collection of token types to check against.

        """
        for token_type in token_types:
            if self.match(token_type):
                return True
        return False

    
    def eat(self, token_type, message):
        """Advances to next token if current tokey type matches given one,
        otherwise produces and error with the given message.

        Args: 
            token_type -- The totken type to match on.
            message -- Error message if types don't match.

        """
        if not self.match(token_type):
            self.error(message)
        self.advance()

        
    def is_bin_op(self):
        """Returns true if the current token is a binary operator."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)


    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------


    # TODO: Finish the recursive descent functions below. Note that
    # you should copy in your functions from HW-2 and then instrument
    # them to build the corresponding AST objects.
    

    def struct_def(self, program_node):
        """Check for well-formed struct definition."""
        struct_def_node =  StructDef(None, [])
        self.eat(TokenType.STRUCT, 'expecting STRUCT in struct_def')
        struct_def_node.struct_name = self.curr_token
        self.eat(TokenType.ID, 'expecting ID in struct_def')
        self.eat(TokenType.LBRACE, 'expecting LBRACE in struct_def')
        self.fields(struct_def_node)
        self.eat(TokenType.RBRACE, 'expecting RBRACE in struct_def')
        program_node.struct_defs.append(struct_def_node)

        
    def fields(self, struct_def_node):
        """Check for well-formed struct fields."""
        while self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            var_def_node = VarDef(None, None)
            var_def_node.data_type = self.data_type()
            var_def_node.var_name = self.curr_token
            struct_def_node.fields.append(var_def_node)
            self.eat(TokenType.ID, 'expecting ID in fields')
            self.eat(TokenType.SEMICOLON, 'expecting SEMICOLON in fields')
            
    def fun_def(self, program_node):
        """Check for well-formed function definition."""
        fun_def_node = FunDef(None,None,[],[])
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            fun_def_node.return_type = self.data_type()
        elif self.match(TokenType.VOID_TYPE):
            fun_def_node.return_type = DataType(False, self.curr_token)
            self.advance()
        else:
            self.error('Expecting data_type or VOID_TYPE in fun_def')
        fun_def_node.fun_name = self.curr_token
        self.eat(TokenType.ID,'Expecting ID in fun_def')
        self.eat(TokenType.LPAREN,'Expecting LPAREN in fun_def')
        fun_def_node.params = self.params()
        self.eat(TokenType.RPAREN,'Expecting RPAREN in fun_def')
        self.eat(TokenType.LBRACE,'Expecting LBRACE in fun_def')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE,TokenType.DOUBLE_TYPE,TokenType.BOOL_TYPE,TokenType.STRING_TYPE,TokenType.ID,TokenType.ARRAY,]):
            fun_def_node.stmts.append(self.stmt())
        self.eat(TokenType.RBRACE,'Expecting RBRACE in fun_def')
        program_node.fun_defs.append(fun_def_node)

    def params(self):
        """Check for well-formed function formal parameters."""
        param_list = []
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            var_def_node = VarDef(None, None)
            var_def_node.data_type = self.data_type()
            var_def_node.var_name = self.curr_token
            param_list.append(var_def_node)
            self.eat(TokenType.ID,'Expecting ID in params')
            while self.match(TokenType.COMMA):
                self.advance()
                var_def_node_next = VarDef(None, None)
                var_def_node_next.data_type = self.data_type()
                var_def_node_next.var_name = self.curr_token
                param_list.append(var_def_node_next)
                self.eat(TokenType.ID,'Expecting ID in params')
        return param_list

    def data_type(self):
        """Check for well-formed data types."""
        data_type_node = DataType(None, None)
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
             data_type_node.type_name = self.curr_token
             data_type_node.is_array = False
             self.base_type()
        elif self.match(TokenType.ID):
            data_type_node.type_name = self.curr_token
            data_type_node.is_array = False
            self.advance()
        elif self.match(TokenType.ARRAY):
            data_type_node.is_array = True
            self.advance()
            data_type_node.type_name = self.curr_token
            if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
                self.base_type()
            elif self.match(TokenType.ID):
                self.advance()
            else:
                self.error('Expecting base_type or ID in data_type')
        else:
            self.error('Expecting base_type or ID or ARRAY in data_type')
        return data_type_node

    def base_type(self):
        """Check for well-formed base types."""
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            self.advance()
        else:
            self.error('Expecting INT_TYPE or DOUBLE_TYPE or BOOL_TYPE or STRING_TYPE in base_type')

    def stmt(self):
        """Check for well-formed statements."""
        stmt_node = Stmt()
        if self.match(TokenType.WHILE):
            stmt_node = self.while_stmt()
        elif self.match(TokenType.IF):
            stmt_node = self.if_stmt()
        elif self.match(TokenType.FOR):
            stmt_node = self.for_stmt()
        elif self.match(TokenType.RETURN):
            stmt_node = self.return_stmt()
            self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
        elif self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY]):
            var_def_node = VarDef(None, None)
            var_def_node.data_type = self.data_type()
            #var_def_node.var_name = self.curr_token
            #self.data_type()
            v_decl_node = VarDecl(var_def_node, None)
            self.vdecl_stmt(v_decl_node)
            stmt_node = v_decl_node
            self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
        elif self.match(TokenType.ID):
            id_token = self.curr_token
            self.advance()
            if self.match(TokenType.ID):
                var_def_node = VarDef(None, None)
                var_def_node.data_type = DataType(False, id_token) #???
                v_decl_node = VarDecl(var_def_node, None)
                self.vdecl_stmt(v_decl_node)
                stmt_node = v_decl_node
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            elif self.match_any([TokenType.LBRACKET, TokenType.DOT, TokenType.ASSIGN]):
                var_ref_node = VarRef(id_token,None)
                assign_stmt_node = AssignStmt([], None)
                assign_stmt_node.lvalue.append(var_ref_node)
                self.assign_stmt(assign_stmt_node)
                stmt_node = assign_stmt_node
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            elif self.match(TokenType.LPAREN):
                call_expr_node = CallExpr(id_token, [], None)
                self.call_expr(call_expr_node)
                stmt_node = call_expr_node
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            else:
                self.error('Expecting vdecl_stmt or assign_stmt or call_expr in stmt')
        else:
            self.error('Expecting while_stmt or if_stmt or for_stmt or return_stmt or vdecl_stmt or assign_stmt or call_expr in stmt')
        return stmt_node
        
    def vdecl_stmt(self, v_decl_node): #special does not deal with initial data_type
        """Check for well-formed variable declarations."""
        v_decl_node.var_def.var_name = self.curr_token
        self.eat(TokenType.ID, 'Expecting ID in vdecl_stmt')
        if self.match(TokenType.ASSIGN):
            self.advance()
            v_decl_node.expr = self.expr(Expr(False, None, None, None)) 

    def assign_stmt(self, assign_stmt_node):
        """Check for well-formed assignment statements."""
        self.lvalue(assign_stmt_node)
        self.eat(TokenType.ASSIGN, 'Expecting ASSIGN in assign_stmt')
        assign_stmt_node.expr = self.expr(Expr(False, None, None, None))


    def lvalue(self, assign_stmt_node): #special does not deal with initial ID
        """Check for well-formed left values."""
        if self.match(TokenType.LBRACKET):
            self.advance()
            assign_stmt_node.lvalue[0].array_expr = self.expr(Expr(False, None, None, None))
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in lvalue')
        while self.match(TokenType.DOT):
            self.advance()
            var_ref_node = VarRef(self.curr_token, None)
            self.eat(TokenType.ID, 'Expecting ID in lvalue')
            if self.match(TokenType.LBRACKET):
                self.advance()
                var_ref_node.array_expr = self.expr(Expr(False, None, None, None))
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in lvalue')
            assign_stmt_node.lvalue.append(var_ref_node)
    
    def if_stmt(self):
        """Check for well-formed if statements."""
        if_stmt_node = IfStmt(None, [], [])
        self.eat(TokenType.IF, 'Expecting IF in if_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in if_stmt')
        basic_if_node = BasicIf(None, [])
        basic_if_node.condition = self.expr(Expr(False, None, None, None))
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in if_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            basic_if_node.stmts.append(self.stmt())
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt')
        if_stmt_node.if_part = basic_if_node
        self.if_stmt_t(if_stmt_node)
        return if_stmt_node
    
    def if_stmt_t(self, if_stmt_node):
        """Check for well-formed if statement tails."""
        if self.match(TokenType.ELSEIF):
            self.advance()
            self.eat(TokenType.LPAREN, 'Expecting LPAREN in if_stmt_t')
            basic_if_node = BasicIf(None, [])
            basic_if_node.condition = self.expr(Expr(False, None, None, None))
            self.eat(TokenType.RPAREN, 'Expecting RPAREN in if_stmt_t')
            self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt_t')
            while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
                basic_if_node.stmts.append(self.stmt())
            self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt_t')
            if_stmt_node.else_ifs.append(basic_if_node)
            self.if_stmt_t(if_stmt_node)
        elif self.match(TokenType.ELSE):
            self.advance()
            self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt_t')
            while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
                if_stmt_node.else_stmts.append(self.stmt())
            self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt_t')

    def while_stmt(self):
        """Check for well-formed while statements."""
        while_stmt_node = WhileStmt(None, [])
        self.eat(TokenType.WHILE, 'Expecting WHILE in while_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in while_stmt')
        while_stmt_node.condition = self.expr(Expr(False, None, None, None))
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in while_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in while_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            while_stmt_node.stmts.append(self.stmt())
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in while_stmt')
        return while_stmt_node   

    def for_stmt(self):
        """Check for well-formed for statements."""
        for_stmt_node = ForStmt(None, None, None, [])
        self.eat(TokenType.FOR, 'Expecting FOR in for_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in for_stmt')
        var_def_node = VarDef(None, None)
        var_def_node.data_type = self.data_type()
        v_decl_node = VarDecl(var_def_node, None)
        self.vdecl_stmt(v_decl_node)
        for_stmt_node.var_decl = v_decl_node
        self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in for_stmt')
        for_stmt_node.condition = self.expr(Expr(False, None, None, None))
        self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in for_stmt')
        var_ref_node = VarRef(self.curr_token,None)
        self.eat(TokenType.ID, 'Expecting ID in for_stmt')
        assign_stmt_node = AssignStmt([], None)
        assign_stmt_node.lvalue.append(var_ref_node)
        self.assign_stmt(assign_stmt_node)
        for_stmt_node.assign_stmt = assign_stmt_node
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in for_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in for_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            for_stmt_node.stmts.append(self.stmt())
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in for_stmt')
        return for_stmt_node

    def call_expr(self, call_expr_node): #special does not deal with initial ID
        """Check for well-formed expression calls."""
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in call_expr')
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID,TokenType.NOT,TokenType.LPAREN]):
            call_expr_node.args.append(self.expr(Expr(False, None, None, None)))
            while self.match(TokenType.COMMA):
                self.advance()
                call_expr_node.args.append(self.expr(Expr(False, None, None, None)))
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in call_expr')

    def return_stmt(self):
        """Check for well-formed return statements."""
        return_stmt_node = ReturnStmt(None)
        self.eat(TokenType.RETURN, 'Expecting RETURN in return_stmt')
        return_stmt_node.expr = self.expr(Expr(False, None, None, None))
        return return_stmt_node

    def expr(self, expr_node):
        """Check for well-formed expressions."""
        #expr_node = Expr(None, None, None, None)
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID]):
            #simple_term_node = SimpleTerm(None)
            expr_node.first = SimpleTerm(self.rvalue())
            #self.rvalue()
        elif self.match(TokenType.NOT):
            self.advance()
            expr_node.not_op = True
            self.expr(expr_node)
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr_node_first = Expr(False, None, None, None)
            expr_node.first = ComplexTerm(self.expr(expr_node_first))
            self.eat(TokenType.RPAREN, 'Expecting RPAREN in expr')
        else:
            self.error('Expecting rvalue or NOT or LPAREN in expr')
        if self.is_bin_op():
            expr_node.op = self.curr_token
            expr_node_rest = Expr(False, None, None, None)
            self.bin_op()
            expr_node.rest = self.expr(expr_node_rest)
        return expr_node

    def bin_op(self):
        """Check for well-formed binary operations."""
        if self.is_bin_op():
            self.advance()

    def rvalue(self):
        """Check for well-formed right values."""
        r_value_node = RValue()
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL]):
            r_value_node = SimpleRValue(self.curr_token)
            self.base_rvalue()
        elif self.match(TokenType.NULL_VAL):
            r_value_node = SimpleRValue(self.curr_token)
            self.advance()
        elif self.match(TokenType.NEW):
            r_value_node = self.new_rvalue()
        elif self.match(TokenType.ID):
            id_token = self.curr_token
            self.advance()
            if self.match(TokenType.LPAREN):
                call_expr_node = CallExpr(id_token, [], None)
                self.call_expr(call_expr_node)
                r_value_node = call_expr_node
            else:
                var_r_value_node = VarRValue([])
                var_r_value_node.path.append(VarRef(id_token, None))
                self.var_rvalue(var_r_value_node)
                r_value_node = var_r_value_node
        else:
            self.error('Expecting base_rvalue or NULL_VAL or new_rvalue or ID in rvalue')
        return r_value_node

    def new_rvalue(self):
        """Check for well-formed new right values."""
        new_r_value_node = NewRValue(None, None, [])
        self.eat(TokenType.NEW, 'Expecting NEW in new_rvalue')
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            new_r_value_node.type_name = self.curr_token
            self.base_type()
            self.eat(TokenType.LBRACKET, 'Expecting LBRACKET in new_rvalue')
            new_r_value_node.array_expr = self.expr(Expr(False, None, None, None))
            new_r_value_node.struct_params = None
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in new_rvalue')
        elif self.match(TokenType.ID):
            new_r_value_node.type_name = self.curr_token
            self.advance()
            if self.match(TokenType.LPAREN):
                self.advance()
                if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID,TokenType.NOT,TokenType.LPAREN]):
                    #new_r_value_node.array_expr = self.expr(Expr(False, None, None, None))
                    new_r_value_node.struct_params.append(self.expr(Expr(False, None, None, None)))
                    while self.match(TokenType.COMMA):
                        self.advance()
                        new_r_value_node.struct_params.append(self.expr(Expr(False, None, None, None)))
                self.eat(TokenType.RPAREN, 'Expecting RPAREN in new_rvalue')
            elif self.match(TokenType.LBRACKET):
                self.advance()
                new_r_value_node.array_expr = self.expr(Expr(False, None, None, None))
                new_r_value_node.struct_params = None
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in new_rvalue')
            else:
                self.error('Expecting LPAREN or LBRACKET in new_rvalue')
        else:
            self.error('Expecting ID or base_type in new_rvalue')    
        return new_r_value_node

    def base_rvalue(self):
        """Check for well-formed base right values."""
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL]):
            self.advance()
        else:
            self.error('Expecting INT_VAL or DOUBLE_VAL or BOOL_VAL or STRING_VAL in base_rvalue')
    
    def var_rvalue(self, var_r_value_node): #special does not deal with initial ID
        """Check for well-formed variable right values."""
        if self.match(TokenType.LBRACKET):
            self.advance()
            var_r_value_node.path[0].array_expr = self.expr(Expr(False, None, None, None))
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in var_value')
        while self.match(TokenType.DOT):
            self.advance()
            var_ref_node = VarRef(self.curr_token, None)
            self.eat(TokenType.ID, 'Expecting ID in var_value')
            if self.match(TokenType.LBRACKET):
                self.advance()
                var_ref_node.array_expr = self.expr(Expr(False, None, None, None))
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in var_value')
            var_r_value_node.path.append(var_ref_node)
                
            
