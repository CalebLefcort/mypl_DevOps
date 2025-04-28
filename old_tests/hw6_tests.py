"""Unit tests for CPSC 326 HW-6. 

DISCLAIMER: These are basic tests that DO NOT guarantee correctness of
your code. As unit tests, each test is focused on an isolated part of
your overall solution. It is important that you also ensure your code
works over the example files provided and that you further test your
program beyond the test cases given. Grading of your work may also
involve the use of additional tests beyond what is provided in the
starter code.


NAME: S. Bowers
DATE: Spring 2024
CLASS: CPSC 326

"""

import pytest
import io

from mypl_error import *
from mypl_iowrapper import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast_parser import *
from mypl_var_table import *
from mypl_code_gen import *
from mypl_vm import *
from mypl_semantic_checker import *
from mypl_symbol_table import *


#----------------------------------------------------------------------
# VAR TABLE TESTS
#----------------------------------------------------------------------

def test_empty_var_table():
    table = VarTable()
    assert len(table) == 0

def test_var_table_push_pop():
    table = VarTable()
    assert len(table) == 0
    table.push_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0
    table.push_environment()
    table.push_environment()    
    assert len(table) == 2
    table.pop_environment()
    assert len(table) == 1
    table.pop_environment()
    assert len(table) == 0

def test_simple_var_table_add():
    table = VarTable()
    table.add('x')
    assert table.get('x') == None
    table.push_environment()
    table.add('x')
    assert table.get('x') == 0
    table.pop_environment()

def test_var_table_multiple_add():
    table = VarTable()
    table.push_environment()
    table.add('x')
    table.add('y')
    assert table.get('x') == 0
    assert table.get('y') == 1

def test_var_table_multiple_environments():
    table = VarTable()
    table.push_environment()
    table.add('x')
    table.add('y')
    table.push_environment()
    table.add('x')
    table.add('z')
    table.push_environment()
    table.add('u')
    assert table.get('x') == 2
    assert table.get('y') == 1
    assert table.get('z') == 3
    assert table.get('u') == 4
    table.pop_environment()
    assert table.get('x') == 2
    assert table.get('y') == 1
    assert table.get('z') == 3
    assert table.get('u') == None
    table.pop_environment()
    assert table.get('x') == 0
    assert table.get('y') == 1
    assert table.get('z') == None
    assert table.get('u') == None
    table.pop_environment()
    assert table.get('x') == None
    assert table.get('y') == None
    assert table.get('z') == None
    assert table.get('u') == None

    
#----------------------------------------------------------------------
# SIMPLE GETTING STARTED TESTS
#----------------------------------------------------------------------

# helper function to build and return a vm from the program string
def build(program):
    in_stream = FileWrapper(io.StringIO(program))
    lexer = Lexer(in_stream)
    parser = ASTParser(lexer)
    ast = parser.parse()
    visitor = SemanticChecker()
    ast.accept(visitor)
    vm = VM()
    codegen = CodeGenerator(vm)
    ast.accept(codegen)
    return vm


def test_empty_program(capsys):
    program = 'void main() {}'
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == ''

def test_simple_print(capsys):
    program = 'void main() {print("blue");}'
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
#----------------------------------------------------------------------
# BASIC VARIABLES AND ASSIGNMENT
#----------------------------------------------------------------------

