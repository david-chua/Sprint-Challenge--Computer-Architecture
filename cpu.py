"""CPU functionality."""

import sys

ADD  = 0b10100000
LDI  = 0b10000010
PRN  = 0b01000111
HLT  = 0b00000001
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
RET  = 0b00010001
CALL = 0b01010000
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
AND  = 0b10101000
OR   = 0b10101010
XOR  = 0b10101011
NOT  = 0b01101001
SHL  = 0b10101100
SHR  = 0b10101101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xF4
        self.running = True
        self.flag = 0b00000000

        self.branchtable = {
            LDI: self.ldi,
            PRN: self.prn,
            HLT: self.hlt,
            MUL: self.mul,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            ADD: self.add,
            CMP: self.cmp,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            AND: self.and,
            OR:  self.or,
            XOR: self.xor,
            NOT: self.not,
            SHL: self.shl,
            shr: self.shr
        }

    def load(self, filename):
        """Load a program into memory."""
        address = 0

        with open(filename) as file:
            for line in file:
                split_line = line.split('#')
                maybe_command = split_line[0].strip()

                if maybe_command == '':
                    continue
                self.ram[address] = int(maybe_command, 2)

                address +=1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            first_num = self.reg[reg_a]
            second_num = self.reg[reg_b]
            self.reg[reg_a] = first_num * second_num
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            value_to_shift = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] << value_to_shift
        elif op == "SHR":
            value_to_shift = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] >> value_to_shift
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR;

    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b

    def prn(self, op_a, op_b):
        value = self.reg[op_a]
        print(value)

    def hlt(self, op_a, op_b):
        self.running = False

    def add(self, op_a, op_b):
        self.alu('ADD', op_a, op_b)

    def mul(self, op_a, op_b):
        self.alu('MUL', op_a, op_b)

    def and(self, reg_a, reg_b):
        self.alu('AND', reg_a, reg_b)

    def or(self, reg_a, reg_b):
        self.alu('OR', reg_a, reg_b)

    def xor(self, reg_a, reg_b):
        self.alu('XOR', reg_a, reg_b)

    def not(self, reg_a, reg_b):
        self.alu('NOT', reg_a, reg_b)

    def shl(self, reg_a, reg_b):
        self.alu('SHL', reg_a, reg_b)

    def shr(self, reg_a, reg_b):
        self.alu('SHR', reg_a, reg_b)

    def push(self, op_a, op_b):
        self.reg[7] -= 1
        value = self.reg[op_a]
        SP = self.reg[7]

        self.ram_write(SP, value)

    def pop(self, op_a, op_b):
        SP = self.reg[7]
        value = self.ram_read(SP)
        self.reg[op_a] = value

        self.reg[7] += 1

    def call(self, op_a, op_b):
        next_instruction_address = self.pc + 2
        self.reg[7] -= 1
        SP = self.reg[7]

        self.ram_write(SP, next_instruction_address)

        call_address = self.reg[op_a]

        self.pc = call_address

    def ret(self, op_a, op_b):
        SP = self.reg[7]

        return_address = self.ram_read(SP)

        self.pc = return_address

    def cmp(self, reg_a, reg_b):
        #compare the values in two registers
        #if equal: set E flag to 1 otherwise, set it to 0
        # if regA is less, set L flag to 1, otherwise, set it to 0
        # if regB is greater, selt G flag to 1, otherwise set it to 0
        reg_value1 = self.reg[reg_a]
        reg_value2 = self.reg[reg_b]
        #00000LGE
        if reg_value1 == reg_value2:
            # set the E flag to 1 or 0
            self.flag = self.flag | 0b00000001
        else:
            self.flag = self.flag & 0b11111110
            #set the L flag to 1 or 0
        if reg_value1 < reg_value2:
            self.flag = self.flag | 0b00000100
        else:
            self.flag = self.flag & 0b11111011

        if reg_value1 > reg_value2:
            self.flag = self.flag | 0b00000010
        else:
            self.flag = self.flag & 0b11111101

    def jmp(self, reg_a, reg_b):
        address_value = self.reg[reg_a]
        self.pc = address_value

    def jeq(self, reg_a, reg_b):
        E_flag = self.flag & 0b00000001
        if E_flag == 1:
            self.jmp(reg_a, reg_b)
        else:
            self.pc += 2

    def jne(self, reg_a, reg_b):
        #if E flag is 0, jump to address stored in register
        E_flag = self.flag & 0b00000001
        if E_flag == 0:
            self.jmp(reg_a, reg_b)
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""

        while self.running:
            IR = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            sets_the_pc = ((IR >> 4) & 0b0001) == 1

            if not sets_the_pc:
                op_size = IR >> 6
                self.pc += (1 + op_size)

            if IR in self.branchtable:
                operation = self.branchtable[IR]
                operation(operand_a, operand_b)
