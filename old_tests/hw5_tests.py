"""Unit tests for CPSC 326 HW-5. 

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
from mypl_opcode import *
from mypl_frame import *
from mypl_vm import *


#----------------------------------------------------------------------
# SIMPLE GETTING STARTED TESTS 
#----------------------------------------------------------------------

def test_single_nop():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(NOP())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()

def test_single_write(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'


def test_dup(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(24))
    main.instructions.append(DUP())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '2424'
    
#----------------------------------------------------------------------
# BASIC LITERALS AND VARIABLES
#----------------------------------------------------------------------

def test_single_pop(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(PUSH('green'))
    main.instructions.append(POP())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_write_null(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_store_and_load(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
#----------------------------------------------------------------------
# OPERATIONS
#----------------------------------------------------------------------

def test_int_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(12))
    main.instructions.append(PUSH(24))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '36'

def test_double_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.50))
    main.instructions.append(PUSH(2.25))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '5.75'

def test_string_add(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('def'))
    main.instructions.append(ADD())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'abcdef'

def test_null_add_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(24))
    main.instructions.append(ADD())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_null_add_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(12))
    main.instructions.append(PUSH(None))
    main.instructions.append(ADD())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_sub(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(15))
    main.instructions.append(PUSH(9))
    main.instructions.append(SUB())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '6'

def test_double_sub(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.75))
    main.instructions.append(PUSH(2.50))
    main.instructions.append(SUB())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1.25'
    
def test_null_sub_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(SUB())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_sub_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(SUB())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_mult(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(15))
    main.instructions.append(PUSH(3))
    main.instructions.append(MUL())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '45'

def test_double_mult(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(3.00))
    main.instructions.append(MUL())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '3.75'
    
def test_null_mult_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(MUL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_mult_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(MUL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_div(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(16))
    main.instructions.append(PUSH(3))
    main.instructions.append(DIV())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '5'

def test_bad_int_div_by_zero():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(0))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_double_div(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.75))
    main.instructions.append(PUSH(3.00))
    main.instructions.append(DIV())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1.25'

def test_bad_double_div_by_zero():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10.0))
    main.instructions.append(PUSH(0.0))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_null_div_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(10))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_div_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(PUSH(None))
    main.instructions.append(DIV())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_and(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(False))
    main.instructions.append(AND())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(False))
    main.instructions.append(AND())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())        
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsefalsetrue'
    
def test_null_and_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(True))
    main.instructions.append(AND())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_and_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(None))
    main.instructions.append(AND())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_or(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    main.instructions.append(PUSH(True))
    main.instructions.append(PUSH(False))
    main.instructions.append(OR())
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(False))
    main.instructions.append(OR())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())        
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetruetrue'
    
def test_null_or_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(True))
    main.instructions.append(OR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_or_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(PUSH(None))
    main.instructions.append(OR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_not(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(NOT())
    main.instructions.append(PUSH(False))
    main.instructions.append(NOT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalse'
    
def test_null_not_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(NOT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_double_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_string_less_than(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLT())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLT())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsefalsetrue'

def test_less_than_null_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_less_than_null_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPLT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_double_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_string_less_than_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLE())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPLE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsetrue'

def test_less_than_equal_null_first_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPLE())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_less_than_equal_null_second_operand():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPLE())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_int_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_double_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_string_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPEQ())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'truefalsefalse'

def test_equal_null_first_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'false'

def test_equal_null_second_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPEQ())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'false'

def test_int_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH(2))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_double_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1.25))
    main.instructions.append(PUSH(1.50))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(1.50))
    main.instructions.append(PUSH(1.25))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH(2.125))
    main.instructions.append(PUSH(2.125))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_string_not_equal(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abd'))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH('abd'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPNE())
    main.instructions.append(PUSH('abc'))
    main.instructions.append(PUSH('abc'))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())    
    main.instructions.append(WRITE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'falsetruetrue'

def test_not_equal_null_first_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH(1))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'true'

def test_not_equal_null_second_operand(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH(None))
    main.instructions.append(CMPNE())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'true'

    
#----------------------------------------------------------------------
# Jumps
#----------------------------------------------------------------------

def test_jump_forward(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(JMP(3))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'green'

                
def test_jump_false_forward(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(False))
    main.instructions.append(JMPF(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'green'

def test_jump_false_no_jump(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(True))
    main.instructions.append(JMPF(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_jump_backwards(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))       # 0
    main.instructions.append(STORE(0))      # 1
    main.instructions.append(LOAD(0))       # 2
    main.instructions.append(PUSH(2))       # 3
    main.instructions.append(CMPLT())       # 4
    main.instructions.append(JMPF(13))      # 5
    main.instructions.append(PUSH('blue'))  # 6
    main.instructions.append(WRITE())       # 7
    main.instructions.append(LOAD(0))       # 8
    main.instructions.append(PUSH(1))       # 9
    main.instructions.append(ADD())         # 10
    main.instructions.append(STORE(0))      # 11
    main.instructions.append(JMP(2))        # 12
    main.instructions.append(PUSH('green')) # 13
    main.instructions.append(WRITE())       # 14
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluebluegreen'

#----------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------

def test_main_returns_null(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(RET())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()


def test_function_returns_literal(capsys):
    f = VMFrameTemplate('f', 0)
    f.instructions.append(PUSH('blue'))
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'

def test_function_returns_modified_param(capsys):
    f = VMFrameTemplate('f', 1)
    f.instructions.append(PUSH(4))
    f.instructions.append(ADD())
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '7'

def test_function_two_params_subtracted(capsys):
    f = VMFrameTemplate('f', 2)
    f.instructions.append(STORE(0))
    f.instructions.append(STORE(1))
    f.instructions.append(LOAD(0))
    f.instructions.append(LOAD(1))
    f.instructions.append(SUB())
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(PUSH(3))    
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '1'

def test_function_two_params_printed(capsys):
    f = VMFrameTemplate('f', 2)
    f.instructions.append(STORE(0))
    f.instructions.append(STORE(1))
    f.instructions.append(LOAD(0))
    f.instructions.append(WRITE())
    f.instructions.append(LOAD(1))
    f.instructions.append(WRITE())
    f.instructions.append(PUSH(None))        # return null
    f.instructions.append(RET())
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('blue'))
    main.instructions.append(PUSH('green'))    
    main.instructions.append(CALL('f'))
    main.instructions.append(POP())          # clean up return value
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_function_recursive_sum_function(capsys):
    f = VMFrameTemplate('sum', 1)
    f.instructions.append(STORE(0))    # x -> var[0]
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(0))     # push 0
    f.instructions.append(CMPLE())     # x < 0
    f.instructions.append(JMPF(7))  
    f.instructions.append(PUSH(0))
    f.instructions.append(RET())       # return 0
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(1))
    f.instructions.append(SUB())       # x - 1
    f.instructions.append(CALL('sum')) # sum(x-1)
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(ADD())       # sum(x-1) + x
    f.instructions.append(RET())       # return sum(x-1) + x    
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(CALL('sum'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '10'

def test_call_multiple_functions(capsys):
    # int f(int x) { return g(x+1) + 1; }
    f = VMFrameTemplate('f', 1)
    f.instructions.append(STORE(0))    # x -> var[0]
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(PUSH(1))
    f.instructions.append(ADD())       # x + 1
    f.instructions.append(CALL('g'))   # g(x + 1)
    f.instructions.append(LOAD(0))     # push x
    f.instructions.append(ADD())       # g(x+1) + x
    f.instructions.append(RET())       # return g(x+1) + x    
    # int g(int y) { return x + 2; }
    g = VMFrameTemplate('g', 1)
    g.instructions.append(STORE(0))    # y -> var[0]
    g.instructions.append(LOAD(0))     # push y
    g.instructions.append(PUSH(2))
    g.instructions.append(ADD())       # y + 2
    g.instructions.append(RET())       # return y + 2
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(CALL('f'))
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(f)
    vm.add_frame_template(g)
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '23'

#----------------------------------------------------------------------
# STRUCT RELATED
#----------------------------------------------------------------------

def test_create_two_no_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(WRITE())
    main.instructions.append(ALLOCS())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '20242025'

def test_create_single_one_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(DUP())
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))
    main.instructions.append(DUP())
    main.instructions.append(GETF('field_1'))
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_create_two_one_field_structs(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(0))           # x -> var[0]
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(1))           # y -> var[1]
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))    # x.field_1 = blue
    main.instructions.append(LOAD(1))
    main.instructions.append(PUSH('green'))
    main.instructions.append(SETF('field_1'))    # y.field_1 = green
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_1'))    # push x.field_1
    main.instructions.append(WRITE())
    main.instructions.append(LOAD(1))
    main.instructions.append(GETF('field_1'))    # push y.field_1
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'

def test_create_one_two_field_struct(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(ALLOCS())
    main.instructions.append(STORE(0))           # x -> var[0]
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))    # x.field_1 = blue
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH('green'))
    main.instructions.append(SETF('field_2'))    # x.field_2 = green
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_1'))    # push x.field_1
    main.instructions.append(WRITE())
    main.instructions.append(LOAD(0))
    main.instructions.append(GETF('field_2'))    # push x.field_2
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'bluegreen'
    
def test_null_object_get_field():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(GETF('field_1'))
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_null_object_set_field():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(SETF('field_1'))
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

#----------------------------------------------------------------------
# ARRAY RELATED
#----------------------------------------------------------------------

def test_array_alloc(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(5))   # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '20242025'

def test_bad_size_value_array_alloc():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(-1))  # array length
    main.instructions.append(ALLOCA())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_size_array_alloc():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))  # array length
    main.instructions.append(ALLOCA())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_array_access(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(5))    # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(0))    # index
    main.instructions.append(GETI())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'null'

def test_bad_null_index_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(None))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_index_too_small_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(-1))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_index_too_large_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))  # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(10))
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_array_access():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0)) # array index
    main.instructions.append(GETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_array_update(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(5))      # array length
    main.instructions.append(ALLOCA())
    main.instructions.append(STORE(0))     # store oid
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0))      # index
    main.instructions.append(PUSH('blue')) # value
    main.instructions.append(SETI())
    main.instructions.append(LOAD(0))
    main.instructions.append(PUSH(0))      # index
    main.instructions.append(GETI())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'
    
def test_loop_with_index_updates(capsys):
    main = VMFrameTemplate('main', 0)
    # allocate 3-element array
    main.instructions.append(PUSH(3))      
    main.instructions.append(ALLOCA())
    main.instructions.append(STORE(0))
    # set index 0 to 2
    for i in range(3): 
        main.instructions.append(LOAD(0))       # oid
        main.instructions.append(PUSH(i))       # index
        main.instructions.append(PUSH(10 + i))  # value
        main.instructions.append(SETI())
    # get and print index 0 to 2
    for i in range(3):
        main.instructions.append(LOAD(0)) # oid
        main.instructions.append(PUSH(i)) # index
        main.instructions.append(GETI())
        main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '101112'
    
def test_bad_null_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(STORE(0))
    main.instructions.append(LOAD(0)) # oid
    main.instructions.append(PUSH(0)) # index
    main.instructions.append(PUSH(1)) # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_index_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(None)) # index
    main.instructions.append(PUSH(1))    # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_index_too_small_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(-1)) # index
    main.instructions.append(PUSH(1))  # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_index_too_large_array_update():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(10))
    main.instructions.append(ALLOCA())
    main.instructions.append(PUSH(10)) # index
    main.instructions.append(PUSH(1))  # value
    main.instructions.append(SETI())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

#----------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#----------------------------------------------------------------------

def test_string_length(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(''))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('blue'))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('green'))
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '045'

def test_bad_null_string_length():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(LEN())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_array_length(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(3))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(10000))
    main.instructions.append(ALLOCA())
    main.instructions.append(LEN())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '0310000'
    
def test_bad_null_array_length():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(LEN())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_get_characters_from_string(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(1))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(2))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(3))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == 'blue'

def test_bad_too_small_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(-1))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_too_big_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(4))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_string_index():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(PUSH('blue'))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_string_in_get():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(0))
    main.instructions.append(PUSH(None))
    main.instructions.append(GETC())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_to_int(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3.14))
    main.instructions.append(TOINT())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('5'))
    main.instructions.append(TOINT())
    main.instructions.append(WRITE())
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '35'

def test_bad_string_to_int():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('bad int'))
    main.instructions.append(TOINT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_to_int():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TOINT())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')
    
def test_to_double(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('5.1'))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('7'))
    main.instructions.append(TODBL())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '3.05.17.0'
    
def test_bad_string_to_double():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH('bad double'))
    main.instructions.append(TODBL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_bad_null_to_double():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TODBL())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')

def test_to_string(capsys):
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(3))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH(5.1))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())
    main.instructions.append(PUSH('a string'))
    main.instructions.append(TOSTR())
    main.instructions.append(WRITE())    
    vm = VM()
    vm.add_frame_template(main)
    vm.run()
    captured = capsys.readouterr()
    assert captured.out == '35.1a string'

def test_bad_null_to_string():
    main = VMFrameTemplate('main', 0)
    main.instructions.append(PUSH(None))
    main.instructions.append(TOSTR())
    vm = VM()
    vm.add_frame_template(main)
    with pytest.raises(MyPLError) as e:
        vm.run()
    assert str(e.value).startswith('VM Error:')


    