def test_simple_var_decls(capsys):
    program = (
        'void main() { \n'
        '  int x1 = 3; \n'
        '  double x2 = 2.7; \n'
        '  bool x3 = true; \n'
        '  string x4 = "abc"; \n'
        '  print(x1); \n'
        '  print(x2); \n'
        '  print(x3); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '32.7trueabc'

def test_simple_var_decl_no_expr(capsys):
    program = (
        'void main() { \n'
        '  int x; \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_simple_var_assignments(capsys):
    program = (
        'void main() { \n'
        '  int x = 3; \n'
        '  print(x); \n'
        '  x = 4; \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '34'

#----------------------------------------------------------------------
# ARITHMETIC EXPRESSIONS
#----------------------------------------------------------------------

def test_simple_add(capsys):
    program = (
        'void main() { \n'
        '  int x = 4 + 5; \n'
        '  double y = 3.25 + 4.5; \n'
        '  string z = "ab" + "cd"; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '  print(" "); \n'        
        '  print(z); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '9 7.75 abcd'

def test_simple_sub(capsys):
    program = (
        'void main() { \n'
        '  int x = 6 - 5; \n'
        '  double y = 4.5 - 3.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '1 1.25'

def test_simple_mult(capsys):
    program = (
        'void main() { \n'
        '  int x = 4 * 3; \n'
        '  double y = 4.5 * 3.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '12 14.625'
    
def test_simple_div(capsys):
    program = (
        'void main() { \n'
        '  int x = 9 / 2; \n'
        '  double y = 4.5 / 1.25; \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4 3.6'

def test_longer_arithmetic_expr(capsys):
    program = (
        'void main() { \n'
        '  int x = 3 + (6 - 5) + (5 * 2) + (2 / 2); \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '15'
    
#----------------------------------------------------------------------
# BOOLEAN EXPRESSIONS
#----------------------------------------------------------------------

def test_simple_and(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = true and true; \n'
        '  bool x2 = true and false; \n'
        '  bool x3 = false and true; \n'        
        '  bool x4 = false and false; \n'        
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '  print(" "); \n'
        '  print(x3); \n'
        '  print(" "); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true false false false'

def test_simple_or(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = true or true; \n'
        '  bool x2 = true or false; \n'
        '  bool x3 = false or true; \n'        
        '  bool x4 = false or false; \n'        
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '  print(" "); \n'
        '  print(x3); \n'
        '  print(" "); \n'
        '  print(x4); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true true true false'

def test_simple_not(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = not true; \n'
        '  bool x2 = not false; \n'
        '  print(x1); \n'
        '  print(" "); \n'
        '  print(x2); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'false true'

def test_more_involved_logical_expression(capsys):
    program = (
        'void main() { \n'
        '  bool x = true or (true and false) or (false or (true and true)); \n'
        '  bool y = not ((not false) and (false or (true or false)) and true); \n'
        '  print(x); \n'
        '  print(" "); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'true false'
    

#----------------------------------------------------------------------
# COMPARISON OPERATORS
#----------------------------------------------------------------------

def test_true_numerical_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = 3 < 4; \n'
        '  bool x2 = 3 <= 4; \n'
        '  bool x3 = 3 <= 3; \n'
        '  bool x4 = 4 > 3; \n'
        '  bool x5 = 4 >= 3; \n'
        '  bool x6 = 3 >= 3; \n'
        '  bool x7 = 3 == 3; \n'
        '  bool x8 = 3 != 4; \n'
        '  print(x1 and x2 and x3 and x4 and x5 and x6 and x7 and x8); \n'
        '  bool y1 = 3.25 < 4.5; \n'
        '  bool y2 = 3.25 <= 4.5; \n'
        '  bool y3 = 3.25 <= 3.25; \n'
        '  bool y4 = 4.5 > 3.25; \n'
        '  bool y5 = 4.5 >= 3.25; \n'
        '  bool y6 = 3.25 >= 3.25; \n'
        '  bool y7 = 3.25 == 3.25; \n'
        '  bool y8 = 3.25 != 4.5; \n'
        '  print(y1 and y2 and y3 and y4 and y5 and y6 and y7 and y8); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'truetrue'

def test_false_numerical_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = 4 < 3; \n'
        '  bool x2 = 4 <= 3; \n'
        '  bool x3 = 3 > 4; \n'
        '  bool x4 = 3 >= 4; \n'
        '  bool x5 = 3 == 4; \n'
        '  bool x6 = 3 != 3; \n'
        '  print(x1 or x2 or x3 or x4 or x5 or x6); \n'
        '  bool y1 = 4.5 < 3.25; \n'
        '  bool y2 = 4.5 <= 3.25; \n'
        '  bool y3 = 3.25 > 4.5; \n'
        '  bool y4 = 3.25 >= 4.5; \n'
        '  bool y5 = 3.25 == 4.5; \n'
        '  bool y6 = 3.25 != 3.25; \n'
        '  print(y1 or y2 or y3 or y4 or y5 or y6); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalse'

def test_true_alphabetic_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = "a" < "b"; \n'
        '  bool x2 = "a" <= "b"; \n'
        '  bool x3 = "a" <= "a"; \n'
        '  bool x4 = "b" > "a"; \n'
        '  bool x5 = "b" >= "a"; \n'
        '  bool x6 = "a" >= "a"; \n'
        '  bool x7 = "a" == "a"; \n'
        '  bool x8 = "a" != "b"; \n'
        '  print(x1 and x2 and x3 and x4 and x5 and x6 and x7 and x8); \n'
        '  bool y1 = "aa" < "ab"; \n'
        '  bool y2 = "aa" <= "ab"; \n'
        '  bool y3 = "aa" <= "aa"; \n'
        '  bool y4 = "ab" > "aa"; \n'
        '  bool y5 = "ab" >= "aa"; \n'
        '  bool y6 = "aa" >= "aa"; \n'
        '  bool y7 = "aa" == "aa"; \n'
        '  bool y8 = "aa" != "ab"; \n'
        '  print(y1 and y2 and y3 and y4 and y5 and y6 and y7 and y8); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'truetrue'
  
def test_false_alphabetic_comparisons(capsys):
    program = (
        'void main() { \n'
        '  bool x1 = "b" < "a"; \n'
        '  bool x2 = "b" <= "a"; \n'
        '  bool x3 = "a" > "b"; \n'
        '  bool x4 = "a" >= "b"; \n'
        '  bool x5 = "a" == "b"; \n'
        '  bool x6 = "a" != "a"; \n'
        '  print(x1 or x2 or x3 or x4 or x5 or x6); \n'
        '  bool y1 = "ab" < "aa"; \n'
        '  bool y2 = "ab" <= "aa"; \n'
        '  bool y3 = "aa" > "ab"; \n'
        '  bool y4 = "aa" >= "ab"; \n'
        '  bool y5 = "aa" == "ab"; \n'
        '  bool y6 = "aa" != "aa"; \n'
        '  print(y1 or y2 or y3 or y4 or y5 or y6); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalse'
  
def test_null_comparisons(capsys):
    program = (
        'void main() { \n'
        '  int a = 3; \n'
        '  double b = 2.75; \n'
        '  string c = "abc"; \n'
        '  bool d = false; \n'
        '  print(null != null); \n'
        '  print((a == null) or (b == null) or (c == null) or (d == null)); \n'
        '  print((null == a) or (null == b) or (null == c) or (null == d)); \n'
        '  print(" "); \n'
        '  print(null == null); \n'
        '  print((a != null) and (b != null) and (c != null) and (d != null)); \n'
        '  print((null != a) and (null != b) and (null != c) and (null != d)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsefalse truetruetrue'

    
#----------------------------------------------------------------------
# WHILE LOOPS
#----------------------------------------------------------------------

def test_basic_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 5) { \n'
        '    i = i + 1;'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '5'
    
def test_more_involved_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 7) { \n'
        '    int j = i * 2; \n'
        '    print(j); \n'
        '    print(" "); \n'
        '    i = i + 1;'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '0 2 4 6 8 10 12 7'

def test_nested_while(capsys):
    program = (
        'void main() { \n'
        '  int i = 0; \n'
        '  while (i < 5) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '    int j = 0; \n'
        '    while (j < i) { \n'
        '      print(j); \n'
        '      print(" "); \n'
        '      j = j + 1; \n'
        '    } \n'
        '    i = i + 1;'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 0 2 0 1 3 0 1 2 4 0 1 2 3 '

#----------------------------------------------------------------------
# FOR LOOPS
#----------------------------------------------------------------------

def test_basic_for(capsys):
    program = (
        'void main() { \n'
        '  for (int i = 0; i < 5; i = i + 1) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 2 3 4 '

def test_nested_for(capsys):
    program = (
        'void main() { \n'
        '  int x = 0; \n'
        '  for (int i = 1; i <= 5; i = i + 1) { \n'
        '    for (int j = 1; j <= 4; j = j + 1) { \n'
        '      x = x + (i * j); \n'
        '    } \n'
        '  } \n'
        '  print(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '150'

def test_for_outer_non_bad_shadowing(capsys):
    program = (
        'void main() { \n'
        '  int i = 32; \n'
        '  for (int i = 0; i < 5; i = i + 1) { \n'
        '    print(i); \n'
        '    print(" "); \n'
        '  } \n'
        '  print(i); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 2 3 4 32'

#----------------------------------------------------------------------
# IF STATEMENTS
#----------------------------------------------------------------------

def test_just_an_if(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (true) { \n'
        '    print(1); \n'
        '  } \n'
        '  print("-"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-1-'
    
def test_consecutive_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (3 < 4) { \n'
        '    print(1); \n'
        '  } \n'
        '  if (true) { \n'
        '    print(2); \n'
        '  } \n'
        '  if (3 > 4) { \n'
        '    print(3); \n'
        '  } \n'
        '  print("-"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-12-'

def test_simple_else_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (3 < 4) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (4 > 3) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  if (4 < 3) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (3 < 4) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  if (4 < 3) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (3 != 3) { \n'
        '    print(2); \n'
        '  } \n'
        '  else { \n'
        '    print(3); \n'
        '  } \n'
        '  print("-"); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-123-'

def test_many_else_ifs(capsys):
    program = (
        'void main() { \n'
        '  print("-"); \n'
        '  if (false) { \n'
        '    print(1); \n'
        '  } \n'
        '  elseif (false) { \n'
        '    print(2); \n'
        '  } \n'
        '  elseif (true) { \n'
        '    print(3); \n'
        '  } \n'
        '  elseif (true) { \n'
        '    print(4); \n'
        '  } \n'
        '  else { \n'
        '    print(5); \n'
        '  } \n'
        '  print("-"); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '-3-'
    

#----------------------------------------------------------------------
# FUNCTION CALLS
#----------------------------------------------------------------------

def test_no_arg_call(capsys):
    program = (
        'void f() {} \n'
        'void main() { \n'
        '  print(f()); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'null'

def test_one_arg_call(capsys):
    program = (
        'int f(int x) {return x;} \n'
        'void main() { \n'
        '  print(f(3)); \n'
        '  print(f(4)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '34'
    
def test_two_arg_call(capsys):
    program = (
        'int f(int x, int y) {return x * y;} \n'
        'void main() { \n'
        '  print(f(3, 2)); \n'
        '  print(f(5, 6)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '630'

def test_three_arg_call(capsys):
    program = (
        'int f(int x, int y, int z) {return (x * y) - z;} \n'
        'void main() { \n'
        '  print(f(3, 2, 4)); \n'
        '  print(f(5, 6, 10)); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '220'

def test_multi_level_call(capsys):
    program = (
        'string f(string s) {return s + "!";} \n'
        'string g(string s1, string s2) {return f(s1 + s2);} \n'
        'string h(string s1, string s2, string s3) {return g(s1, s2) + f(s3);} \n'
        'void main() { \n'
        '  print(h("red", "blue", "green")); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'redblue!green!'

def test_basic_recursion(capsys):
    program = (
        'int non_negative_sum(int x) { \n'
        '  if (x <= 0) {return 0;} \n'
        '  return x + non_negative_sum(x-1); \n'
        '} \n'

        'void main() { \n'
        '  print(non_negative_sum(0)); \n'
        '  print(" "); \n'
        '  print(non_negative_sum(1)); \n'
        '  print(" "); \n'
        '  print(non_negative_sum(10)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 1 55'

def test_fib_recursion(capsys):
    program = (
        'int fib(int n) { \n'
        '  if (n < 0) {return null;} \n'
        '  if (n == 0) {return 0;} \n'
        '  if (n == 1) {return 1;} \n'
        '  return fib(n-1) + fib(n-2); \n'
        '}\n'
        'void main() { \n'
        '  print(fib(8)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '21'

#----------------------------------------------------------------------
# STRUCTS
#----------------------------------------------------------------------

def test_empty_struct(capsys):
    program = (
        'struct T {} \n'
        'void main() { \n'
        '  T t = new T(); \n'
        '  print(t); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024'

def test_simple_one_field_struct(capsys):
    program = (
        'struct T {int x;} \n'
        'void main() { \n'
        '  T t = new T(3); \n'
        '  print(t.x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3'

def test_simple_two_field_struct(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t = new T(3, true); \n'
        '  print(t.x); \n'
        '  print(" "); \n'
        '  print(t.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3 true'

def test_simple_assign_field(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t = new T(3, true); \n'
        '  t.x = t.x + 1; \n'
        '  t.y = not t.y; \n'
        '  print(t.x); \n'
        '  print(" "); \n'
        '  print(t.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '4 false'

def test_simple_struct_assign(capsys):
    program = (
        'struct T {int x; bool y;} \n'
        'void main() { \n'
        '  T t1 = new T(3, true); \n'
        '  T t2 = t1; \n'
        '  T t3; \n'
        '  t3 = t2; \n'
        '  t1.x = t1.x + 1; \n'
        '  print(t1.x); \n'
        '  print(" "); \n'
        '  print(t1.y); \n'
        '  print(" "); \n'
        '  print(t2.x); \n'
        '  print(" "); \n'
        '  print(t2.y); \n'
        '  print(" "); \n'        
        '  print(t3.x); \n'
        '  print(" "); \n'
        '  print(t3.y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '4 true 4 true 4 true'

def test_simple_two_structs(capsys):
    program = (
        'struct T1 {int val; T2 t2;} \n'
        'struct T2 {int val; T1 t1;} \n'
        'void main() { \n'
        '  T1 x = new T1(3, null); \n'
        '  T2 y = new T2(4, x); \n'
        '  x.t2 = y; \n'
        '  print(x.val); \n'
        '  print(" "); \n'
        '  print(x.t2.val); \n'
        '  print(" "); \n'
        '  print(y.val); \n'
        '  print(" "); \n'
        '  print(y.t1.val); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3 4 4 3'
    
def test_recursive_struct(capsys):
    program = (
        'struct Node {int val; Node next;} \n'
        'void main() { \n'
        '  Node r = new Node(10, null); \n'
        '  r.next = new Node(20, null); \n'
        '  r.next.next = new Node(30, null); \n'
        '  print(r); \n'
        '  print(" "); \n'
        '  print(r.val); \n'
        '  print(" "); \n'
        '  print(r.next); \n'
        '  print(" "); \n'
        '  print(r.next.val); \n'
        '  print(" "); \n'        
        '  print(r.next.next); \n'
        '  print(" "); \n'        
        '  print(r.next.next.val); \n'
        '  print(" "); \n'        
        '  print(r.next.next.next); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 10 2025 20 2026 30 null'

def test_struct_as_fun_param(capsys):
    program = (
        'struct Node {int val; Node next;} \n'
        'int val(Node n) {print(n); print(" "); return n.val;} \n'
        'void main() { \n'
        '  Node r = new Node(24, null); \n'
        '  print(val(r)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 24'

#----------------------------------------------------------------------
# ARRAYS
#----------------------------------------------------------------------

def test_simple_array_creation(capsys):
    program = (
        'void main() { \n'
        '  array int xs = new int[5]; \n'
        '  print(xs); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024'

def test_simple_array_access(capsys):
    program = (
        'void main() { \n'
        '  array int xs = new int[2]; \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'
        '  print(xs[1]); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'null null'

def test_array_init(capsys):
    program = (
        'void main() { \n'
        '  array bool xs = new bool[3]; \n'
        '  xs[0] = false; \n'
        '  xs[1] = true; \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'
        '  print(xs[1]); \n'
        '  print(" "); \n'
        '  print(xs[2]); \n'        
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'false true null'

def test_array_of_struct(capsys):
    program = (
        'struct T {bool x; int y;} \n'
        'void main() { \n'
        '  array T xs = new T[3]; \n'
        '  xs[0] = new T(true, 24); \n'
        '  xs[1] = new T(false, 48); \n'
        '  print(xs); \n'
        '  print(" "); \n'
        '  print(xs[0]); \n'
        '  print(" "); \n'        
        '  print(xs[0].x); \n'
        '  print(" "); \n'        
        '  print(xs[0].y); \n'
        '  print(" "); \n'        
        '  print(xs[1]); \n'
        '  print(" "); \n'        
        '  print(xs[1].x); \n'
        '  print(" "); \n'        
        '  print(xs[1].y); \n'
        '  print(" "); \n'        
        '  print(xs[2]); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 2025 true 24 2026 false 48 null'

def test_update_array_of_struct(capsys):
    program = (
        'struct T {bool x; int y;} \n'
        'void main() { \n'
        '  array T xs = new T[2]; \n'
        '  xs[0] = new T(true, 24); \n'
        '  xs[1] = new T(false, 48); \n'
        '  xs[0].x = not xs[0].x; \n'
        '  xs[0].y = xs[0].y + 1; \n'
        '  xs[1].x = not xs[1].x; \n'
        '  xs[1].y = xs[1].y + 1; \n'
        '  print(xs[0].y); \n'
        '  print(" "); \n'        
        '  print(xs[0].x); \n'
        '  print(" "); \n'        
        '  print(xs[1].y); \n'
        '  print(" "); \n'        
        '  print(xs[1].x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '25 false 49 true'

def test_update_path_ending_in_array(capsys):
    program = (
        'struct Node {int val; array Node next;} \n'
        'void main() { \n'
        '  Node n = new Node(20, new Node[2]); \n'
        '  n.next[0] = new Node(10, new Node[1]); \n'
        '  n.next[1] = new Node(30, null); \n'
        '  n.next[0].next[0] = new Node(5, null); \n'
        '  print(n.val); \n'
        '  print(" "); \n'        
        '  print(n.next[0].val); \n'
        '  print(" "); \n'        
        '  print(n.next[1].val); \n'
        '  print(" "); \n'        
        '  print(n.next[0].next[0].val); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '20 10 30 5'

def test_array_as_param(capsys):
    program = (
        'bool val(array bools xs, int index) { \n'
        '  print(xs); \n'
        '  print(" "); \n'
        '  return xs[index]; \n'
        '} \n'
        'void main() { \n'
        '  array bool xs = new bool[5]; \n'
        '  xs[0] = true; \n'
        '  print(val(xs, 0)); \n'
        '  print(" "); \n'
        '  xs[1] = false; \n'
        '  print(val(xs, 1)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2024 true 2024 false'
    
    
#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

def test_simple_to_str(capsys):
    program = (
        'void main() { \n'
        '  print(itos(24)); \n'
        '  print(" "); \n'
        '  print(dtos(3.14)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '24 3.14'

def test_simple_to_int(capsys):
    program = (
        'void main() { \n'
        '  print(stoi("24")); \n'
        '  print(" "); \n'
        '  print(dtoi(3.14)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '24 3'
    
def test_simple_to_double(capsys):
    program = (
        'void main() { \n'
        '  print(stod("3.14")); \n'
        '  print(" "); \n'
        '  print(itod(3)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '3.14 3.0'

def test_string_length(capsys):
    program = (
        'void main() { \n'
        '  print(length("")); \n'
        '  print(" "); \n'
        '  print(length("abcdefg")); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 7'

def test_array_length(capsys):
    program = (
        'void main() { \n'
        '  print(length(new int[0])); \n'
        '  print(" "); \n'
        '  print(length(new int[7])); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '0 7'
    
def test_string_get(capsys):
    program = (
        'void main() { \n'
        '  string s = "bluegreen"; \n'
        '  for (int i = 0; i < length(s); i = i + 1) { \n'
        '    print(get(i, s)); \n'
        '    print(" "); \n'
        '  } \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'b l u e g r e e n '
    


#----------------------------------------------------------------------
# TODO: Add at least 10 of your own tests below. Half of the tests
# should be positive tests, and half should be negative. Focus on
# trickier parts of your code (e.g., rvalues, lvalues, new rvalues)
# looking for places in your code that are not tested by the above.
#----------------------------------------------------------------------

