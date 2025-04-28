"""MyPL simple syntax checker (parser) implementation.

NAME: <Caleb Lefcort>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *


class SimpleParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser."""
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def()
            else:
                self.fun_def()
        self.eat(TokenType.EOS, 'expecting EOF')

        
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
        """Returns true if the current token is a binary operation token."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)

    
    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------
        
    def struct_def(self):
        """Check for well-formed struct definition."""
        self.eat(TokenType.STRUCT, 'expecting STRUCT in struct_def')
        self.eat(TokenType.ID, 'expecting ID in struct_def')
        self.eat(TokenType.LBRACE, 'expecting LBRACE in struct_def')
        self.fields()
        self.eat(TokenType.RBRACE, 'expecting RBRACE in struct_def')
        
    def fields(self):
        """Check for well-formed struct fields."""
        while self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            self.data_type()
            self.eat(TokenType.ID, 'expecting ID in fields')
            self.eat(TokenType.SEMICOLON, 'expecting SEMICOLON in fields')
            
    def fun_def(self):
        """Check for well-formed function definition."""
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            self.data_type()
        elif self.match(TokenType.VOID_TYPE):
            self.advance()
        else:
            self.error('Expecting data_type or VOID_TYPE in fun_def')
        self.eat(TokenType.ID,'Expecting ID in fun_def')
        self.eat(TokenType.LPAREN,'Expecting LPAREN in fun_def')
        self.params()
        self.eat(TokenType.RPAREN,'Expecting RPAREN in fun_def')
        self.eat(TokenType.LBRACE,'Expecting LBRACE in fun_def')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE,TokenType.DOUBLE_TYPE,TokenType.BOOL_TYPE,TokenType.STRING_TYPE,TokenType.ID,TokenType.ARRAY,]):
            self.stmt()
        self.eat(TokenType.RBRACE,'Expecting RBRACE in fun_def')

    def params(self):
        """Check for well-formed function formal parameters."""
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            self.data_type()
            self.eat(TokenType.ID,'Expecting ID in params')
            while self.match(TokenType.COMMA):
                self.advance()
                self.data_type()
                self.eat(TokenType.ID,'Expecting ID in params')

    def data_type(self):
        """Check for well-formed data types."""
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
             self.base_type()
        elif self.match(TokenType.ID):
            self.advance()
        elif self.match(TokenType.ARRAY):
            self.advance()
            if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
                self.base_type()
            elif self.match(TokenType.ID):
                self.advance()
            else:
                self.error('Expecting base_type or ID in data_type')
        else:
            self.error('Expecting base_type or ID or ARRAY in data_type')

    def base_type(self):
        """Check for well-formed base types."""
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            self.advance()
        else:
            self.error('Expecting INT_TYPE or DOUBLE_TYPE or BOOL_TYPE or STRING_TYPE in base_type')

    def stmt(self):
        """Check for well-formed statements."""
        if self.match(TokenType.WHILE):
            self.while_stmt()
        elif self.match(TokenType.IF):
            self.if_stmt()
        elif self.match(TokenType.FOR):
            self.for_stmt()
        elif self.match(TokenType.RETURN):
            self.return_stmt()
            self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
        elif self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY]):
            self.data_type()
            self.vdecl_stmt()
            self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
        elif self.match(TokenType.ID):
            self.advance()
            if self.match(TokenType.ID):
                self.vdecl_stmt()
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            elif self.match_any([TokenType.LBRACKET, TokenType.DOT, TokenType.ASSIGN]):
                self.assign_stmt()
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            elif self.match(TokenType.LPAREN):
                self.call_expr()
                self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in stmt')
            else:
                self.error('Expecting vdecl_stmt or assign_stmt or call_expr in stmt')
        else:
            self.error('Expecting while_stmt or if_stmt or for_stmt or return_stmt or vdecl_stmt or assign_stmt or call_expr in stmt')
        
    def vdecl_stmt(self): #special does not deal with initial data_type
        """Check for well-formed variable declarations."""
        self.eat(TokenType.ID, 'Expecting ID in vdecl_stmt')
        if self.match(TokenType.ASSIGN):
            self.advance()
            self.expr() 

    def assign_stmt(self):
        """Check for well-formed assignment statements."""
        self.lvalue()
        self.eat(TokenType.ASSIGN, 'Expecting ASSIGN in assign_stmt')
        self.expr()


    def lvalue(self): #special does not deal with initial ID
        """Check for well-formed left values."""
        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in lvalue')
        while self.match(TokenType.DOT):
            self.advance()
            self.eat(TokenType.ID, 'Expecting ID in lvalue')
            if self.match(TokenType.LBRACKET):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in lvalue')
    
    def if_stmt(self):
        """Check for well-formed if statements."""
        self.eat(TokenType.IF, 'Expecting IF in if_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in if_stmt')
        self.expr()
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in if_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            self.stmt()
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt')
        self.if_stmt_t()
    
    def if_stmt_t(self):
        """Check for well-formed if statement tails."""
        if self.match(TokenType.ELSEIF):
            self.advance()
            self.eat(TokenType.LPAREN, 'Expecting LPAREN in if_stmt_t')
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting RPAREN in if_stmt_t')
            self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt_t')
            while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
                self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt_t')
            self.if_stmt_t()
        elif self.match(TokenType.ELSE):
            self.advance()
            self.eat(TokenType.LBRACE, 'Expecting LBRACE in if_stmt_t')
            while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
                self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting RBRACE in if_stmt_t')

    def while_stmt(self):
        """Check for well-formed while statements."""
        self.eat(TokenType.WHILE, 'Expecting WHILE in while_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in while_stmt')
        self.expr()
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in while_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in while_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            self.stmt()
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in while_stmt')   

    def for_stmt(self):
        """Check for well-formed for statements."""
        self.eat(TokenType.FOR, 'Expecting FOR in for_stmt')
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in for_stmt')
        self.data_type()
        self.vdecl_stmt()
        self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in for_stmt')
        self.expr()
        self.eat(TokenType.SEMICOLON, 'Expecting SEMICOLON in for_stmt')
        self.eat(TokenType.ID, 'Expecting ID in for_stmt')
        self.assign_stmt()
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in for_stmt')
        self.eat(TokenType.LBRACE, 'Expecting LBRACE in for_stmt')
        while self.match_any([TokenType.WHILE,TokenType.IF,TokenType.FOR,TokenType.RETURN,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY,TokenType.ID]):
            self.stmt()
        self.eat(TokenType.RBRACE, 'Expecting RBRACE in for_stmt')  

    def call_expr(self): #special does not deal with initial ID
        """Check for well-formed expression calls."""
        self.eat(TokenType.LPAREN, 'Expecting LPAREN in call_expr')
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID,TokenType.NOT,TokenType.LPAREN]):
            self.expr()
            while self.match(TokenType.COMMA):
                self.advance()
                self.expr()
        self.eat(TokenType.RPAREN, 'Expecting RPAREN in call_expr')

    def return_stmt(self):
        """Check for well-formed return statements."""
        self.eat(TokenType.RETURN, 'Expecting RETURN in return_stmt')
        self.expr()

    def expr(self):
        """Check for well-formed expressions."""
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID]):
            self.rvalue()
        elif self.match(TokenType.NOT):
            self.advance()
            self.expr()
        elif self.match(TokenType.LPAREN):
            self.advance()
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting RPAREN in expr')
        else:
            self.error('Expecting rvalue or NOT or LPAREN in expr')
        if self.is_bin_op():
            self.bin_op()
            self.expr()

    def bin_op(self):
        """Check for well-formed binary operations."""
        if self.is_bin_op():
            self.advance()

    def rvalue(self):
        """Check for well-formed right values."""
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL]):
            self.base_rvalue()
        elif self.match(TokenType.NULL_VAL):
            self.advance()
        elif self.match(TokenType.NEW):
            self.new_rvalue()
        elif self.match(TokenType.ID):
            self.advance()
            if self.match(TokenType.LPAREN):
                self.call_expr()
            else:
                self.var_rvalue()
        else:
            self.error('Expecting base_rvalue or NULL_VAL or new_rvalue or ID in rvalue')

    def new_rvalue(self):
        """Check for well-formed new right values."""
        self.eat(TokenType.NEW, 'Expecting NEW in new_rvalue')
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            self.base_type()
            self.eat(TokenType.LBRACKET, 'Expecting LBRACKET in new_rvalue')
            self.expr()
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in new_rvalue')
        elif self.match(TokenType.ID):
            self.advance()
            if self.match(TokenType.LPAREN):
                self.advance()
                if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL,TokenType.NULL_VAL,TokenType.NEW,TokenType.ID,TokenType.NOT,TokenType.LPAREN]):
                    self.expr()
                    while self.match(TokenType.COMMA):
                        self.advance()
                        self.expr()
                self.eat(TokenType.RPAREN, 'Expecting RPAREN in new_rvalue')
            elif self.match(TokenType.LBRACKET):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in new_rvalue')
            else:
                self.error('Expecting LPAREN or LBRACKET in new_rvalue')
        else:
            self.error('Expecting ID or base_type in new_rvalue')

    def base_rvalue(self):
        """Check for well-formed base right values."""
        if self.match_any([TokenType.INT_VAL,TokenType.DOUBLE_VAL,TokenType.BOOL_VAL,TokenType.STRING_VAL]):
            self.advance()
        else:
            self.error('Expecting INT_VAL or DOUBLE_VAL or BOOL_VAL or STRING_VAL in base_rvalue')
    
    def var_rvalue(self): #special does not deal with initial ID
        """Check for well-formed variable right values."""
        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in var_value')
        while self.match(TokenType.DOT):
            self.advance()
            self.eat(TokenType.ID, 'Expecting ID in var_value')
            if self.match(TokenType.LBRACKET):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting RBRACKET in var_value')
        





        
        
