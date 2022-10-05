import sys
import secrets

if sys.version_info<(3,9):
    print("You need a newer version of python installed to run this program, At least python3.9.")
    exit(1)

import traceback

from base import BaseMath, convert_primitive_type
from matrice import Matrice, MatriceError, init_matrice, visualize_operation, show
from debugprinter import PrettyPrinter

printer = PrettyPrinter()
printer.debug=True

global_namespace: dict[str,BaseMath] = {}


class StreamStruct:
    def __init__(self, cin=sys.stdin, cout=sys.stdout, cerr=sys.stderr):
        self.cin=cin
        self.cout=cout
        self.cerr=cerr
    
    def readline(self):
        return self.cin.readline()
    
    def write(self, string:str):
        self.cout.write(string)
        self.cout.flush()
    
    def writeline(self, string:str):
        self.write(string+'\n')
    
    def _print(self, *args, **kw):
        kw.update({'file':self.cout})
        print(*args, **kw)
        self.cout.flush()
    
    def _(self, *args, **kw):
        return self._print(*args, **kw)
    
    def input(self, prompt):
        self._print(prompt, end='')
        return self.readline().strip('\n').strip('\r\n')


def interpreter(stream:StreamStruct, namespace=global_namespace):
    token=secrets.token_hex(3)
    stream._print("Welcome to the math sandbox interpreter!\nFeel free to do as you please here!\nTo see commands, enter 'help'.")
    while True:
        try:
            cmd, *args = stream.input(">+>").upper().split(' ')
            printer.print_debug("DEBUG Input", {'Command':cmd, 'Arguments':args})
            if not len(cmd):
                continue
            if cmd in ['EXIT', 'EXIT()']:
                stream._print("Exiting sandbox...")
                return
            elif cmd in ['HELP']:
                stream._print("""\
{<CommandName>[|Alias[|Alias...]]} {Subcomands} <Args> Description.\n\
{EXIT|EXIT()} Exit\n\
{CREATE|C} {MATRICE} [<Name>] Creates a matrice with given name or show prompt to get matrice name.\n\
{DEFINE|DEF} [<SimpleAssigment> [<SimpleAssigment> [<SimpleAssigment>...]]] Defines a value with the value passed. SimpleAssigment is in the form of \"C=A\" Where A is an Int or Float and C is the name to assign the value to.\n\
{LIST|LS} Prints all created & defined variables\n\
{SHOW|DISPLAY|S|D} [<Name> [<Name> [<Name>...]]] Shows the value of the variables with given names.\n\
{OP|OPERATE|EXP}[R] [<SimpleStatement> [<SimpleStatement> [<SimpleStatement>...]]] Defines a value with the statement passed and shows the operation visually. SimpleStatement is in the form of \"C=A{Op}B\" Where A and B must be an already defined variable and C is the name to assign the value to, and Op is operations [+,-,*].\n""".strip())
            elif cmd in ['C', 'CREATE']:
                if len(args) == 0:
                    continue
                if args[0] == 'MATRICE':
                    if len(args) <=1:
                        args.append(stream.input('Matrice Name(s):').upper().split())
                    for name in args[1:]:
                        namespace[name] = init_matrice(print_matrice=False)
                        stream._print("|+|Created Object '{name}' => {object}".format(name=name, object=namespace[name]))
            elif cmd in ['DEF', 'DEFINE', 'DEF*', 'DEFINE*']:
                if len(args) == 0:
                    if cmd.endswith('*'):
                        stream._print("Define variables with primitive types and ")
                        while True:
                            inp = stream.input("+(DEF)>").upper()
                            if not inp:
                                break
                            args.extend(inp.split(' '))
                    else:
                        args.extend(stream.input("+(DEF)>").upper().split(' '))
                for arg in args:
                    name,value=arg.split('=',1)
                    exec(f"__HIDDEN_TMP__={value}", {}, namespace) # Don't pollute namespace
                    print(namespace)
                    namespace[name]=convert_primitive_type(namespace.get('__HIDDEN_TMP__'))
                    stream._print("|+|Defined Object '{name}' => {object}".format(name=name, object=namespace[name]))
            elif cmd in ['SUM']:
                if len(args) == 0:
                    args.extend(stream.input("Matrice Name:").upper().split(' '))
                for i, name in enumerate(args):
                    obj = namespace[name]
                    if isinstance(obj, Matrice):
                        stream._print("|+{i}|{name}.sum() => {res}".format(i=i+1, name=name, object=obj, res=obj.sum()))
            elif cmd in ['TP', 'TRANSPOSE']:
                if len(args) == 0:
                    args.extend(stream.input("Matrice Name:").upper().split(' '))
                for i, name in enumerate(args):
                    obj = namespace[name]
                    if isinstance(obj, Matrice):
                        stream._print("|+{i}|{name}.transpose()\n{res}\n".format(i=i+1, name=name, object=obj, res=obj.transpose().get_str()))
            elif cmd in ['LS', 'LIST']:
                stream._print("Objects List:")
                for i, (name, obj) in enumerate(namespace.items()):
                    if name.startswith("__HIDDEN"):
                        continue
                    stream._print("|+{i}|{name} {object}".format(i=i+1, name=name, object=obj))
                stream._print("")
            elif cmd in ['S','SHOW', 'D', 'DISPLAY']:
                for arg in args:
                    if arg.startswith('__HIDDEN'):
                        continue
                    if (obj:=namespace.get(arg)) is not None:
                        stream._print("|+|{name} {object}".format(name=arg, object=obj))
                        obj.show(file=stream.cout)
                        stream._print("")
                    else:
                        stream._print("Object with name '{}' is not found.".format(arg))
            elif cmd in ['OP', 'OPR', 'OPERATE', 'OPERATER', 'EXP', 'EXPR']:
                right=cmd.endswith('R')
                if len(args)==0:
                    args = stream.input("+(OP)>").upper().split()
                if (operation:=' '.join(args)).__contains__('='):
                    try:
                        assign_name,operation=operation.split('=',1)
                        for op in ['*', '+','-']:
                            if op in operation:
                                op_args = operation.split(op,1)
                                namespace[assign_name] = visualize_operation(namespace[op_args[0]], namespace[op_args[1]], op, result_right=right)
                                break
                    except:
                        exec(' '.join(args), namespace, {'vop':visualize_operation})
                else:
                    for op in ['*', '+','-']:
                        if op in operation:
                            op_args = operation.split(op,1)
                            visualize_operation(namespace[op_args[0]], namespace[op_args[1]], op)
                            break
            else:
                if cmd in ['DEV', 'CONSOLE', 'DEVCON']:
                    _globals = globals()
                    _globals.update(locals())
                    [_globals.pop(k) for k in ['_globals', 'cmd', 'args']]
                    while True:
                        try:
                            command=stream.input("(PyConsole)>>")
                            if command.upper() in ['EXIT', 'EXIT()']:
                                break
                            exec(f"__HIDDEN_TMP__={command}\nstream._print(__HIDDEN_TMP__) if __HIDDEN_TMP__ is not None else None", _globals, namespace)
                        except Exception as exc:
                            stream._print("Err:{}".format(exc))
                else:
                    stream._print("Command is not found.")
        except MatriceError:
            stream._print("A matrice error has been encountered. Err:{}".format(traceback.format_exc()))
        except Exception as exc:
            # stream._print(traceback.format_exc())
            stream._print("Err:{}".format(exc))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'd':
        printer.debug=not printer.debug
    interpreter(StreamStruct())
