"""Implementation of the MyPL Virtual Machine (VM).

NAME: Caleb Lefcort
DATE: Spring 2024
CLASS: CPSC 326

"""

from mpl.mypl_error import *
from mpl.mypl_opcode import *
from mpl.mypl_frame import *


class VM:

    def __init__(self):
        """Creates a VM."""
        self.struct_heap = {}        # id -> dict
        self.array_heap = {}         # id -> list
        self.next_obj_id = 2024      # next available object id (int)
        self.frame_templates = {}    # function name -> VMFrameTemplate
        self.call_stack = []         # function call stack

    
    def __repr__(self):
        """Returns a string representation of frame templates."""
        s = ''
        for name, template in self.frame_templates.items():
            s += f'\nFrame {name}\n'
            for i in range(len(template.instructions)):
                s += f'  {i}: {template.instructions[i]}\n'
        return s

    
    def add_frame_template(self, template):
        """Add the new frame info to the VM. 

        Args: 
            frame -- The frame info to add.

        """
        self.frame_templates[template.function_name] = template

    
    def error(self, msg, frame=None):
        """Report a VM error."""
        if not frame:
            raise VMError(msg)
        pc = frame.pc - 1
        instr = frame.template.instructions[pc]
        name = frame.template.function_name
        msg += f' (in {name} at {pc}: {instr})'
        raise VMError(msg)

    
    #----------------------------------------------------------------------
    # RUN FUNCTION
    #----------------------------------------------------------------------
    
    def run(self, debug=False):
        """Run the virtual machine."""

        # grab the "main" function frame and instantiate it
        if not 'main' in self.frame_templates:
            self.error('No "main" functrion')
        frame = VMFrame(self.frame_templates['main'])
        self.call_stack.append(frame)

        # run loop (continue until run out of call frames or instructions)
        while self.call_stack and frame.pc < len(frame.template.instructions):
            # get the next instruction
            instr = frame.template.instructions[frame.pc]
            # increment the program count (pc)
            frame.pc += 1
            # for debugging:
            if debug:
                print('\n')
                print('\t FRAME.........:', frame.template.function_name)
                print('\t PC............:', frame.pc)
                print('\t INSTRUCTION...:', instr)
                val = None if not frame.operand_stack else frame.operand_stack[-1]
                print('\t NEXT OPERAND..:', val)
                cs = self.call_stack
                fun = cs[-1].template.function_name if cs else None
                print('\t NEXT FUNCTION..:', fun)

            #------------------------------------------------------------
            # Literals and Variables
            #------------------------------------------------------------

            if instr.opcode == OpCode.PUSH:
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.POP:
                frame.operand_stack.pop()
                

            # TODO: Fill in rest of ops

            
            #------------------------------------------------------------
            # Operations
            #------------------------------------------------------------
            elif instr.opcode == OpCode.STORE:
                if len(frame.variables) == instr.operand:
                    frame.variables.append(frame.operand_stack.pop())
                else:
                    frame.variables[instr.operand] = frame.operand_stack.pop()

            elif instr.opcode == OpCode.LOAD:
                frame.operand_stack.append(frame.variables[instr.operand])

            elif instr.opcode == OpCode.ADD:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y + x)

            elif instr.opcode == OpCode.SUB:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y - x)

            elif instr.opcode == OpCode.MUL:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y * x)

            elif instr.opcode == OpCode.DIV:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                if x == 0:
                    self.error("divison by zero")
                if type(x) == int:
                    frame.operand_stack.append(y // x)
                else:
                    frame.operand_stack.append(y / x)

            elif instr.opcode == OpCode.AND:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y and x)

            elif instr.opcode == OpCode.OR:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y or x)
            
            elif instr.opcode == OpCode.NOT:
                x = frame.operand_stack.pop()
                if type(x) != bool:
                    self.error("not non boolean")
                frame.operand_stack.append(not x)

            elif instr.opcode == OpCode.CMPLT:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y < x)

            elif instr.opcode == OpCode.CMPLE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y):
                    self.error("add type mismatch")
                frame.operand_stack.append(y <= x)

            elif instr.opcode == OpCode.CMPEQ:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y) and (x != None and y != None):
                    self.error("add type mismatch")
                frame.operand_stack.append(y == x)

            elif instr.opcode == OpCode.CMPNE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if type(x) != type(y) and (x != None and y != None):
                    self.error("add type mismatch")
                frame.operand_stack.append(y != x)
            


            # TODO: Fill in rest of ops
            

            #------------------------------------------------------------
            # Branching
            #------------------------------------------------------------
            elif instr.opcode == OpCode.JMP:
                frame.pc = instr.operand

            elif instr.opcode == OpCode.JMPF:
                if(not frame.operand_stack.pop()):
                    frame.pc = instr.operand

            # TODO: Fill in rest of ops
            
                    
            #------------------------------------------------------------
            # Functions
            #------------------------------------------------------------
            elif instr.opcode == OpCode.CALL:
                if not instr.operand in self.frame_templates:
                    self.error(f'No "{instr.operand}" function')
                new_frame = VMFrame(self.frame_templates[instr.operand])
                for i in range(new_frame.template.arg_count):
                    new_frame.operand_stack.append(frame.operand_stack.pop())
                self.call_stack.append(new_frame)
                frame = new_frame

            elif instr.opcode == OpCode.RET:
                return_val = frame.operand_stack.pop()
                self.call_stack.pop()
                if self.call_stack:
                    frame = self.call_stack[-1]
                    frame.operand_stack.append(return_val)
            

            # TODO: Fill in rest of ops

            
            #------------------------------------------------------------
            # Built-In Functions
            #------------------------------------------------------------

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.WRITE:
                x = frame.operand_stack.pop()
                if x == None:
                    print('null', end='')
                else:
                    if str(x) == "True":
                        print('true', end='')
                    elif str(x) == "False":
                        print('false', end='')
                    else:
                        print(x, end='')

            elif instr.opcode == OpCode.READ:
                frame.operand_stack.append(input().strip())

            elif instr.opcode == OpCode.LEN:
                x = frame.operand_stack.pop()
                if x is None:
                    self.error("invalid type for len")
                if type(x) == str:
                    frame.operand_stack.append(len(x))
                else:
                    frame.operand_stack.append(len(self.array_heap[x]))

            elif instr.opcode == OpCode.GETC:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None or y < 0 or y >= len(x):
                    self.error("Invalid string index")
                if type(x) == str:
                    frame.operand_stack.append(x[y])
                else:
                    self.error("invalid type for GETC")

            elif instr.opcode == OpCode.TOINT:
                val = frame.operand_stack.pop()
                if val == None:
                    self.error("invalid literal for TOINT")
                try:
                    frame.operand_stack.append(int(val))
                except:
                    self.error("invalid literal for TOINT")
            elif instr.opcode == OpCode.TODBL:
                val = frame.operand_stack.pop()
                if val == None:
                    self.error("invalid literal for TODBL")
                try:
                    frame.operand_stack.append(float(val))
                except:
                    self.error("invalid literal for TODBL")
            elif instr.opcode == OpCode.TOSTR:
                val = frame.operand_stack.pop()
                if val == None:
                    self.error("invalid literal for TOSTR")
                try:
                    frame.operand_stack.append(str(val))
                except:
                    self.error("invalid literal for TOSTR")
            
            #------------------------------------------------------------
            # Heap
            #------------------------------------------------------------
            elif instr.opcode == OpCode.ALLOCS:
                oid = self.next_obj_id
                self.next_obj_id += 1
                self.struct_heap[oid] = {}
                frame.operand_stack.append(oid)
            
            elif instr.opcode == OpCode.SETF:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None:
                    self.error("null field name")
                self.struct_heap[y][instr.operand] = x

            elif instr.opcode == OpCode.GETF:
                x = frame.operand_stack.pop()
                try:
                    frame.operand_stack.append(self.struct_heap[x][instr.operand])
                except:
                    self.error("feild does not exist")

            elif instr.opcode == OpCode.ALLOCA:
                oid = self.next_obj_id
                self.next_obj_id += 1
                array_len = frame.operand_stack.pop()
                if array_len == None or array_len < 0:
                    self.error("bad array size")
                self.array_heap[oid] = [None for _ in range(array_len)]
                frame.operand_stack.append(oid)
            
            elif instr.opcode == OpCode.SETI:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                z = frame.operand_stack.pop()
                if z == None or y == None or y >= len(self.array_heap[z]) or y < 0:
                    self.error("bad array oid or index")
                self.array_heap[z][y] = x

            elif instr.opcode == OpCode.GETI:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None or x >= len(self.array_heap[y]) or x < 0:
                    self.error("bad array oid or index")
                frame.operand_stack.append(self.array_heap[y][x])

            # TODO: Fill in rest of ops
            
            
            #------------------------------------------------------------
            # Special 
            #------------------------------------------------------------

            elif instr.opcode == OpCode.DUP:
                x = frame.operand_stack.pop()
                frame.operand_stack.append(x)
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.NOP:
                # do nothing
                pass

            else:
                self.error(f'unsupported operation {instr}')
