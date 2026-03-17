
import dis
import odoo.tools.safe_eval as safe_eval

allowed_opcodes = {dis.opname[x] for x in safe_eval._SAFE_OPCODES}
all_available_opcodes = set(dis.opname)

# List of opcodes that are usually considered "unsafe" or shouldn't be in safe_eval
# We don't want to blindly add everything.
unsafe_potential = {
    'IMPORT_STAR', 'IMPORT_NAME', 'IMPORT_FROM',
    'STORE_ATTR', 'DELETE_ATTR',
    'STORE_GLOBAL', 'DELETE_GLOBAL'
}

missing = []
for op in sorted(all_available_opcodes):
    if op in dis.opmap and op not in allowed_opcodes and op not in unsafe_potential:
        missing.append(op)

print("Missing (excluding known unsafe):", missing)
