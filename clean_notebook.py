import json
import sys

notebook_path = sys.argv[1]

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def remove_jetTransient(cell):
    if 'outputs' in cell:
        for output in cell['outputs']:
            if 'jetTransient' in output:
                del output['jetTransient']

for cell in nb['cells']:
    remove_jetTransient(cell)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
