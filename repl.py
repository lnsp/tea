#!/usr/bin/python3
"""Command line runtime for Tea."""

import runtime.lib
import sys
from runtime import lexer, parser, env, flags

TEA_VERSION = "0.0.5-dev"
TEA_TITLE = "Tea @" + TEA_VERSION
CLI_ESCAPE = "\\"
CLI_SYMBOL = ">> "
CLI_SPACE = " " * 3
CLI_RESULT = "<- "
CLI_ERROR = "!! "

class CLISupportLib(object):
    def _print_operation():
        def do_print(context):
            """Print a value."""
            var_a = context.find("id", "a")
            print(var_a.data)
            return env.Value(env.NULL)
        print_node = env.FunctionBinding(do_print)
        signatures = [
            env.Signature([
                env.Value(env.ANY, None, "a"),
            ], print_node)
        ]
        return env.Function(signatures, "print")
    PRINT_FUNCTION = _print_operation()
    EXPORTS = [
        PRINT_FUNCTION,
    ]

def run_script(name, context):
    script = ""
    with open(name, "r") as f:
        script = ' '.join(line for line in f)

    tokens = lexer.run(script)
    tree = parser.generate(tokens)
    return tree.eval(context)


def interpret(expression, context):
    """Interpret an expression by tokenizing, parsing and evaluating."""
    if expression == CLI_ESCAPE + "exit":
        context.flags.append("exit")
        return
    if expression == CLI_ESCAPE + "debug":
        flags.debug = not flags.debug
        return "Debug mode %s" % ("on" if flags.debug else "off")

    try:
        tokens = lexer.run(expression)
        tree = parser.generate(tokens)
        return CLI_RESULT + tree.eval(context).format()
    except (env.FunctionException, env.OperatorException, env.RuntimeException, parser.ParseException) as e:
        return CLI_ERROR + str(e)


def main():
    """Run the CLI."""
    # print application title
    print(TEA_TITLE)

    # run REPL
    context = env.empty_context()
    context.load(runtime.lib)
    context.load(CLISupportLib)

    if len(sys.argv) > 1:
        run_script(sys.argv[1], context)
        return

    while "done" not in context.flags:
        output = interpret(input(CLI_SYMBOL), context)
        while "continue" in context.flags:
            output = interpret(input(CLI_SPACE), context)
        if "exit" in context.flags:
            return
        print(output)

if __name__ == "__main__":
    main()
