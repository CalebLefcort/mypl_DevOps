"""The MyPL Lexer class.

NAME: <Caleb Lefcort>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mpl.mypl_token import *
from mpl.mypl_error import *


class Lexer:
    """For obtaining a token stream from a program."""

    def __init__(self, in_stream):
        """Create a Lexer over the given input stream.

        Args:
            in_stream -- The input stream. 

        """
        self.in_stream = in_stream
        self.line = 1
        self.column = 0


    def read(self):
        """Returns and removes one character from the input stream."""
        self.column += 1
        return self.in_stream.read_char()

    
    def peek(self):
        """Returns but doesn't remove one character from the input stream."""
        return self.in_stream.peek_char()

    
    def eof(self, ch):
        """Return true if end-of-file character"""
        return ch == ''

    
    def error(self, message, line, column):
        raise LexerError(f'{message} at line {line}, column {column}')

    
    def next_token(self):
        """Return the next token in the lexer's input stream."""
        #dictonary used to find keywords
        key_words = {
            'and' : TokenType.AND,
            'or' : TokenType.OR,
            'not' : TokenType.NOT,
            'int' : TokenType.INT_TYPE,
            'double' : TokenType.DOUBLE_TYPE,
            'string' : TokenType.STRING_TYPE,
            'bool' : TokenType.BOOL_TYPE,
            'void' : TokenType.VOID_TYPE,
            'true' : TokenType.BOOL_VAL,
            'false' : TokenType.BOOL_VAL,
            'struct' : TokenType.STRUCT,
            'array' : TokenType.ARRAY,
            'for' : TokenType.FOR,
            'while' : TokenType.WHILE,
            'if' : TokenType.IF,
            'elseif' : TokenType.ELSEIF,
            'else' : TokenType.ELSE,
            'new' : TokenType.NEW,
            'return' : TokenType.RETURN,
            'null' : TokenType.NULL_VAL
        }
        #read first char and set column for that char
        ch = self.read()
        col = self.column

        #finds keywords and IDs
        if ch.isalpha():
            while(self.peek().isalpha() or self.peek().isdigit() or self.peek() == '_'):
                ch += self.read()
            if(ch in key_words.keys()):
                return Token(key_words[ch], ch, self.line, col)
            else:
                return Token(TokenType.ID, ch, self.line, col)
        #finds ints and doubles
        elif ch.isdigit():
            if ch == '0' and self.peek().isdigit():
                raise LexerError("Leading 0")
            else:
                while(self.peek().isdigit()):
                    ch += self.read()
                if(self.peek() == '.'):
                    ch += self.read()
                    if(self.peek().isdigit()):
                        while(self.peek().isdigit()):
                            ch += self.read()
                        return Token(TokenType.DOUBLE_VAL, ch, self.line, col)
                    else:
                        raise LexerError("Missing double digit")
                else:
                    return Token(TokenType.INT_VAL, ch, self.line, col)
        #finds strings
        elif ch == '"':
            ch = ''
            while(self.peek() != '"'):
                if(self.peek() == '\n' or self.peek == ''):
                    raise LexerError('Non terminating string')
                else:
                    ch += self.read()
            self.read()
            return Token(TokenType.STRING_VAL, ch, self.line, col)
        #finds comments
        elif ch == '/' and self.peek() == '/':
            ch = self.read()
            ch = ''
            while(self.peek() != '\n' and self.peek() != ''):
                ch += self.read()
            return Token(TokenType.COMMENT, ch, self.line, col)
        #these deal with the simple tokens
        elif ch == '+':
            return Token(TokenType.PLUS, ch, self.line, col)
        elif ch == '-':
            return Token(TokenType.MINUS, ch, self.line, col)
        elif ch == '*':
            return Token(TokenType.TIMES, ch, self.line, col)
        elif ch == '/':
            return Token(TokenType.DIVIDE, ch, self.line, col)
        elif ch == '=' and self.peek() == '=':
            ch += self.read()
            return Token(TokenType.EQUAL, ch, self.line, col)
        elif ch == '.':
            return Token(TokenType.DOT, ch, self.line, col)
        elif ch == ',':
            return Token(TokenType.COMMA, ch, self.line, col)
        elif ch == '(':
            return Token(TokenType.LPAREN, ch, self.line, col)
        elif ch == ')':
            return Token(TokenType.RPAREN, ch, self.line, col)
        elif ch == '[':
            return Token(TokenType.LBRACKET, ch, self.line, col)
        elif ch == ']':
            return Token(TokenType.RBRACKET, ch, self.line, col)
        elif ch == ';':
            return Token(TokenType.SEMICOLON, ch, self.line, col)
        elif ch == '{':
            return Token(TokenType.LBRACE, ch, self.line, col)
        elif ch == '}':
            return Token(TokenType.RBRACE, ch, self.line, col)
        elif ch == '!' and self.peek() == '=':
            ch += self.read()
            return Token(TokenType.NOT_EQUAL, ch, self.line, col)
        elif ch == '<' and self.peek() == '=':
            ch += self.read()
            return Token(TokenType.LESS_EQ, ch, self.line, col)
        elif ch == '>' and self.peek() == '=':
            ch += self.read()
            return Token(TokenType.GREATER_EQ, ch, self.line, col)
        elif ch == '>':
            return Token(TokenType.GREATER, ch, self.line, col)
        elif ch == '<':
            return Token(TokenType.LESS, ch, self.line, col)
        elif ch == '=':
            return Token(TokenType.ASSIGN, ch, self.line, col)
        elif ch == '!':
            raise LexerError("Invalid not")
        #white space
        elif ch == '\n':
            self.line += 1
            self.column = 0
            return self.next_token()
        elif ch == ' ':
            return self.next_token()
        elif ch == '':
            return Token(TokenType.EOS, ch, self.line, col)
        #any other char
        else:
            raise LexerError("Invalid symbol")