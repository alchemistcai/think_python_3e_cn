'''让ThinkPython 3e笔记正确运行的准备步骤。'''

import contextlib
import io
import re


def extract_function_name(text):
    """搜索函数的定义并返回函数名。

    text: str,一串包含函数定义的字符串。

    返回值: 字符串中函数定义的函数名，如果没有找到，则返回None。
    """
    pattern = r"def\s+(\w+)\s*\("
    match = re.search(pattern, text)
    if match:
        func_name = match.group(1)
        return func_name
    else:
        return None


# the functions that define cell magic commands are only defined
# if we're running in Jupyter.

try:
    from IPython.core.magic import register_cell_magic
    from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

    @register_cell_magic
    def add_method_to(args, cell):

        # 返回此单元格定义的函数名
        func_name = extract_function_name(cell)
        if func_name is None:
            return f"此单元格未定义任何新函数。"

        # 获得我们要添加函数到哪个类中
        namespace = get_ipython().user_ns
        class_name = args
        cls = namespace.get(class_name, None)
        if cls is None:
            return f"找不到类'{class_name}'。"

        # 如果已经定义，保存旧版本的函数
        old_func = namespace.get(func_name, None)
        if old_func is not None:
            del namespace[func_name]

        # 执行单元格，以定义函数
        get_ipython().run_cell(cell)

        # 获得新定义的函数
        new_func = namespace.get(func_name, None)
        if new_func is None:
            return f"此单元格未定义函数{func_name}。"

        # 添加函数到指定类中，从命名空间中删除该函数
        setattr(cls, func_name, new_func)
        del namespace[func_name]

        # 恢复旧版本的函数到命名空间中
        if old_func is not None:
            namespace[func_name] = old_func

    @register_cell_magic
    def expect_error(line, cell):
        try:
            get_ipython().run_cell(cell)
        except Exception as e:
            get_ipython().run_cell("%tb")

    @magic_arguments()
    @argument("exception", help="要捕获的异常类型")
    @register_cell_magic
    def expect(line, cell):
        args = parse_argstring(expect, line)
        exception = eval(args.exception)
        try:
            get_ipython().run_cell(cell)
        except exception as e:
            get_ipython().run_cell("%tb")

    def traceback(mode):
        """设置追踪模式。

        mode: str,追踪模式
        """
        with contextlib.redirect_stdout(io.StringIO()):
            get_ipython().run_cell(f"%xmode {mode}")

    traceback("Minimal")
except (ImportError, NameError):
    print("警告: 找不到IPython，单元格魔术方法未定义。")
