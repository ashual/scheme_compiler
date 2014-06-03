
class LabelGen:
    CurrentLabel = 0
    @staticmethod
    def Next():
        LabelGen.CurrentLabel += 1
        return "L" + str(LabelGen.CurrentLabel)
    @staticmethod
    def Next(desc):
        LabelGen.CurrentLabel += 1
        return "L" + desc + str(LabelGen.CurrentLabel)
    @staticmethod
    def Reset():
        LabelGen.CurrentLabel = 0

class ConstantFucntionsManager:
    functions = {"BOOLEAN?" : "BOOLEAN", "CAR":"CAR", "CDR":"CDR", "CONS":"CONS", "EQ?":"EQ", \
                "INTEGER?":"INTEGER", "NULL?":"NULL", "NUMBER?":"NUMBER", "PAIR?":"PAIR", "PROCEDURE?":"PROCEDURE",\
                "STRING?":"STRING", "SYMBOL?":"SYMBOL", "VECTOR?":"IS_VECTOR", "ZERO?":"ZERO",\
                "STRING-LENGTH":"STRINGLENGTH", "SYMBOL->STRING":"SYMBOLTOSTRING","VECTOR-LENGTH":"VECTORLENGTH",\
                "VECTOR-REF":"VECTORREF","STRING->SYMBOL":"STRINGTOSYMBOL", "CHAR?":"CHAR","CHAR->INTEGER":"CHARTOINTEGER", \
                "INTEGER->CHAR":"INTEGERTOCHAR", "STRING-REF":"STRINGREF","LIST":"LIST", "MAP":"MAP", "VECTOR":"VECTOR", \
                "MAKE-VECTOR":"MAKEVECTOR", "MAKE-STRING":"MAKESTRING", \
                "+":"PLUS", "*":"MULT" ,"-":"MINUS","=":"EQUAL", ">":"GREATER","<":"LOWER", "APPEND":"APPEND", \
                "APPLY":"APPLY", "/":"DIVIDE", "REMAINDER":"REMAINDER", "LIST->VECTOR": "LISTTOVECTOR" }

    def __init__(self, VarTable):
        self.VarTable = VarTable
        for func in self.functions:
            VarTable.AddFreeVar(func)
    def Reset(self, VarTable):
        for func in self.functions:
            self.VarTable.AddFreeVar(func)
    def CodeGen(self):
        OutputCode = "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Build Constant functions ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        for func in self.functions:
            OutputCode += "\n"
            OutputCode += "// (((((((((((((((((((((((((((((((Build function: " + str(func) + " )))))))))))))))))))))))))"
            OutputCode += "\n"
            OutputCode += "PUSH(LABEL(L_" +  self.functions[func] + "));"
            OutputCode += "\n"
            OutputCode += "PUSH(FPARG(0));" #push the global env
            OutputCode += "\n"
            OutputCode += "CALL(MAKE_SOB_CLOSURE);"
            OutputCode += "\n"
            OutputCode += "DROP(2);"
            OutputCode += "\n"
            OutputCode += "MOV(IND(" + self.VarTable.GetAddress(func) + "),R0);"
            OutputCode += "\n"
        OutputCode += "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Finish Build Constant functions ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        OutputCode += "\n"

        return OutputCode

class VariableTable:
    vars = dict()

    NextFreeSpace = 10 # in 1 sit the entry for the symbol table in 2 and 3 sit the dummy env. 4-9 void,nil,true,false

    def Reset(self):
        self.vars = dict()
        self.NextFreeSpace = 10

    def AddFreeVar(self, FreeVar):
        if FreeVar not in self.vars:
            self.vars[FreeVar] =  self.NextFreeSpace
            self.NextFreeSpace += 1
    def GetAddress(self, FreeVar):
        if FreeVar not in self.vars:
            raise SyntaxError
        else:
            return str(self.vars[FreeVar])
    def CodeGen(self):
        OutputCode = "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Create Var Table ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        OutputCode += "\n"
        OutputCode += "// Allocate space for all the free vars"
        OutputCode += "\n"
        OutputCode += "PUSH(IMM(" + str(len(self.vars)) + "));"
        OutputCode += "\n"
        OutputCode += "CALL(MALLOC);"
        OutputCode += "\n"
        OutputCode += "DROP(1);"
        OutputCode += "\n"
        OutputCode += "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Finish Create Var Table ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        OutputCode += "\n"

        return OutputCode

