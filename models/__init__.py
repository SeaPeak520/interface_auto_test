import types

def load_module_functions(module):
    """ 获取 module中方法的名称和所在的内存地址 """
    return {
        name: item
        for name, item in vars(module).items()
        if isinstance(item, types.FunctionType)
    }



