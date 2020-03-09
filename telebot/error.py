import sys
import traceback

def foo(str):
	traceback.print_stack(limit = -1)
	exit("  "+str)

sys.modules[__name__] = foo
