from pathlib import Path
import ast,copy,hashlib
SOURCE=Path('/workspace/ByteNDT-B014-C2-TRUE-TWIN/B014_C2_TOUTES_VUES_Z_CORRIGE_V2.py');tree=ast.parse(SOURCE.read_text());nodes=[]
for n in tree.body:
 if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=='st'and n.value.func.attr=='set_page_config':break
 if isinstance(n,(ast.Import,ast.ImportFrom)):
  if isinstance(n,ast.Import)and any(a.name=='streamlit'for a in n.names):continue
  nodes.append(n)
 elif isinstance(n,(ast.Assign,ast.AnnAssign)):nodes.append(n)
 elif isinstance(n,ast.FunctionDef):
  n=copy.deepcopy(n);n.decorator_list=[d for d in n.decorator_list if not (isinstance(d,ast.Call)and isinstance(d.func,ast.Attribute)and isinstance(d.func.value,ast.Name)and d.func.value.id=='st')];nodes.append(n)
ctx={'__file__':str(SOURCE),'__name__':'c2_reference'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),ctx)
