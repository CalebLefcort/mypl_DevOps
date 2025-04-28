"""Unit tests for CPSC 326 HW-2. 

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


#----------------------------------------------------------------------
# Positive Test Cases
#----------------------------------------------------------------------

# Basic Tests

def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_empty_struct():
    in_stream = FileWrapper(io.StringIO('struct s {}'))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_empty_function():
    in_stream = FileWrapper(io.StringIO('void f() {}'))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic Struct Tests
    
def test_struct_with_base_type_fields():
    s = ('struct my_struct {'
         '  int x1;'
         '  double x2;'
         '  bool x3;'
         '  string x5;'
         '}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_struct_with_non_base_type_fields():
    s = ('struct my_struct {'
         '  array int x1;'
         '  my_struct x2;'
         '  array my_struct x3;'
         '}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic Function Tests

def test_function_base_value_return_type():
    in_stream = FileWrapper(io.StringIO('int my_fun() {}'))
    p = ASTParser(Lexer(in_stream))
    p.parse()
    
def test_function_non_base_value_return_type():
    s = ('my_struct my_fun() {}'
         'array int my_fun() {}'
         'array my_struct my_fun() {}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_function_one_base_type_param():
    in_stream = FileWrapper(io.StringIO('void my_fun(int x) {}'))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_function_one_non_base_type_param():
    s = ('void my_fun(my_struct first_arg) {}'
         'void my_fun(array int first_arg) {}'
         'void my_fun(array my_struct first_arg) {}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_function_with_base_type_params():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x1, double x2, string x3, bool x4) {}'
    )) 
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_function_with_non_base_type_params():
    in_stream = FileWrapper(io.StringIO(
        'void f(s x1, array int x2, array s x3) {}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic Return Test

def test_return():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  return 10;'
        '  return null;'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()
    
# Basic variable declaration tests
    
def test_var_decls_not_initialized():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  int x1;'
        '  double x2;'
        '  bool x3;'
        '  string x4;'
        '  MyType x5;'
        '  array int x1;'
        '  array double x2;'
        '  array bool x3;'
        '  array string x4;'
        '  array MyType x5;'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_var_decls_initialized():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  int x1 = 42;'
        '  double x2 = 3.14;'
        '  bool x3 = false;'
        '  string x4 = "";'
        '  MyType x5 = null;'
        '  array int x1 = new int[10];'
        '  array double x2 = new double[100];'
        '  array bool x3 = new bool[20];'
        '  array string x4 = new string[1];'
        '  array MyType x5 = null;'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()
    
# Basic if statement tests

def test_if_simple():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  if (true) {}'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()


def test_if_full():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  if (true) {x = 1;}'
        '  elseif (false) {x = 2;}'
        '  elseif (true) {x = 3;}'
        '  else {x = 4;}'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic loop statement tests

def test_for_simple():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  for (int i = 0; i < 10; i = i + 1) {'
        '    x = x + 1;'
        '  }'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()


def test_while_simple():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  while (i < 10) {'
        '    x = x + 1;'
        '  }'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic path expression tests

def test_path_expressions(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  a.b.c = 0;'
        '  x = a.b.c;'
        '  xs[0] = 5;'
        '  x = xs[1];'
        '  y = xs[0].att1.att2[y].att3;'
        '  xs[1].att1.att2[0].att3 = 3;'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic function call tests

def test_function_calls(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  z = f();'
        '  z = f(x);'
        '  z = f(x, y);'
        '  z = f(x, y, z);'
        '  f(); f(x); f(x,y); f(x,y,z);'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()


# Basic logical expression tests

def test_logical_expressions(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  z = x and y or true and not false;'
        '  z = not (x and y) and not ((x and z) or y);'
        '  z = (x or not y) and (not x or y) and not not (true or true or false);'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic relational expression tests

def test_relational_expressions(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  z = x == y or (x < y) or (x != y) or (x > y);'
        '  z = not (z or x < y or x > y) and ((x == y) or (x != y));'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic arithmetic expression tests

def test_arithmetic_expressions(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  z = x + y - z * u / v;'
        '  z = ((x + y) / (x - y) + z) / (x * (x - y));'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic new expression tests

def test_new_expressions(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  my_struct x = new my_struct(a, b);'
        '  my_struct x = new my_struct();'
        '  my_array xs = new int[10];'
        '  my_array xs = new int[z * (z - 1)];'
        '  array my_struct zs = new my_struct[z + 1];'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic nested statement test

def test_nested_statetements(): 
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  if (odd(x)) {'
        '    while (true) {'
        '      for (int i = 0; i < x; i = i + 1) {'
        '        x = x + 2 + g(x + z);'
        '      }'
        '    }'
        '  }'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

# Basic mix of statements

def test_mix_of_statetements(): 
    in_stream = FileWrapper(io.StringIO(
        'bool my_fun(int z) {'
        '  int x = 1;'
        '  x = 2;'
        '  if (odd(x)) {return true;}'
        '  while (true) {x = x + 1;}'
        '  for (int i = 0; i < x; i = i + 1) {'
        '    x = x + 2;'
        '  }'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_mix_of_structs_and_functions(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x;}'
        'void f1() {}'
        'struct S2 {int y; double z;}'
        'int f2(S1 s1, S2 s2) {return s1.x + s2.y;}'
        'string f3() {}'
        'struct S3 {}'
        'void main() {}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()
    

    
# TODO: Add at least 5 of your own "positive" expression tests below:

def test_if_complex_condition():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  if (not (x and y) and not ((x and z) or y)) {}'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_struct_followed_by_function():
    s = ('struct my_struct {'
         '  int x1;'
         '}'
         'int my_fun() {}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_function_followed_by_struct():
    s = ('int my_fun() {}'
         'struct my_struct {'
         '  int x1;'
         '}')
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()

def test_nested_if_statments():
    s = ('int my_fun() {'
         'if (x > 0){'
         '  if(x > 5){'
         '      if (x < 7){}'
         '  }'
         '}'
        '}'
         )
    in_stream = FileWrapper(io.StringIO(s))
    p = ASTParser(Lexer(in_stream))
    p.parse()
    
def test_return_function_call():
    in_stream = FileWrapper(io.StringIO(
        'void f() {'
        '  return square(x);'
        '}'
    ))
    p = ASTParser(Lexer(in_stream))
    p.parse()
#------------------------------------------------------------
# Negative Test Cases
#------------------------------------------------------------

# Basic Tests

def test_statement_outside_function_or_struct():
    in_stream = FileWrapper(io.StringIO('int x1 = 0;'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_not_struct_or_function_braces():
    in_stream = FileWrapper(io.StringIO('{ }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

    
# Basic Struct Tests
    
def test_missing_struct_id():
    in_stream = FileWrapper(io.StringIO('struct {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_missing_struct_open_brace():
    in_stream = FileWrapper(io.StringIO('struct s int x;'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_missing_struct_close_brace():
    in_stream = FileWrapper(io.StringIO('struct s { int x;'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_missing_data_type_field():
    in_stream = FileWrapper(io.StringIO('struct s {x; int y;}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_missing_field_id():
    in_stream = FileWrapper(io.StringIO('struct s {int x; int;}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_last_field_with_missing_semicolon():
    in_stream = FileWrapper(io.StringIO('struct s {int x; int y}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_first_field_with_missing_semicolon():
    in_stream = FileWrapper(io.StringIO('struct s {int x int y;}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

# Basic Function Tests

def test_missing_function_return_type():
    in_stream = FileWrapper(io.StringIO('f() {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_open_paren():
    in_stream = FileWrapper(io.StringIO('void f ) {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_close_paren():
    in_stream = FileWrapper(io.StringIO('void f( {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_open_barce():
    in_stream = FileWrapper(io.StringIO('void f() }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_close_barce():
    in_stream = FileWrapper(io.StringIO('void f() {'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_param_type():
    in_stream = FileWrapper(io.StringIO('void f(x, int y) {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_function_param_id():
    in_stream = FileWrapper(io.StringIO('void f(int x, int) {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_too_many_commas_in_function_params():
    in_stream = FileWrapper(io.StringIO('void f(int x, int y, ) {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_too_few_commas_in_function_params():
    in_stream = FileWrapper(io.StringIO('void f(int x int y) {}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

# Return

def test_return_without_expr():
    in_stream = FileWrapper(io.StringIO('void f() { return; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_return_without_semicolon():
    in_stream = FileWrapper(io.StringIO('void f() { return null }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
# Basic Variable Declaration Tests

def test_multiple_vars_in_var_def():
    in_stream = FileWrapper(io.StringIO('void f() { int x x = 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_no_vars_in_var_def():
    in_stream = FileWrapper(io.StringIO('void f() { int = 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_assign_in_var_def():
    in_stream = FileWrapper(io.StringIO('void f() { int x 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_val_in_var_def():
    in_stream = FileWrapper(io.StringIO('void f() { bool y = ;}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

    
def test_missing_semi_in_var_decl():
    in_stream = FileWrapper(io.StringIO('void f() { int x }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_missing_semi_in_var_def():
    in_stream = FileWrapper(io.StringIO('void f() { int x = 0}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
# If statements

def test_no_parens_in_if():
    in_stream = FileWrapper(io.StringIO('void f() { if true {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_no_expr_in_if():
    in_stream = FileWrapper(io.StringIO('void f() { if () {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_no_if_body():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_non_termininating_if_body():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) { x = 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_if_with_no_if():
    in_stream = FileWrapper(io.StringIO('void f() { elseif (true) { } }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_else_if_with_no_condition():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) elseif { } }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_if_with_only_parens():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) elseif ( ) { } }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_else_if_with_no_body():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) elseif (false) }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_with_no_if():
    in_stream = FileWrapper(io.StringIO('void f() { else {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_out_of_order():
    in_stream = FileWrapper(io.StringIO(
        'void f() { '
        '  if (true) { } '
        '  else { } '
        '  elseif (false) { } '
        '}'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_with_no_body():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) else }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_else_with_no_terminating_body():
    in_stream = FileWrapper(io.StringIO('void f() { if (true) else { }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

# While statements

def test_while_with_no_condition():
    in_stream = FileWrapper(io.StringIO('void f() { while () { } }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_while_with_no_parens():
    in_stream = FileWrapper(io.StringIO('void f() { while true { } }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_while_with_no_terminating_body():
    in_stream = FileWrapper(io.StringIO('void f() { while (true) { }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
# For statements

def test_for_with_no_loop_control():
    in_stream = FileWrapper(io.StringIO('void f() { for {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_for_with_empty_loop_control():
    in_stream = FileWrapper(io.StringIO('void f() { for () {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_for_with_missing_condition():
    in_stream = FileWrapper(io.StringIO('void f() { for (int i=0; i=i+1) {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_for_with_missing_assign():
    in_stream = FileWrapper(io.StringIO('void f() { for (int i=0; i<10;) {} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
def test_for_with_missing_body():
    in_stream = FileWrapper(io.StringIO('void f() { for (int i=0; i<10; i=i+1) }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_for_with_non_terminated_body():
    in_stream = FileWrapper(io.StringIO('void f() { for (int i=0; i<10; i=i+1) { }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    
# Assignment statements

def test_assign_with_missing_expression():
    in_stream = FileWrapper(io.StringIO('void f() { x=; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_assign_with_missing_assign_op():
    in_stream = FileWrapper(io.StringIO('void f() { x 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_assign_with_missing_assign_semicolon():
    in_stream = FileWrapper(io.StringIO('void f() { x = 0 }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_assign_with_bad_lvalue():
    in_stream = FileWrapper(io.StringIO('void f() { x.y. = 0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

# Expressions

def test_expression_with_missing_operand():
    in_stream = FileWrapper(io.StringIO('void f() { x = 2.1 * 4 +; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_expression_with_too_many_ops():
    in_stream = FileWrapper(io.StringIO('void f() { x = 2.1 * + 4; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')


def test_expression_with_too_few_parens():
    in_stream = FileWrapper(io.StringIO('void f() { x = (2.1 * 3.0; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_expression_with_bad_id_rvalue():
    in_stream = FileWrapper(io.StringIO('void f() { x = y.z. ; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')
    

# TODO: Add at least 5 of your own "negative" expression tests below:

def test_nested_function():
    in_stream = FileWrapper(io.StringIO('void f() { void y(){} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_struct_declaration_in_function():
    in_stream = FileWrapper(io.StringIO('void f() { struct mystruct{int x;} }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_new_literal_value():
    in_stream = FileWrapper(io.StringIO('void f() { x = new 12; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_assign_value_to_literal():
    in_stream = FileWrapper(io.StringIO('void f() { 2 = 3; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')

def test_assign_with_equals():
    in_stream = FileWrapper(io.StringIO('void f() { x == 3; }'))
    p = ASTParser(Lexer(in_stream))
    with pytest.raises(MyPLError) as e:
        p.parse()
    assert str(e.value).startswith('Parser Error')