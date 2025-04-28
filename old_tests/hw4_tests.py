"""Unit tests for CPSC 326 HW-4. 

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

from mpl.mypl_error import *
from mpl.mypl_iowrapper import *
from mpl.mypl_token import *
from mpl.mypl_lexer import *
from mpl.mypl_ast_parser import *
from mpl.mypl_semantic_checker import *
from mpl.mypl_symbol_table import *

#----------------------------------------------------------------------
# SYMBOL TABLE TESTS
#----------------------------------------------------------------------

def test_empty_table():
    table = SymbolTable()
    assert len(table) == 0

def test_push_pop():
    table = SymbolTable()
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

def test_simple_add():
    table = SymbolTable()
    table.add('x', 'int')
    assert not table.exists('x')
    table.push_environment()
    table.add('x', 'int')
    assert table.exists('x') and table.get('x') == 'int'
    table.pop_environment()

def test_multiple_add():
    table = SymbolTable()
    table.push_environment()
    table.add('x', 'int')
    table.add('y', 'double')
    assert table.exists('x') and table.get('x') == 'int'
    assert table.exists('y') and table.get('y') == 'double'

def test_multiple_environments():
    table = SymbolTable()
    table.push_environment()
    table.add('x', 'int')
    table.add('y', 'double')
    table.push_environment()
    table.add('x', 'string')
    table.add('z', 'bool')
    table.push_environment()
    table.add('u', 'Node')
    assert table.exists('x') and table.get('x') == 'string'
    assert table.exists('y') and table.get('y') == 'double'
    assert table.exists('z') and table.get('z') == 'bool'
    assert table.exists('u') and table.get('u') == 'Node'
    assert not table.exists_in_curr_env('x')
    assert not table.exists_in_curr_env('y')
    assert not table.exists_in_curr_env('z')
    assert table.exists_in_curr_env('u')
    table.pop_environment()
    assert not table.exists('u')
    assert table.exists_in_curr_env('x') and table.get('x') == 'string'
    assert table.exists_in_curr_env('z') and table.get('z') == 'bool'
    table.pop_environment()
    assert not table.exists('z')
    assert table.exists('x') and table.get('x') == 'int'
    assert table.exists('y') and table.get('y') == 'double'
    table.pop_environment()

    
#----------------------------------------------------------------------
# BASIC FUNCTION DEFINITIONS
#----------------------------------------------------------------------

def test_smallest_program():
    in_stream = FileWrapper(io.StringIO('void main() {}'))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_valid_function_defs():
    in_stream = FileWrapper(io.StringIO(
        'void f1(int x) {} \n'
        'void f2(double x) {} \n'
        'bool f3(bool x) {} \n'
        'string f4(int p1, bool p2) {} \n'
        'void f5(double p1, int p2, string p3) {} \n'
        'int f6(int p1, int p2, string p3) {} \n'
        'array int f7() {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_missing_main():
    in_stream = FileWrapper(io.StringIO(''))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_main_with_bad_params():
    in_stream = FileWrapper(io.StringIO('void main(int x) {}'))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_main_with_bad_return_type():
    in_stream = FileWrapper(io.StringIO('int main() {}'))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_redefined_built_in():
    in_stream = FileWrapper(io.StringIO(
        'void input(string msg) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_two_functions_same_name():
    in_stream = FileWrapper(io.StringIO(
        'void f(string msg) {} \n'
        'int f() {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_two_params_same_name():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, double y, string x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_param_type():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, array double y, Node z) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_array_param_type():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, array Node y) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_return_type():
    in_stream = FileWrapper(io.StringIO(
        'Node f(int x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_function_with_bad_array_return_type():
    in_stream = FileWrapper(io.StringIO(
        'array Node f(int x) {} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#------------------------------------------------------------
# BASIC STRUCT DEFINITION CASES
#------------------------------------------------------------

def test_valid_structs():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; int y;} \n'
        'struct S2 {bool x; string y; double z;} \n'
        'struct S3 {S1 s1;} \n'
        'struct S4 {array int xs;} \n'
        'struct S5 {array S4 s4s;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_self_ref():
    in_stream = FileWrapper(io.StringIO(
        'struct Node {int val; Node next;} \n'
        'struct BigNode {array int val; array Node children;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_mutual_ref():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; S2 y;} \n'
        'struct S2 {int u; S1 v;} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_struct_and_function_same_name():
    in_stream = FileWrapper(io.StringIO(
        'struct s {} \n'
        'void s() {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_function_with_struct_param():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x, S y, array S z) {} \n'
        'struct S {} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_two_structs_same_name():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x;} \n'
        'struct S {bool y;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_with_undefined_field_type():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; S2 s;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_with_same_field_names():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x; double y; string x;} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# VARIABLE DECLARATIONS
#----------------------------------------------------------------------

def test_good_var_decls():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 0; \n'
        '  double x2 = 0.0; \n'
        '  bool x3 = false; \n'
        '  string x4 = "foo"; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_good_var_decls_with_null():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = null; \n'
        '  double x2 = null; \n'
        '  bool x3 = null; \n'
        '  string x4 = null; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_good_var_decls_no_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x3; \n'
        '  string x4; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_local_shadow(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x1; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_mismatched_var_decl_types(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 3.14; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_mismatched_var_decl_array_types(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = 256; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# EXPRESSIONS
#----------------------------------------------------------------------

def test_expr_no_parens():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 1 + 2 + 3 * 4 / 5 - 6 - 7; \n'
        '  double x2 = 1.0 + 2.1 + 3.3 * 4.4 / 5.5 - 6.6 - 7.7; \n'
        '  bool x3 = not true or false and true and not false; \n'
        '  string x4 = "a" + "b" + "c"; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_expr_with_parens():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = ((1 + 2) + (3 * 4)) / ((5 - 6) - 7); \n'
        '  double x2 = ((1.0 + 2.1) + (3.3 * 4.4) / (5.5 - 6.6)) - 7.7; \n'
        '  bool x3 = not (true or false) and (true and not false); \n'
        '  string x4 = (("a" + "b") + "c"); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_expr_with_parens_and_vars():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = (1 + 2) + (3 * 4); \n'
        '  int x2 = (5 - 6) - 7; \n'
        '  int x3 = ((x1 / x2) + x1 - x2) / (x1 + x2); \n' 
        '  double x4 = (1.0 + 2.1) + (3.3 * 4.4); \n'
        '  double x5 = (5.5 - 6.6) - 7.7; \n'
        '  double x6 = ((x4 / x5) + x5 - x4) / (x4 + x5); \n'
        '  bool x7 = not (true or false); \n'
        '  bool x8 = true and not x7; \n'
        '  bool x9 = (x7 and x8) or (not x7 and x8) or (x7 and not x8); \n'
        '  string x10 = "a" + "b"; \n'
        '  string x11 = (x10 + "c") + ("c" + x10); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_basic_relational_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = 0 < 1; \n'
        '  bool x2 = 0 <= 1; \n' 
        '  bool x3 = 0 > 1; \n'
        '  bool x4 = 0 >= 1; \n'
        '  bool x5 = 0 != 1; \n'
        '  bool x6 = 0 == 1; \n'
        '  bool x7 = 0 != null; \n'
        '  bool x8 = 0 == null; \n'
        '  bool x9 = null != null; \n'
        '  bool x10 = null == null; \n'
        '  bool x11 = not 0 < 1; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_combined_relational_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = (0 < 1) and ("a" < "b") and (3.1 < 3.2); \n'
        '  bool x2 = (not ("a" == null)) or (not (3.1 != null)); \n'
        '  bool x4 = ("abc" <= "abde") or (x1 == false); \n'
        '  bool x5 = (not x2 == null) and 3.1 >= 4.1; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_array_comparisons():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = new int[10]; \n'
        '  array int x2 = x1; \n'
        '  bool x3 = (x2 != null) and ((x1 != x2) or (x1 == x2)); \n' 
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_bad_relational_comparison():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x1 = (true < false); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_array_relational_comparison():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1 = new int[10]; \n'
        '  array int x2 = x1; \n'
        '  bool x1 = x1 <= x2; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_logical_negation():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool x = not (1 + 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')


#----------------------------------------------------------------------
# FUNCTION RETURN TYPES
#----------------------------------------------------------------------

def test_function_return_match():
    in_stream = FileWrapper(io.StringIO(
        'int f() {return 42;} \n'
        'int g() {return null;} \n'
        'void h() {return null;} \n'
        'bool i() {return true;} \n'
        'array double j() {return new double[10];} \n'
        'void main() {} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_bad_function_return_type():
    in_stream = FileWrapper(io.StringIO(
        'int f() {return true;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_non_null_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() {return 0;} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_one_return_bad_type():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) { \n'
        '  if (x < 0) {return 0;} \n'
        '  else {return false;} \n'
        '} \n'
        'void main() {} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BASIC CONDITIONAL CHECKS
#----------------------------------------------------------------------

def test_bad_non_bool_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (1) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_non_bool_elseif():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (false) {} elseif ("a") {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool flags = new bool[2]; \n'
        '  if (flags) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_elseif():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool flags = new bool[2]; \n'
        '  if (true) {} elseif (flags) {} \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_bool_while():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (3 * 2) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_array_while():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool xs = new bool[2]; \n'
        '  while (xs) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_condition_for_1():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i; i + 1; i = i + 1) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_bool_condition_for():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool xs = new bool[2]; \n'
        '  for (int i; xs; i = i + 1) { } \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BASIC FUNCTION CALLS
#----------------------------------------------------------------------

def test_call_to_undeclared_function():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_too_few_args_in_function_call():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_too_many_args_in_function_call():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    

#----------------------------------------------------------------------
# SHADOWING
#----------------------------------------------------------------------

def test_allowed_shadowing():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x = 0; \n'
        '  if (true) { \n'
        '    double x = 1.0; \n'
        '    double y = x * 0.01; \n'
        '  } \n'
        '  elseif (false) { \n'
        '    bool x = true; \n'
        '    bool y = x and false; \n'
        '  } \n'
        '  for (double x = 0.0; x < 10.0; x = x + 1.0) { \n'
        '    double y = x / 2.0; \n'
        '  } \n'
        '  while (true) { \n'
        '    string x = ""; \n'
        '    string y = x + "a"; \n'
        '  } \n'        
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    
    
def test_illegal_shadowing_example():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x = 0; \n'
        '  if (true) { \n'
        '    int y = x  + 1; \n'
        '  } \n'
        '  double x = 1.0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

# print function

def test_print_exampes():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  print(0); \n'
        '  print(1.0); \n'
        '  print(true); \n'
        '  print("abc"); \n'
        '  int x = print(0); \n'  # print returns void
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())    

def test_print_struct_object():
    in_stream = FileWrapper(io.StringIO(
        'struct S {} \n'
        'void main() { \n'
        '  S s = new S(); \n'
        '  print(s); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_print_array_object():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int xs = new int[10]; \n'
        '  print(xs); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_print_arg_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  print(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# input function

def test_input_example():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = input(); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_input_return_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int s = input(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_input_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int s = input("Name: "); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
# casting functions

def test_cast_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string x1 = itos(5); \n'
        '  string x2 = dtos(3.1); \n'
        '  int x3 = stoi("5"); \n'
        '  int x4 = dtoi(3.1); \n'
        '  double x5 = stod("3.1"); \n'
        '  double x6 = itod(5); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
# itos functions
    
def test_itos_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = itos(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itos_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = itos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# dtos function    

def test_dtos_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtos_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(0.0, 1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtos_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string s = dtos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_dtos_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = dtos(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# itod function

def test_itod_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = itod(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itod_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = itod(0, 1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_itod_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  double d = dtos(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_itod_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = itod(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# dtoi function

def test_dtoi_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(0.0, 1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = dtoi(1); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_dtoi_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = dtoi(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# length function

def test_length_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l1 = length("abc"); \n'
        '  int l2 = length(new int[1]); \n'
        '  int l3 = length(new double[10]); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_length_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_length_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length("abc", "def"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_length_bad_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int l = length(1.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_length_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  bool b = length("abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

# get function

def test_get_examples():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c1 = get(0, "abc"); \n'
        '  string c2 = get(10, ""); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_get_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_get_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(0, "abc", "def"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_first_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(1.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_second_arg():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  string c = get(1, new string[10]); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_get_bad_return():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int i = get(0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
#------------------------------------------------------------
# USER-DEFINED FUNCTIONS CALLS
#------------------------------------------------------------

def test_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(1) + f(1 + 2); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_type_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(2.0); \n'
        '  int y = f(null); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_too_many_params_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_too_few_params_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  int x = f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_return_single_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {} \n'
        'void main() { \n'
        '  double x = f(2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'bool f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  bool x = f(1, 2.0, "abc"); \n'
        '  bool y = f(null, null, null); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_arg_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  bool x = f(1, "abc", 2.0); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_return_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  string x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
def test_bad_return_array_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'array int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  int x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_return_no_array_mutiple_parameter_call():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, double y, string z) {} \n'
        'void main() { \n'
        '  array int x = f(1, 2.0, "abc"); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_single_param_access():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x) {return x;} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_multiple_param_access():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, double y) {return x + y;} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_multiple_type_param_access():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, string y) {return x + stod(y);} \n'
        'void main() { } \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_param_type_mismatch():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x, string y) {return x + y;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_missing_param():
    in_stream = FileWrapper(io.StringIO(
        'double f(double x) {return x + y;} \n'
        'void main() { } \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# ADDITIONAL ARRAY TESTS
#----------------------------------------------------------------------

def test_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S {} \n'
        'void main() { \n'
        '  int n = 10; \n'
        '  array int a1 = new int[n]; \n'
        '  array int a2 = null; \n'
        '  a2 = a1; \n'
        '  array double a3 = new double[10]; \n'
        '  array string a4 = new string[n+1]; \n'
        '  array string a5 = null; \n'
        '  array bool a6 = new bool[n]; \n'
        '  array S a7 = new S[n]; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_base_type_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int a1 = new double[n]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_type_array_creation(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {} \n'
        'struct S2 {} \n'
        'void main() { \n'
        '  array S1 a1 = new S2[n]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_array_access():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {string val;} \n'
        'void main() { \n'
        '  int n = 10; \n'
        '  array bool a1 = new bool[n]; \n'
        '  array S1 a2 = new S1[n]; \n'
        '  bool x = a1[n-5]; \n'
        '  a1[0] = x or true; \n'
        '  a2[0] = null; \n'
        '  S1 s = a2[1]; \n'
        '  string t = a2[0].val; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_array_assignment(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool a1 = new bool[10]; \n'
        '  a1[0] = 10; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_array_access(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool a1 = new bool[10]; \n'
        '  int x = a1[0]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')
    
    
#----------------------------------------------------------------------
# ADDITIONAL STRUCT TESTS
#----------------------------------------------------------------------

def test_struct_creation():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 { } \n'
        'struct S2 {int x;} \n'
        'struct S3 {int x; string y;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(); \n'
        '  S2 p2 = new S2(5); \n'
        '  S3 p3 = new S3(5, "a"); \n'
        '  S3 p4 = new S3(null, null); \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_struct_creation_too_few_args():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_creation_too_many_args():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_struct_creation_bad_arg_type():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {int x; string y;} \n'
        'void main() { \n'
        '  S1 p1 = new S1(1, 2); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_struct_path_examples():
    in_stream = FileWrapper(io.StringIO(
        'struct S {double val; T t;} \n'
        'struct T {bool val; S s;} \n'
        'void main() { \n'
        '  S s; \n'
        '  T t = new T(null, s); \n'
        '  s = new S(null, t); \n'
        '  s.val = 1.0; \n'
        '  t.val = true; \n'
        '  s.t.val = false; \n'
        '  t.s.val = 2.0; \n'
        '  s.t.s.val = 3.0; \n'
        '  t.s.t.val = true; \n'
        '  double x = s.val; \n'
        '  bool y = t.val; \n'
        '  y = s.t.val; \n'
        '  x = t.s.val; \n'
        '  x = s.t.s.val; \n'
        '  y = t.s.t.val; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_lvalue_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  s.s.val = 0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')


def test_bad_rvalue_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  int x = p.s.s.val; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_lvalue_array_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0].s[1].val = 5.0; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    
def test_bad_lvalue_array_path_type(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0].s.val = 5.0; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

    
#----------------------------------------------------------------------
# TODO: Add at least 10 of your own tests below. Half of the tests
# should be positive tests, and half should be negative. Focus on
# trickier parts of your code (e.g., rvalues, lvalues, new rvalues)
# looking for places in your code that are not tested by the above.
#----------------------------------------------------------------------
    
# positive
def test_function_return_struct_type():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val;} \n'
        'S1 f() {return new S1(3.4);}'
        'void main() { \n'
        'S1 p = f();'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_assign_array_null(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int i = null; \n'
        '  i = new int[5]; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_array_usage(): 
    in_stream = FileWrapper(io.StringIO(
        'void main() {\n'
            'array int xs = new int[100];\n'
            'xs[0] = 1;\n'
            'int x = xs[99];\n'
            'array int xs_ref = xs;\n'
        '}\n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_array_access_rvalue(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '    S1 s1 = new S1(null, null); \n'
        '    array S1 s2 = null; \n'
        '    s2 = s1.s; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_array_access_lvalue(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '    S1 s1 = new S1(null, null); \n'
        '    array S1 s2 = null; \n'
        '    s1.s = s2; \n'
        '} \n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())


# negative
def test_lvalue_path_array_assigned_non_array(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0].s = new S1(null, null); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_lvalue_path_array_index_assigned_array(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  p.s[0] = new S1[100]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_return_int_array_to_int():
    in_stream = FileWrapper(io.StringIO(
        'array int f() {} \n'
        'void main() { \n'
        '   int x = f(); \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_assignment_with_multiple_array_indexs(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  S1 p2 = new S1(null, null); \n'
        '  p.s[0].s[2].s = p2.s[0].s[2]; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_assignment_struct_val_assignment(): 
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {double val; array S1 s;} \n'
        'struct S2 {double val; array S2 s;} \n'
        'void main() { \n'
        '  S1 p = new S1(null, null); \n'
        '  S2 p2 = new S1(null, null); \n'
        '  p.s = p2.s; \n'
        '} \n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')