
import dis
import odoo.tools.safe_eval as se
from opcode import opmap, opname

print("NOT_TAKEN in opmap:", 'NOT_TAKEN' in opmap)
if 'NOT_TAKEN' in opmap:
    code = opmap['NOT_TAKEN']
    print("NOT_TAKEN code:", code)
    print("NOT_TAKEN in _SAFE_OPCODES:", code in se._SAFE_OPCODES)

print("JUMP in opmap:", 'JUMP' in opmap)
if 'JUMP' in opmap:
    code = opmap['JUMP']
    print("JUMP code:", code)
    print("JUMP in _SAFE_OPCODES:", code in se._SAFE_OPCODES)

# Find what 41 is (Odoo reported NOT_TAKEN for it?)
# No, Odoo didn't report a code, it reported the name.
