def print_exception(exception):
    print(fancy_exception(exception))

def fancy_exception(exception):
    tb = exception.__traceback__
    l = []
    while tb is not None:
        file_name = tb.tb_frame.f_code.co_filename
        line = tb.tb_lineno
        tb = tb.tb_next
        l.append(type(exception).__name__ + ': ' + str(exception) + ' on line ' + str(line) + " in '{}'".format(file_name))
    return '\n'.join(l)

def short_exception(exception):
    tb = exception.__traceback__
    l = []
    while tb is not None:
        file_name = tb.tb_frame.f_code.co_filename
        line = tb.tb_lineno
        tb = tb.tb_next
        return type(exception).__name__ + ': ' + str(exception)