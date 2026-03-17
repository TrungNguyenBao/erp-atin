
import dis
import odoo.tools.safe_eval as safe_eval

all_opcodes = set(dis.opname)
allowed_opcodes = {dis.opname[x] for x in safe_eval._SAFE_OPCODES}

# Opcodes that are typically safe but might be missing due to version changes
potential_new_safe = [
    'LOAD_SMALL_INT',
    'LOAD_CONST_IMMORTAL',
    'LOAD_FAST_AND_CLEAR',
    'LOAD_FAST_CHECK',
    'STORE_FAST_LOAD_FAST',
    'STORE_FAST_STORE_FAST',
    'LOAD_FAST_LOAD_FAST',
    'CALL_KW',
    'CONVERT_VALUE',
    'FORMAT_SIMPLE',
    'FORMAT_WITH_SPEC',
    'SET_FUNCTION_ATTRIBUTE'
]

missing = [op for op in potential_new_safe if op in dis.opmap and op not in allowed_opcodes]
print("Missing:", missing)

# Print all available opcodes for reference
# print("Available:", sorted(dis.opname))
