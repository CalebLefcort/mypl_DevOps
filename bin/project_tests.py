#----------------------------------------------------------------------
# Project Unit Tests
# Caleb Lefcort
# Bowers 326
# 5/10/2024
#
# These are a comprehensive set of unit tests I used to check my extention
#----------------------------------------------------------------------

import pytest
import io
from mpl.mypl_error import *
from mpl.mypl_iowrapper import *
from mpl.mypl_token import *
from mpl.mypl_lexer import *
from mpl.mypl_ast_parser import *
from mpl.mypl_var_table import *
from mpl.mypl_code_gen import *
from mpl.mypl_vm import *
from mpl.mypl_semantic_checker import *
from mpl.mypl_symbol_table import *


#-------------------------------------------------------------------------------
# AST tests
#-------------------------------------------------------------------------------
def test_empty_fun():
    in_stream = FileWrapper(io.StringIO(
        'int f(){return 1;}\n'
        'void main() {f();}'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[1].stmts[0].fun_id == 'f'

def test_one_param_fun():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x){return 1;}\n'
        'void main() {f(2);}'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 1
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[1].stmts[0].fun_id == 'f_int'

def test_two_param_fun():
    in_stream = FileWrapper(io.StringIO(
        'int f(int x, string y){return 1;}\n'
        'void main() {f(2, "yo");}'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 2
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[1].stmts[0].fun_id == 'f_int_string'

def test_one_array_param_fun():
    in_stream = FileWrapper(io.StringIO(
        'int f(array int x){return 1;}\n'
        'void main() {\n'
            'array int xs = new int[10];\n'
            'f(xs);}\n'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 1
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[1].stmts[1].fun_id == 'f_intarray'

def test_one_array_param_and_param_fun():
    in_stream = FileWrapper(io.StringIO(
        'int f(array int x, string y){return 1;}\n'
        'void main() {\n'
            'array int xs = new int[10];\n'
            'f(xs, "yo");}\n'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 2
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[1].stmts[1].fun_id == 'f_intarray_string'

def test_ast_overload_fun():
    in_stream = FileWrapper(io.StringIO(
        'void f(int x){}\n'
        'void f(string x){}\n'
        'void main() {'
            'f(2);\n'
            'f("yo");}\n'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 3
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'void'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 1
    assert len(p.fun_defs[0].stmts) == 0
    assert p.fun_defs[2].stmts[0].fun_id == 'f_int'
    assert p.fun_defs[2].stmts[1].fun_id == 'f_string'

def test_struct_param_fun():
    in_stream = FileWrapper(io.StringIO(
        'struct Node{}'
        'void f(Node t){}\n'
        'void main() {\n'
            'Node x = new Node();\n'
            'f(x);}\n'
                                        ))
    p = ASTParser(Lexer(in_stream)).parse()
    visitor = SemanticChecker()
    p.accept(visitor)
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 1
    assert p.fun_defs[0].return_type.type_name.lexeme == 'void'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 1
    assert len(p.fun_defs[0].stmts) == 0
    assert p.fun_defs[1].stmts[1].fun_id == 'f_Node'

#-------------------------------------------------------------------------------
# Basic functions tests
#-------------------------------------------------------------------------------

#---------------------------------Positive--------------------------------------
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

def test_dec_as_null(capsys):
    program = (
        'void f(string x){print("Hi");}\n'
        'void f(int x){print("yo");}\n'
        'void main() { \n'
        '  string y = null; \n'
        '  int x = null; \n'
        '  f(y); \n'
        '  f(x); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'Hiyo'

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

#---------------------------------Negative--------------------------------------
def test_null_parameter_call():
    program = (
        'bool f(int x) {} \n'
        'void main() { \n'
        '  bool y = f(null); \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_function_with_two_params_same_name():
    program = (
        'void f(int x, double y, string x) {} \n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_param_type():
    program = (
        'void f(int x, array double y, Node z) {} \n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_function_with_bad_return_type():
    program = (
        'Node f(int x) {} \n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_call_to_undeclared_function():
    program = (
        'void main() { \n'
        '  f(); \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_too_few_args_in_function_call():
    program = (
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(); \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_too_many_args_in_function_call():
    program = (
        'void f(int x) {} \n'
        'void main() { \n'
        '  f(1, 2); \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')
#-------------------------------------------------------------------------------
# Basic overload tests
#-------------------------------------------------------------------------------

#---------------------------------Positive--------------------------------------
def test_basic_overload(capsys):
    program = (
        'int sum(int x, int y){return x+y;}\n'
        'double sum(double x, double y){return x+y;}\n'
        'void main() { \n'
        '  int x = sum(7,4); \n'
        '  print(x); \n'
        '  double y = sum(7.2,4.2); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '1111.4'

def test_string_int(capsys):
    program = (
        'int f(int x){return x+1;}\n'
        'string f(string x){return x+"!";}\n'
        'void main() { \n'
        '  int x = f(1); \n'
        '  print(x); \n'
        '  string y = f("hi"); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '2hi!'

def test_no_param_one_param(capsys):
    program = (
        'int f(){return 1;}\n'
        'int f(int x){return x+2;}\n'
        'void main() { \n'
        '  int x = f(); \n'
        '  print(x); \n'
        '  int y = f(2); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '14'

def test_fun_param_other_fun(capsys):
    program = (
        'int f(){return 1;}\n'
        'int f(int x, int y){return x+y;}\n'
        'void main() { \n'
        '  print(f(f(),f())); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '2'

def test_struct_int(capsys):
    program = (
        'struct T {string x;} \n'
        'string f(T s){return s.x;}\n'
        'int f(int x){return x*2;}\n'
        'void main() { \n'
        '  T r = new T("hi"); \n'
        '  string x = f(r); \n'
        '  print(x); \n'
        '  int y = f(2); \n'
        '  print(y); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'hi4'

def test_array_int_int(capsys):
    program = (
        'int f(array int x){return x[0];}\n'
        'int f(int x){return x;}\n'
        'void main() { \n'
        '  array int xs = new int[1]; \n'
        '  xs[0] = 5; \n'
        '  print(f(xs)); \n'
        '  print(f(4)); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '54'

#---------------------------------Negative--------------------------------------
def test_bad_same_fun(capsys):
    program = (
        'int f(){return 1;}\n'
        'int f(){return 1;}\n'
        'void main() { \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_same_fun_dif_return(capsys):
    program = (
        'int f(){return 1;}\n'
        'string f(){return "hi";}\n'
        'void main() { \n'
        '} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_two_mains(capsys):
    program = (
        'void main() {} \n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_two_mains_dif_params(capsys):
    program = (
        'void main(int x) {} \n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_no_main(capsys):
    program = (
        'void f() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')


#-------------------------------------------------------------------------------
# Built-ins tests
#-------------------------------------------------------------------------------

#---------------------------------Positive--------------------------------------
def test_overload_print(capsys):
    program = (
        'void print(int x, int y){print("Hi");}\n'
        'void main() { \n'
        '  print(3); \n'
        '  print(3,5); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '3Hi'

def test_overload_input(capsys):
    program = (
        'void input(int x){print("Hi");}\n'
        'void main() { \n'
        '  input(3); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'Hi'

def test_overload_stoi(capsys):
    program = (
        'void stoi(int x){print("Hi");}\n'
        'void main() { \n'
        '  print(1+stoi("3")); \n'
        '  stoi(1); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4Hi'

def test_overload_stod(capsys):
    program = (
        'void stod(int x){print("Hi");}\n'
        'void main() { \n'
        '  print(1.1+stod("3.1")); \n'
        '  stod(1); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4.2Hi'

def test_overload_itod(capsys):
    program = (
        'void itod(string x){print("Hi");}\n'
        'void main() { \n'
        '  print(1.1+itod(3)); \n'
        '  itod("a"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4.1Hi'

def test_overload_itos(capsys):
    program = (
        'void itos(string x){print("Hi");}\n'
        'void main() { \n'
        '  print("b"+itos(3)); \n'
        '  itos("a"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'b3Hi'

def test_overload_dtos(capsys):
    program = (
        'void dtos(string x){print("Hi");}\n'
        'void main() { \n'
        '  print("b"+dtos(3.1)); \n'
        '  dtos("a"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == 'b3.1Hi'

def test_overload_dtoi(capsys):
    program = (
        'void dtoi(string x){print("Hi");}\n'
        'void main() { \n'
        '  print(1+dtoi(3.0)); \n'
        '  dtoi("a"); \n'
        '} \n'
    )
    build(program).run()
    captured = capsys.readouterr()
    assert captured.out == '4Hi'

#---------------------------------Negative--------------------------------------
def test_bad_print_redef_int(capsys):
    program = (
        'void print(int x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_print_redef_bool(capsys):
    program = (
        'void print(bool x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_print_redef_double(capsys):
    program = (
        'void print(double x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_print_redef_string(capsys):
    program = (
        'void print(string x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    assert str(e.value).startswith('Static Error:')

def test_bad_input_redef(capsys):
    program = (
        'void input(){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_itos_redef(capsys):
    program = (
        'void itos(int x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_itod_redef(capsys):
    program = (
        'void itod(int x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_stod_redef(capsys):
    program = (
        'void stod(string x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_stoi_redef(capsys):
    program = (
        'void stoi(string x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_dtoi_redef(capsys):
    program = (
        'void dtoi(double x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_dtos_redef(capsys):
    program = (
        'void dtos(double x){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_length_redef(capsys):
    program = (
        'void length(array int xs){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_length_redef_struct(capsys):
    program = (
        'struct T {string x;} \n'
        'void length(array T xs){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

def test_bad_get_redef(capsys):
    program = (
        'void get(int x, string y){}\n'
        'void main() {} \n'
    )
    with pytest.raises(MyPLError) as e:
        build(program).run()
    print(e)
    assert str(e.value).startswith('Static Error:')