class ConstantTable:
    constans = dict()
    NextFreeSpace = 4

    def __init__(self, InitList, NextFreeSpace):
        self.NextFreeSpace = 4 # After the pointer to the symbol table and the dummy env
        self.InitList = InitList

        self.Comment("&&&&&&&&&&&&&Constant table Initialize begin - void,nil,true,false &&&&&&&&&&&&&&&&&&& ")
        for cons in InitList:
            self.GetAddr(cons)
        self.Comment("&&&&&&&&&&&&&Constant table Initialize end - void,nil,true,false &&&&&&&&&&&&&&&&&&& ")

        self.InitOutputCode = self.OutputCode

        self.NextFreeSpace = NextFreeSpace
        self.OutputCode = ""
        self.Comment("&&&&&&&&&&&&&Constant table Initialize begin - dynmic constants &&&&&&&&&&&&&&&&&&& ")
    def Reset(self, NextFreeSpace):
        self.constans = dict()
        self.InitOutputCode = ""
        self.OutputCode = ""

        self.NextFreeSpace = 4

        self.Comment("&&&&&&&&&&&&&Constant table Initialize begin - void,nil,true,false &&&&&&&&&&&&&&&&&&& ")
        for cons in self.InitList:
            self.GetAddr(cons)
        self.Comment("&&&&&&&&&&&&&Constant table Initialize end - void,nil,true,false &&&&&&&&&&&&&&&&&&& ")

        self.InitOutputCode = self.OutputCode

        self.NextFreeSpace = NextFreeSpace
        self.OutputCode = ""
        self.Comment("&&&&&&&&&&&&&Constant table Initialize begin - dynmic constants &&&&&&&&&&&&&&&&&&& ")
    def CodeGen(self):
        self.Comment("&&&&&&&&&&&&&Constant table Initialize end - dynmic constants &&&&&&&&&&&&&&&&&&& ")
        self.Enterl("  ")
        return self.OutputCode

    OutputCode = ""
    InitOutputCode = ""
    def Enterl(self, line):
        self.OutputCode += line
        self.OutputCode += "\n"
    def Comment(self, desc):
        self.OutputCode += "//"
        self.OutputCode += desc
        self.OutputCode += "\n"

    def GetAddr(self, item):
        if item not in self.constans:
            self.Enterl(item.EnterToConstantTable())
            self.constans[item] =  self.NextFreeSpace  #save the index of the constant in the memory
            self.NextFreeSpace += item.SpaceInMemory()

        return str(self.constans[item])

class SymbolTable:
    Symbols = []

    def __init__(self, StartPoint, NilAddress, ConsTalbe):
        self.StartPoint = StartPoint
        self.NilAddress = NilAddress
        self.ConsTable = ConsTalbe

    def Reset(self):
        self.Symbols = []

    def AddSymbol(self, item):
        self.Symbols.append(item)

    def CodeGen(self):
        OutputCode = "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Create Symbol Table ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        OutputCode += "\n"

        OutputCode += "PUSH(R1);"
        OutputCode += "\n"
        OutputCode += "MOV(R1," + str(self.StartPoint) + ");"
        OutputCode += "\n"

        for item in self.Symbols:
            itemAddr = self.ConsTable.GetAddr(item)
            OutputCode += "// Allocate  next symbol"
            OutputCode += "\n"
            OutputCode += "PUSH(IMM(2));"
            OutputCode += "\n"
            OutputCode += "CALL(MALLOC);"
            OutputCode += "\n"
            OutputCode += "DROP(1);"
            OutputCode += "\n"
            OutputCode += "MOV(IND(R1), R0);"
            OutputCode += "\n"
            OutputCode += "MOV(IND(R0)," + str(itemAddr) + ");"
            OutputCode += "\n"
            OutputCode += "INCR(R0);"
            OutputCode += "\n"
            OutputCode += "MOV(R1, R0);"
            OutputCode += "\n"

        OutputCode += "MOV(IND(R1)," + str(self.NilAddress) + ");"
        OutputCode += "\n"
        OutputCode += "POP(R1);"
        OutputCode += "\n"
        OutputCode += "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Finish Create Symbol Table ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        OutputCode += "\n"

        return OutputCode