import os
import imp
import json

root = os.path.split(__file__)[0]

# add project folder to sys path
os.sys.path.insert(0, os.path.join(root, '..'))

# set environ variable
os.environ['EJTP_IDENTITY_CACHE_PATH'] = os.path.join(root, '../resources/examplecache.json')


# load ejtp-console as a module
with open(os.path.join(root, 'ejtp-console'), 'rb') as fp:
    console = imp.load_module('console', fp, 'ejtp-console', ('.py', 'rb', imp.PY_SOURCE))


# define input messages
inputs = [
    "mitzi@lackadaisy.com",
    "send",
    "victor@lackadaisy.com",
    json.dumps("first message"),
    "messages",
    "eval",
    "2 ** 10",
    "set client",
    "victor@lackadaisy.com",
    "send",
    "mitzi@lackadaisy.com",
    json.dumps("another message"),
    "messages",
    "quit"
]

def input_func(prompt):
    global inputs
    print prompt,
    try:
        obj = inputs.pop(0)
    except IndexError:
        raise KeyboardInterrupt()
    print "$", obj
    return obj

# override raw_input builtin
console.raw_input = input_func

# run interactive console
inter = console.Interactive()
inter.repl()

