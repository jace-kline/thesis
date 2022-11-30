
parent = "DataType"
subclasses = [
    "DataTypeFloat",
    "DataTypeFunctionPrototype",
    "DataTypeInt",
    "DataTypePointer",
    "DataTypeStruct",
    "DataTypeUndefined",
    "DataTypeUnion",
    "DataTypeVoid",
    "DataTypeArray"
]

for subclass in subclasses:
    print("{} <|-- {}".format(parent, subclass))