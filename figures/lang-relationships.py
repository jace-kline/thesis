from typing import List

class Address(object):
    pass

class AbsoluteAddress(Address):
    pass

class StackAddress(Address):
    pass

class RegisterAddress(Address):
    pass

class RegisterOffsetAddress(Address):
    pass

class AddressLiveRange(object):
    def __init__(
        self,
        addr: Address,
        startpc: Address,
        endpc: Address
    ):
        self.addr = addr
        self.startpc = startpc
        self.endpc = endpc
    

class DataType(object):
    def __init__(
        self,
        metatype: int,
        size: int
    ):
        self.metatype = metatype
        self.size = size

class DataTypeFloat(DataType):
    pass

class DataTypeFunctionPrototype(DataType):
    pass

class DataTypeInt(DataType):
    pass

class DataTypePointer(DataType):
    pass

class DataTypeStruct(DataType):
    pass

class DataTypeUndefined(DataType):
    pass

class DataTypeUnion(DataType):
    pass

class DataTypeVoid(DataType):
    pass

class DataTypeArray(DataType):
    pass

class Variable(object):
    def __init__(self,
        name: str,
        liveranges: List[AddressLiveRange],
        dtype: DataType
    ):
        self.name: str = name
        self.liveranges: List[AddressLiveRange] = liveranges
        self.dtype: DataType = dtype

class Function(object):
    def __init__(self,
        name: str,
        startaddr: Address,
        endaddr: Address,
        vars: List[Variable],
        params: List[Variable],
        rettype: DataType,
    ):
        self.name = name
        self.startaddr = startaddr
        self.endaddr = endaddr
        self.vars = vars
        self.params = params
        self.rettype = rettype

class ProgramInfo:
    def __init__(self,
        functions: List[Function],
        globals: List[Variable]
    ):
        self.functions = functions
        self.globals = globals