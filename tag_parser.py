
from  CodeGenTools import ConstantTable, LabelGen, VariableTable, ConstantFucntionsManager, SymbolTable
import sexprs

class AbstractSchemeExpr:
    @staticmethod
    def parseRec(input):
        isSuccess, parsingObject =  ConstantFactory.parseRec(input)
        if(isSuccess):
            return parsingObject
        elif(AbstractLambda.instanceof(input)):
            return LambdaFactory.CreateLambda(input)
        elif(QuasiQuote.instanceof(input)):
            return AbstractSchemeExpr.parseRec(QuasiQuote.MyExpandQQ(input))
        elif(Def.instanceof(input)):
            return Def(input)
        elif(IfThenElse.instanceof(input)):
            return IfThenElse(input)
        elif(Or.instanceof(input)):
            return Or(input)
        elif(Cond.instanceof(input)):
            return Cond.ConvertToIf(input)
        elif(And.instanceof(input)):
            return And.ConvertToIf(input)
        elif(Let.instanceof(input)):
            return Let.ConvertToApplic(input)
        elif(LetAsterisk.instanceof(input)):
            return LetAsterisk.Parse(input)
        elif(Letrec.instanceof(input)):
            return Letrec.ConvertToYag(input)
        elif(Applic.instanceof(input)):
            return Applic(input)
        elif(Variable.instanceof(input)):
            return Variable(input)
        elif(isinstance(input, AbstractSchemeExpr)):
            return input
        else:
            return False
    @staticmethod
    def parse(input):
        result, rem = sexprs.AbstractSexpr.readFromString(input)
        return  AbstractSchemeExpr.parseRec(result), rem
    def semantic_analysis(self):
        return self.debruijn().annotateTC()

    OutputCode = ""
    TempOutputCode = ""
    def Enterl(self, line):
        self.OutputCode += line
        self.OutputCode += "\n"
    def EnterT(self, line):
        self.TempOutputCode += line
        self.TempOutputCode += "\n"
    def EnterTTab(self,line):
        self.TempOutputCode+=("\t"+line+"\n")
    def Comment(self, desc):
        self.TempOutputCode += "//"
        self.TempOutputCode += desc
        self.TempOutputCode += "\n"
    def CodeGenRec(self):
        self.EnterTTab('printf("%s", "TBD");')
        return self.TempOutputCode
    def code_gen(self):
        return self.CodeGenRec()

    def __str__(self):
        return ""

    def debruijn(self):
        return self.debrujinParams(self,[[]],[])
    def debrujinParams(self,e,B,p):
        if isinstance(e,Variable):
            if str(e) in p:
                minor=p.index(str(e))
                return VarParam(e,minor)
            elif findBound(e,B)!=-1:
                major,minor=findBound(e,B)
                return VarBound(e,major,minor)
            else:
                return VarFree(e)
        elif isinstance(e,LambdaSimple):
            return LambdaSimple(e.Params,self.debrujinParams(e.Body,[p]+B,list(map(str,e.Params))))
        elif isinstance(e,LambdaVar):
            return LambdaVar(e.OneParam,self.debrujinParams(e.Body,[p]+B,[str(e.OneParam)]))
        elif isinstance(e,LambdaOpt):
            return LambdaOpt(e.Params,self.debrujinParams(e.Body,[p]+B,list(map(str,e.Params))))
        elif isinstance(e,Applic):
            newParams=list()
            for param in e.ParamList:
                newParams.append( self.debrujinParams(param,B,p))
            e.ParamList=newParams
            e.Lambda = self.debrujinParams(e.Lambda,B,p)
            return e
        elif isinstance(e,Def):
            e.variable = self.debrujinParams(e.variable,B,p)
            e.Value= self.debrujinParams(e.Value,B,p)
            return e
        elif isinstance(e,IfThenElse):
            e.IfCondition=self.debrujinParams(e.IfCondition,B,p)
            e.IfTrue=self.debrujinParams(e.IfTrue,B,p)
            e.IfFalse=self.debrujinParams(e.IfFalse,B,p)
            return e
        elif isinstance(e,Or):
            OrList=[]
            for item in e.OrConditions:
                OrList.append(self.debrujinParams(item,B,p))
            e.OrConditions=OrList
            return e
        else:
            return e

    def annotateTC(self):
        return self.Atp(self, False)

    def Atp(self, exp, tp):
        if(isinstance(exp, Or)):
            NewLastCond = self.Atp(exp.OrConditions.pop(), tp)
            NewOrConditions = list(map((lambda x:  self.Atp(x, False)),exp.OrConditions))
            NewOrConditions.append(NewLastCond)
            exp.OrConditions =   NewOrConditions
        elif (isinstance(exp, Def)):
            exp.Value = self.Atp(exp.Value, False)
        elif (isinstance(exp, IfThenElse)):
            exp.IfCondition = self.Atp(exp.IfCondition, False)
            exp.IfTrue = self.Atp(exp.IfTrue, tp)
            exp.IfFalse = self.Atp(exp.IfFalse, tp)
        elif (isinstance(exp, AbstractLambda)):
            exp.Body = self.Atp(exp.Body, True)
        elif(isinstance(exp, Applic)):
            if(tp):
                exp =    ApplicTP(self.Atp(exp.Lambda, False), list(map((lambda x:  self.Atp(x, False)), exp.ParamList) ))
            else:
                exp.Lambda = self.Atp(exp.Lambda, False)
                exp.ParamList = list(map((lambda x:  self.Atp(x, False)), exp.ParamList))
        return exp

def findBound(e,B):
    for i,lst in enumerate(B):
        for j,boundVar in enumerate(lst):
            if str(boundVar) == str(e):
                return i, j
    return -1

def NextItem(input):
    Next = input.Item2

    if(not isinstance(Next, sexprs.Pair)):
        return False

    return Next

def StartWith(Prefix, input):
    if(isinstance(input, sexprs.Pair)):
        Label = input.Item1
        return (isinstance(Label, sexprs.Symbol) and (str(Label) == Prefix))
    else:
        return False

class SyntaxError(Exception):
    pass

class QuasiQuote:
    @staticmethod
    def instanceof(instance):
        item = instance
        return ((isinstance(item,sexprs.Pair)) and (isinstance(item.Item1,sexprs.Symbol)) and (str(item.Item1)=="QUASIQUOTE"))
    @staticmethod
    def MyExpandQQ(MyE):
        e = MyE.Item2.Item1
        return QuasiQuote.ExpandQQ(e)
    @staticmethod
    def ExpandQQ(e):
        if(QuasiQuote.Unqouted(e)):
            return e.Item2.Item1
        elif(QuasiQuote.UnqouteSplicing(e)):
            print("unquote-splicing here makes no sense!")
            raise SyntaxError
        elif ((isinstance(e,sexprs.Pair))):
            if QuasiQuote.UnqouteSplicing(e.Item1):
                if(isinstance(e.Item2,sexprs.Nil)):
                    return sexprs.Pair(sexprs.Symbol("append"), sexprs.Pair((((e.Item1).Item2)).Item1, sexprs.Nil()))
                else:
                    return sexprs.Pair(sexprs.Symbol("append"), sexprs.Pair((((e.Item1).Item2)).Item1,sexprs.Pair(QuasiQuote.ExpandQQ(e.Item2), sexprs.Nil())))
            elif  QuasiQuote.UnqouteSplicing(e.Item2):
                return sexprs.Pair(sexprs.Symbol("cons"),sexprs.Pair(QuasiQuote.ExpandQQ(e.Item1),sexprs.Pair(((e.Item2).Item2).Item1, sexprs.Nil())))
            else:
                return sexprs.Pair(sexprs.Symbol("cons"),sexprs.Pair(QuasiQuote.ExpandQQ(e.Item1),sexprs.Pair(QuasiQuote.ExpandQQ(e.Item2), sexprs.Nil())))
        elif((isinstance(e,sexprs.Vector))):
            return sexprs.Pair(sexprs.Symbol("list->vector"),sexprs.Pair(QuasiQuote.ExpandQQ(QuasiQuote.VectorToList(e.values)) ,sexprs.Nil()))
        elif((isinstance(e,sexprs.Nil)) or (isinstance(e,sexprs.Symbol))):
            return sexprs.Pair(sexprs.Symbol("quote"),sexprs.Pair(e,sexprs.Nil()))
        else:
            return e
    @staticmethod
    def VectorToList(items):
        if items:
            return sexprs.Pair(items[0], QuasiQuote.VectorToList(items[1:]))
        else:
            return sexprs.Nil()
    @staticmethod
    def Qoute(tag,e):
        return ((isinstance(e,sexprs.Pair)) and
                (str(e.Item1)==tag) and
                (isinstance(e.Item2,sexprs.Pair)) and
                (isinstance(e.Item2.Item2,sexprs.Nil)))
    @staticmethod
    def Unqouted(q):
        return QuasiQuote.Qoute("UNQUOTE", q)
    @staticmethod
    def UnqouteSplicing(q):
        return QuasiQuote.Qoute("UNQUOTE-SPLICING", q)

class ConstantFactory:
    @staticmethod
    def parseRec(input):
        return ConstantFactory.InnerParseRec(input, False)
    @staticmethod
    def InnerParseRec(input, IsInQoute):
        if(IntegerConstant.instanceof(input)):
            return (True, IntegerConstant(input))
        elif(BooleanConstant.instanceof(input)):
            return (True, BooleanConstant(input))
        elif(FractionConstant.instanceof(input)):
            return (True, FractionConstant(input))
        elif(CharConstant.instanceof(input)):
            return (True,CharConstant(input))
        elif(VoidConstant.instanceof(input)):
            return (True,VoidConstant(input))
        elif(StringConstant.instanceof(input)):
            return (True,StringConstant(input))
        elif(IsInQoute):
            if(SymbolConstant.instanceof(input)):
                return (True,SymbolConstant(input))
            elif(PairConstant.instanceof(input)):
                return (True,PairConstant(input))
            elif(NilConstant.instanceof(input)):
                return (True,NilConstant(input))
            elif(VectorConstant.instanceof(input)):
                return (True,VectorConstant(input))
        elif((not IsInQoute) and (isinstance(input,sexprs.Pair)) and \
                 (isinstance(input.Item1,sexprs.Symbol)) and \
                 (str(input.Item1)=="QUOTE")):
            return ConstantFactory.InnerParseRec(input.Item2.Item1, True)
        else:
            return (False, False)

class Constant(AbstractSchemeExpr):
    def __init__(self,var):
        self.var=var
        self.value = 0 #Dummy
        # This section is importent for the hash table of ConstantTable class
    value = 0
    def __hash__(self):
        return hash((self.__class__.__name__, self.value))
    def __eq__(self, other):
        return (self.__class__.__name__, self.value) == (other.__class__.__name__, other.value)

    def __str__(self):
        return str(self.var)

    def CodeGenRec(self):
        # correct only for constant that save in the memory: tag and then value in length 1
        self.EnterTTab("MOV(R0," + str(ConsTable.GetAddr(self)) + ");")
        return self.TempOutputCode
        # This function tell the ConstantTable class what is the size of this constant in the memory
    def SpaceInMemory(self):
        return 2
        # This function tell the ConstantTable class how to enter the constant to the memory
    def EnterToConstantTable(self):
        ConstatTableOutputCode = ""
        ConstatTableOutputCode += "// Enter constant " + self.__class__.__name__ + " to Constant table \n"
        ConstatTableOutputCode += ("PUSH(" + str(self.value) + "); \n")
        ConstatTableOutputCode += "CALL(" + self.CreatorInMemFunction() + "); \n"
        ConstatTableOutputCode +="DROP(1); \n"
        return ConstatTableOutputCode
    def CreatorInMemFunction(self):
        pass

class BooleanConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return  isinstance(instance,sexprs.Boolean)
    def __init__(self,var):
        super(BooleanConstant,self).__init__(var)
        self.value = int(self.var.value)
    def CreatorInMemFunction(self):
        return "MAKE_SOB_BOOL"
class FractionConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return  isinstance(instance,sexprs.Fraction)
    def __init__(self,var):
        super(FractionConstant,self).__init__(var)
        self.Numerator = self.var.Numerator
        self.Denominator = self.var.Denominator
        self.value = str(self.Numerator) + str(self.Denominator)
    def EnterToConstantTable(self):
        ConstatTableOutputCode = ""
        ConstatTableOutputCode += "// Enter constant " + self.__class__.__name__ + " to Constant table \n"
        ConstatTableOutputCode += ("PUSH(" + str(self.Denominator) + "); \n")
        ConstatTableOutputCode += ("PUSH(" + str(self.Numerator) + "); \n")
        ConstatTableOutputCode += "CALL(" + self.CreatorInMemFunction() + "); \n"
        ConstatTableOutputCode +="DROP(2); \n"
        return ConstatTableOutputCode
    def CreatorInMemFunction(self):
        return "MAKE_SOB_FRACTION"
    def SpaceInMemory(self):
        return 3

class IntegerConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return  isinstance(instance,sexprs.Integer)
    def __init__(self,var):
        super(IntegerConstant,self).__init__(var)
        self.value = self.var.value
    def CreatorInMemFunction(self):
        return "MAKE_SOB_INTEGER"

class CharConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return  isinstance(instance,sexprs.Char)
    def __init__(self,var):
        super(CharConstant,self).__init__(var)
        char=self.var.sym
        if(char=='newline'):
            self.value=10
        elif(char=='return'):
            self.value=13
        elif(char=='tab'):
            self.value=9
        elif(char=='page'):
            self.value=12
        elif(char=='lambda'):
            self.value=0x03bb
        elif(char[0]=='x'):
            self.value=('0'+char)
        else:
            self.value = ord(self.var.sym) #ord - get ascii value
    def CreatorInMemFunction(self):
        return "MAKE_SOB_CHAR"

class VoidConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return isinstance(instance,sexprs.Void)
    def CreatorInMemFunction(self):
        return "MAKE_SOB_VOID"
    def SpaceInMemory(self):
        return 1

class NilConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return isinstance(instance,sexprs.Nil)
    def CreatorInMemFunction(self):
        return "MAKE_SOB_NIL"
    def SpaceInMemory(self):
        return 1

class StringConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return  isinstance(instance,sexprs.String)
    def __init__(self,var):
        super(StringConstant,self).__init__(var)
        self.value = self.var.sym
        self.AsciiString =  [ord(c) for c in  self.value] #ord - get ascii value
    def EnterToConstantTable(self):
        ConstatTableOutputCode = ""
        ConstatTableOutputCode += "// Enter constant StringConstant to Constant table \n"
        ConstatTableOutputCode += "// Enter all the char in ascii to the stack \n"
        for char in self.AsciiString :
            ConstatTableOutputCode += ("PUSH(" + str(char) + "); \n")
        ConstatTableOutputCode += "// Enter length of string to the stack \n"
        ConstatTableOutputCode += ("PUSH(" + str(len(self.AsciiString )) + "); \n")
        ConstatTableOutputCode += "CALL(MAKE_SOB_STRING); \n"
        ConstatTableOutputCode +="DROP("+ str(len(self.AsciiString ) + 1) +"); \n"
        return ConstatTableOutputCode
    def SpaceInMemory(self):
        return len(self.AsciiString) + 2

class SymbolConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return isinstance(instance,sexprs.Symbol)
    def __init__(self,var):
        super(SymbolConstant,self).__init__(var)
        self.value = StringConstant(sexprs.String(str(var)))
    def CreatorInMemFunction(self):
        return "MAKE_SOB_SYMBOL"
    def EnterToConstantTable(self):
        SymTable.AddSymbol(self)
        self.value =   ConsTable.GetAddr(self.value)
        return super(SymbolConstant,self).EnterToConstantTable()

class PairConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return isinstance(instance,sexprs.Pair)
    def __init__(self,var):
        super(PairConstant,self).__init__(var)
        #todo - maybe to change the dummy to some validy check
        dummy, self.Item1 = ConstantFactory.InnerParseRec(var.Item1, True)
        dummy, self.Item2 = ConstantFactory.InnerParseRec(var.Item2, True)
        self.value = str(var)
    def SpaceInMemory(self):
        return 3
        # This function tell the ConstantTable class how to enter the constant to the memory
    def EnterToConstantTable(self):
        self.Item1 =   ConsTable.GetAddr(self.Item1)
        self.Item2 =   ConsTable.GetAddr(self.Item2)
        ConstatTableOutputCode = ""
        ConstatTableOutputCode += "// Enter constant " + self.__class__.__name__ + " to Constant table \n"
        ConstatTableOutputCode += ("PUSH(" + str(self.Item2) + "); \n")
        ConstatTableOutputCode += ("PUSH(" + str(self.Item1) + "); \n")
        ConstatTableOutputCode += "CALL(" + self.CreatorInMemFunction() + "); \n"
        ConstatTableOutputCode +="DROP(2); \n"
        return ConstatTableOutputCode
    def CreatorInMemFunction(self):
        return "MAKE_SOB_PAIR"

class VectorConstant(Constant):
    @staticmethod
    def instanceof(instance):
        return isinstance(instance,sexprs.Vector)
    def __init__(self,var):
        super(VectorConstant,self).__init__(var)
        self.size = len(var.values)
        self.values = []
        for cons in var.values:
            #todo - maybe to change the dummy to some validy check
            dummy, cons = ConstantFactory.InnerParseRec(cons, True)
            self.values.append(cons)
        self.value = ""
        for x in self.values:
            self.value += " "
            self.value += str(x.value)
    def SpaceInMemory(self):
        return 2 + self.size
        # This function tell the ConstantTable class how to enter the constant to the memory
    def EnterToConstantTable(self):
        ConstatTableOutputCode = ""
        ConstatTableOutputCode += "// Enter constant " + self.__class__.__name__ + " to Constant table \n"
        for cons in self.values:
            cons =  ConsTable.GetAddr(cons)
            ConstatTableOutputCode += ("PUSH(" + str(cons) + "); \n")
        ConstatTableOutputCode += ("PUSH(" + str(self.size) + "); \n")
        ConstatTableOutputCode += "CALL(" + self.CreatorInMemFunction() + "); \n"
        ConstatTableOutputCode +="DROP(" + str(1 + self.size) + "); \n"
        return ConstatTableOutputCode
    def CreatorInMemFunction(self):
        return "MAKE_SOB_VECTOR"


class Variable(AbstractSchemeExpr):
    def __init__(self,con):
        if(isinstance(con, sexprs.Pair)):
            self.con=con.Item1
        else:
            self.con=con

    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            item = instance.Item1
        else:
            item = instance

        return isinstance(item, sexprs.Symbol)

    def __str__(self):
        return  str(self.con)

class VarFree(Variable):
    def __init__(self,e):
        super(VarFree,self).__init__(str(e))
        VarTable.AddFreeVar(self.__str__())
    def __str__(self):
        return super(VarFree,self).__str__()
    def CodeGenRec(self):
        self.Comment("---------------------------------Free Var Begin-------------------------------------------------")
        self.EnterTTab("MOV(R0, IND(" + VarTable.GetAddress(self.__str__()) + "));")
        self.Comment("---------------------------------Free Var End---------------------------------------------------")
        return self.TempOutputCode

class VarParam(Variable):
    def __init__(self,e,minor):
        super(VarParam,self).__init__(str(e))
        self.minor=minor
    def __str__(self):
        return super(VarParam,self).__str__()
    def CodeGenRec(self):
        self.EnterTTab("MOV(R0,FPARG("+ str(self.minor+2)+ "));//variable is "+ str(self.minor) +" in the stack ")
        return  self.TempOutputCode

class VarBound(Variable):
    def __init__(self,e,major,minor):
        super(VarBound,self).__init__(str(e))
        self.major=major
        self.minor=minor
    def __str__(self):
        return super(VarBound,self).__str__()
    def CodeGenRec(self):
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("MOV(R1,FPARG(0));")
        self.EnterTTab("MOV(R0,INDD(R1,"+str(self.major+2) +"));//R0 will have the proper major")
        self.EnterTTab("MOV(R0,INDD(R0,"+ str(self.minor+1) +"));//R0 will have the proper minor")
        self.EnterTTab("POP(R1);")
        return  self.TempOutputCode

class IfThenElse(AbstractSchemeExpr):
    def __init__(self,statment):

        Cond = NextItem(statment)
        self.IfCondition = AbstractSchemeExpr.parseRec(Cond.Item1)

        TrueOperand = NextItem(Cond)
        self.IfTrue = AbstractSchemeExpr.parseRec(TrueOperand.Item1)

        ElseOperands = TrueOperand.Item2
        NilExcepted = ""
        if(not isinstance(ElseOperands, sexprs.Pair)):
            self.IfFalse = AbstractSchemeExpr.parseRec(sexprs.Void())    #fixed
            NilExcepted = ElseOperands
        else:
            self.IfFalse = AbstractSchemeExpr.parseRec(ElseOperands.Item1)
            NilExcepted = ElseOperands.Item2

        if(not isinstance(NilExcepted, sexprs.Nil)):
            raise SyntaxError

    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            IfLabel = instance.Item1
            return (isinstance(IfLabel, sexprs.Symbol) and (str(IfLabel) == "IF"))
        else:
            return False
    def CodeGenRec(self):
        self.Comment("<<<<<<<<<<<<<<< IF then else statment begin >>>>>>>>>>>>>>>")
        self.EnterT(" ")

        self.TempOutputCode +=  self.IfCondition.CodeGenRec()
        self.EnterTTab("CMP (R0," + ConsTable.GetAddr(MyBoolConstantFalse) + ");")
        FalseLabel = LabelGen.Next("iffalse")
        ExitLabel = LabelGen.Next("ifexit")

        self.EnterTTab("JUMP_EQ(" + FalseLabel + ");")
        self.TempOutputCode += self.IfTrue.CodeGenRec()
        self.EnterTTab("JUMP(" + ExitLabel + ");")
        self.EnterT(FalseLabel + ":")
        self.TempOutputCode += self.IfFalse.CodeGenRec()
        self.EnterT(ExitLabel + ":")

        self.Comment("<<<<<<<<<<<<<<< IF then else statment end >>>>>>>>>>>>>>>")
        self.EnterT(" ")

        return self.TempOutputCode
    def __str__(self):
        return "(if " + str(self.IfCondition) + " " + str(self.IfTrue) + " " + str(self.IfFalse)+ ")"


class Def(AbstractSchemeExpr):
    def __init__(self,definestatment):
        operands = NextItem(definestatment)

        Type, Typearg = self.ParseLeftPart(operands.Item1)

        operands = NextItem(operands)
        if(Type):
            lambdaStatement = sexprs.Pair(Typearg, operands)
            ValueToParse = sexprs.Pair(sexprs.Symbol("LAMBDA"), lambdaStatement)
        else:
            ValueToParse =  operands.Item1

        self.Value = AbstractSchemeExpr.parseRec(ValueToParse)

        endofdefine = operands.Item2
        if(not (isinstance(endofdefine, sexprs.Nil))):
            raise SyntaxError

    def ParseLeftPart(self, input):
        if(isinstance(input, sexprs.Pair)):
            self.ParseName(input.Item1)
            return (True, input.Item2)
        else:
            self.ParseName(input)
            return (False, "")

    def ParseName(self, input):
        self.variable = AbstractSchemeExpr.parseRec(input)
        if(not isinstance(self.variable, Variable)):
            raise SyntaxError

    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            DefineLabel = instance.Item1
            return (isinstance(DefineLabel, sexprs.Symbol) and (str(DefineLabel) == "DEFINE"))
        else:
            return False

    def CodeGenRec(self):
        self.Comment("----------------------------- Define statment for "+ str(self.variable) + " Begin-----------------------------")
        self.TempOutputCode += self.Value.CodeGenRec()
        self.EnterTTab("MOV(IND(" + VarTable.GetAddress( str(self.variable)) + "), R0);")
        self.EnterTTab("MOV(R0," + ConsTable.GetAddr(MyVoidConstant) + ");")
        self.Comment("----------------------------- Define statment for "+ str(self.variable) + " End-------------------------------")
        return self.TempOutputCode

    def __str__(self):
        return "(define " + str(self.variable) + " " + str(self.Value)+ ")"

class LambdaFactory:
    @staticmethod
    def CreateLambda(input):
        operands = NextItem(input)

        bodyStatement = NextItem(operands)
        if(not  isinstance(bodyStatement.Item2, sexprs.Nil)):
            raise SyntaxError
        body = AbstractSchemeExpr.parseRec(bodyStatement.Item1)

        parameters = operands.Item1

        if(isinstance(parameters, sexprs.Symbol)):
            OneParam = AbstractSchemeExpr.parseRec(parameters)
            if(not isinstance(OneParam, Variable)):
                raise SyntaxError
            return LambdaVar(OneParam, body)
        else:
            type, ParamList = LambdaFactory.ParametersParse(parameters, [])
            if(type):
                return LambdaOpt(ParamList, body)
            else:
                return LambdaSimple(ParamList, body)

    @staticmethod
    def ParametersParse(input, list):
        if(not isinstance(input, sexprs.Pair)):
            if(not isinstance(input, sexprs.Nil)):
                raise SyntaxError
            else:
                return (False, ())
        else:
            CurrParam = AbstractSchemeExpr.parseRec(input.Item1)
            if(not isinstance(CurrParam, Variable)):
                raise SyntaxError
            list.append(CurrParam)

            if(isinstance(input.Item2, sexprs.Nil)):
                return (False, list)
            elif(isinstance(input.Item2, sexprs.Symbol)):
                LastParam = AbstractSchemeExpr.parseRec(input.Item2)
                if(not isinstance(LastParam, Variable)):
                    raise SyntaxError
                list.append(LastParam)
                return (True, list)
            else:
                return  LambdaFactory.ParametersParse(input.Item2, list)

class AbstractLambda(AbstractSchemeExpr):
    def __init__(self, body):
        self.Body = body
    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            LambdaLabel = instance.Item1
            return (isinstance(LambdaLabel, sexprs.Symbol) and (str(LambdaLabel) == "LAMBDA"))
        else:
            return False
    def __str__(self):
        return "(lambda "
    def body(self):
        return self.Body
    def CodeGenRec(self):
        self.Comment("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Lambda code"+self.Name()+" start:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        self.EnterT("  ")

        self.Comment("Save registry values before make lambda code")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("PUSH(R2);")
        self.EnterTTab("PUSH(R3);")
        self.EnterTTab("PUSH(R4);")
        self.EnterT("  ")

        #Enlarge the env
        self.Comment("Enlarge env")
        self.EnterTTab("PUSH(FPARG(0));//push the env")
        self.EnterTTab("CALL(ENLARGE_ENV);")
        self.EnterTTab("DROP(1);")

        self.Comment("save in R1 the new env")
        self.EnterTTab("MOV(R1, R0);") #save in R1 the new env
        self.EnterT("  ")

        #Allocate space for the new level
        self.Comment("Allocate space for the new level")
        self.EnterTTab("MOV(R3, FPARG(1));")
        self.EnterTTab("INCR(R3);") #make space for meta-data: number of args in level
        self.EnterTTab("PUSH(R3);")
        self.EnterTTab("CALL(MALLOC);")
        self.EnterTTab("DROP(1);")
        self.EnterTTab("MOV(R2, R0);") #save in R2 the new level
        self.EnterTTab("MOV(IND(R2), FPARG(1));") #save in the first cell the number of args in level
        self.EnterT("  ")

        #Create Labels for the copy args loop - copy from the stack to the new level
        LambdaCopyArgLoop = LabelGen.Next("Lambda"+ self.Name()+"CopyArgLoop")
        LambdaCopyArgExit = LabelGen.Next("Lambda"+ self.Name()+"CopyArgExit")

        #init loop
        self.Comment("This loop - copy from the stack to the new level")
        self.EnterTTab("INCR(R2);")  #skip the metadata of the new level for the offset will be correct(like in stack)
        self.EnterTTab("MOV(R3, 0);")  #R3 is the loop counter and also the offest
        self.EnterT("  ")

        self.EnterTTab("MOV(R4,R3);")
        self.EnterTTab("ADD(R4,IMM(2));")###########

        #loop cond +body
        self.Comment("loop cond +body")
        self.EnterT(LambdaCopyArgLoop + ":")
        self.EnterTTab("CMP(R3, FPARG(1));")
        self.EnterTTab("JUMP_EQ(" + LambdaCopyArgExit + ");" )
        self.EnterTTab("MOV(INDD(R2,R3), FPARG(R4));")##########3
        self.EnterTTab("INCR(R3);")
        self.EnterTTab("INCR(R4);")############3
        self.EnterTTab("JUMP(" + LambdaCopyArgLoop + ");")
        self.EnterT("  ")

        #exit loop
        self.Comment("exit loop")
        self.EnterT(LambdaCopyArgExit + ":")
        self.EnterTTab("DECR(R2);")  #Cancel the INCR(R2) before the loop
        self.EnterTTab("  ")

        #make closure
        self.Comment("make closure")
        LambdaBody = LabelGen.Next("Lambda"+ self.Name()+"Body")
        LambdaBodyExit = LabelGen.Next("Lambda"+ self.Name()+"BodyExit")
        self.EnterTTab("MOV(INDD(R1, 2), R2);") #copy the new level(address) into the env
        self.EnterTTab("PUSH(LABEL(" +  LambdaBody + "));")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("CALL(MAKE_SOB_CLOSURE);")
        self.EnterTTab("DROP(2);")
        self.EnterTTab("  ")

        self.Comment("recover temp vars")
        self.EnterTTab("POP(R4);")
        self.EnterTTab("POP(R3);")
        self.EnterTTab("POP(R2);")
        self.EnterTTab("POP(R1);")
        self.EnterTTab("  ")

        self.EnterTTab("JUMP(" + LambdaBodyExit + ");")
        self.EnterTTab("  ")
        self.CodeGenBody(LambdaBody, LambdaBodyExit)

        self.Comment("^^^^^^^^^^^^^^^^^^^^^^^^^Lambda"+  self.Name() + "code end:^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        return self.TempOutputCode

class LambdaSimple(AbstractLambda):
    def __init__(self,Params, body):
        super(LambdaSimple, self).__init__(body)
        self.Params = Params

    def Name(self):
        return "Simple"

    def CodeGenBody(self, LambdaBody, LambdaBodyExit):
        self.Comment("Body appiication:")
        self.EnterT(LambdaBody + ":")
        self.EnterTTab("PUSH(FP);")
        self.EnterTTab("MOV(FP, SP);")

        self.TempOutputCode += self.Body.CodeGenRec()

        self.EnterTTab("POP(FP);")
        self.EnterTTab("RETURN;")
        self.EnterT(LambdaBodyExit + ":")

    def __str__(self):
        return "(lambda (" + ' '.join((map(str,self.Params))) + ") " + str(self.Body)+ ")"

class LambdaOpt(AbstractLambda):
    def __init__(self,Params, body):
        super(LambdaOpt, self).__init__(body)
        self.Params = Params
    def Name(self):
        return "Optional"

    def CodeGenBody(self, LambdaBody, LambdaBodyExit):

        self.EnterT(LambdaBody + ":")
        self.Comment("Body appiication:")

        self.EnterTTab("PUSH(FP);")
        self.EnterTTab("MOV(FP, SP);")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("PUSH(R2);")
        self.EnterTTab("PUSH(R3);")

        #Fixing the Stack
        self.Comment("***LAMBDA OPT begin **")
        LambdaFixing = LabelGen.Next("Lambda"+ self.Name()+"FixingTheStack")
        LambdaFixingEnd = LabelGen.Next("Lambda"+ self.Name()+"FixingTheStackEnd")
        LambdaMagicDeleteOpt=  LabelGen.Next("Lambda"+ self.Name()+"MagicDelete")

        self.EnterTTab("MOV(R1,"+ConsTable.GetAddr(MyNilConstant)+");") #R1 is the final object
        self.EnterTTab("MOV(R2,FPARG(1));")#R2 is the number of parameters left
        self.EnterTTab("SUB(R2,"+str(len(self.Params)-1)+");")
        self.EnterTTab("MOV(R3,FPARG(1));")#R3 is the number of total parameters
        self.EnterTTab("INCR(R3);")
        self.EnterT(LambdaFixing+":")
        if 1:
            self.EnterTTab("CMP(R2,0);")
            self.EnterTTab("JUMP_EQ("+LambdaFixingEnd +");")
            self.EnterTTab("PUSH(R1);")
            self.EnterTTab("PUSH(FPARG(R3));")
            self.EnterTTab("CALL(MAKE_SOB_PAIR);")
            self.EnterTTab("MOV(R1,R0);")
            self.EnterTTab("DROP(2);")
            self.EnterTTab("DECR(R2);")
            self.EnterTTab("DECR(R3);")
            self.EnterTTab("JUMP("+LambdaFixing +");")
        self.EnterT(LambdaFixingEnd+":")
        self.EnterTTab("MOV(R2,FPARG(1));")
        self.EnterTTab("ADD(R2,2);")

        self.Comment("****************")
        self.EnterTTab("CMP(FPARG(R2),IMM(123456));")
        self.EnterTTab("JUMP_EQ("+LambdaMagicDeleteOpt+");")
        self.EnterTTab("DECR(R2);")
        self.EnterT(LambdaMagicDeleteOpt+":")

        self.EnterTTab("MOV(FPARG(R2),R1);")
        self.EnterTTab("DECR(R2);")

        LambdaOPTFixing = LabelGen.Next("LambdaOPTFixing")
        LambdaOPTFixingEnd = LabelGen.Next("LambdaOPTFixingEnd")
        self.EnterTTab("MOV(R3,"+str(len(self.Params))+");")
        self.EnterT(LambdaOPTFixing+":")
        self.EnterTTab("CMP(2,R3);")
        self.EnterTTab("JUMP_GT("+LambdaOPTFixingEnd+");")
        self.EnterTTab("MOV(FPARG(R2),FPARG(R3));")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("DECR(R3);")
        self.EnterTTab("JUMP("+LambdaOPTFixing+");")
        self.EnterTTab(LambdaOPTFixingEnd+":")

        self.EnterTTab("MOV(FPARG(R2),"+str(len(self.Params))+");")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(0));")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(-1));")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(-2));")
        self.EnterTTab("SUB(FP,R2);")
        self.EnterTTab("SUB(FP,2);")
        self.EnterTTab("POP(R3);")
        self.EnterTTab("POP(R2);")
        self.EnterTTab("POP(R1);")
        self.EnterTTab("MOV(SP,FP);")

        self.Comment("***LAMBDA OPT end **")

        self.TempOutputCode += self.Body.CodeGenRec()


        self.EnterTTab("POP(FP);")
        self.EnterTTab("RETURN;")
        self.EnterT(LambdaBodyExit + ":")


    def __str__(self):
        return "(lambda (" + ' . '.join((map(str,self.Params))) + ") " + str(self.Body)+ ")"

class LambdaVar(AbstractLambda):
    def __init__(self,OneParam, body):
        super(LambdaVar, self).__init__(body)
        self.OneParam = OneParam
    def __str__(self):
        return "(lambda " + str(self.OneParam) + " " + str(self.Body)+ ")"

    def Name(self):
        return "Variadic"

    def CodeGenBody(self, LambdaBody, LambdaBodyExit):

        self.EnterT(LambdaBody + ":")
        self.Comment("Body appiication:")

        self.EnterTTab("PUSH(FP);")
        self.EnterTTab("MOV(FP, SP);")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("PUSH(R2);")

        #Fixing the Stack
        LambdaFixing = LabelGen.Next("Lambda"+ self.Name()+"FixingTheStack")
        LambdaFixingEnd = LabelGen.Next("Lambda"+ self.Name()+"FixingTheStackEnd")
        LambdaMagicDelete=  LabelGen.Next("Lambda"+ self.Name()+"MagicDelete")
        self.EnterTTab("MOV(R1,"+ConsTable.GetAddr(MyNilConstant)+");") #R1 is the final object
        self.EnterTTab("MOV(R2,FPARG(1));")#R2 is the number of parameters left
        self.EnterTTab("ADD(R2,1);")
        self.EnterT(LambdaFixing+":")
        if 1:
            self.EnterTTab("CMP(2,R2);")
            self.EnterTTab("JUMP_GT("+LambdaFixingEnd +");")
            self.EnterTTab("PUSH(R1);")
            self.EnterTTab("PUSH(FPARG(R2));")
            self.EnterTTab("CALL(MAKE_SOB_PAIR);")
            self.EnterTTab("MOV(R1,R0);")
            self.EnterTTab("DROP(2);")
            self.EnterTTab("DECR(R2);")
            self.EnterTTab("JUMP("+LambdaFixing +");")
        self.EnterT(LambdaFixingEnd+":")
        self.EnterTTab("MOV(R2,FPARG(1));")
        self.EnterTTab("ADD(R2,2);")

        self.EnterTTab("CMP(FPARG(R2),IMM(123456));")
        self.EnterTTab("JUMP_EQ("+LambdaMagicDelete+");")
        self.EnterTTab("DECR(R2);")
        self.EnterT(LambdaMagicDelete+":")

        self.EnterTTab("MOV(FPARG(R2),R1);")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),1);")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(0));")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(-1));")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("MOV(FPARG(R2),FPARG(-2));")
        self.EnterTTab("SUB(FP,R2);")
        self.EnterTTab("SUB(FP,2);")
        self.EnterTTab("POP(R2);")
        self.EnterTTab("POP(R1);")
        self.EnterTTab("MOV(SP,FP);")


        self.TempOutputCode += self.Body.CodeGenRec()

        self.EnterTTab("POP(FP);")
        self.EnterTTab("RETURN;")
        self.EnterT(LambdaBodyExit + ":")

class Applic(AbstractSchemeExpr):
    def __init__(self,applic):
        self.Lambda = AbstractSchemeExpr.parseRec(applic.Item1)
        params =  NextItem(applic)
        ParamList = []


        while(isinstance(params,sexprs.Pair)):
            temp=  AbstractSchemeExpr.parseRec(params.Item1)
            ParamList.append(temp)
            params= params.Item2
        self.ParamList=ParamList

    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            Lambda = instance.Item1
            return (isinstance(Lambda, sexprs.Pair) or isinstance(Lambda,( sexprs.Symbol, sexprs.Char, sexprs.Integer )))
        else:
            return False

    def __str__(self):
        return "(" + str(self.Lambda) + " " + ' '.join((map(str,self.ParamList)))+ ")"
    def CodeGenRec(self):
        self.Comment("**************Aplic MotherFucker***************")
        self.EnterTTab("    ")

        self.Comment("Save the regisry will change in the application")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("PUSH(R2);")
        self.EnterTTab("PUSH(R3);")
        self.EnterTTab("PUSH(R4);")
        self.EnterTTab("PUSH(R5);")
        self.EnterTTab("    ")

        self.Comment("Entering all the the application parameters in reverse order after Evaluation")
        self.Comment("**Magic Parameter**")
        self.EnterTTab("PUSH (123456); //Magic Parameter")
        ReverseParamList=self.ParamList
        ReverseParamList.reverse()
        for param in ReverseParamList:  #Entering all the the application parameters in reverse order after Evaluation
            self.TempOutputCode += param.CodeGenRec()
            self.EnterTTab("PUSH (R0);")



        self.EnterT("         ")
        self.Comment("*******Number of Parameters***********")
        self.EnterTTab("PUSH ("+ str(len(self.ParamList))+");")#Number of Parameters

        self.TempOutputCode+= self.Lambda.CodeGenRec() #Code Generator of the Closure

        self.Comment("Checking whether we got a real Closure")  #Checking whether we got a real Closure
        self.EnterTTab("PUSH(R0);")
        self.EnterTTab("CALL(IS_SOB_CLOSURE);")
        self.EnterTTab("CMP(R0,0);")
        self.EnterTTab("JUMP_EQ(LERROR_NOT_CLOSURE);")
        self.EnterTTab("POP(R0);")
        self.EnterTTab("    ")

        self.EnterTTab("PUSH(INDD(R0,1));")#Pushing the Env
        self.EnterTTab("CALLA(INDD(R0,2));")#<--Apllication
        self.EnterTTab("   ")

        self.Comment("*****Cleaning the Stack*******")
        self.EnterTTab("DROP(1);")
        self.EnterTTab("POP(R1);")
        self.EnterTTab("DROP(R1);")
        self.EnterT("     ")

        ApplicMagicDelete = LabelGen.Next("ApplicMagicDelete")#Deleting the Magic Number
        self.EnterTTab("POP(R1);")
        self.EnterTTab("CMP(R1,123456);")
        self.EnterTTab("JUMP_EQ("+ApplicMagicDelete+");")
        self.EnterTTab("PUSH(R1);")
        self.EnterT(ApplicMagicDelete+":")

        self.Comment("Recover the regisries")
        self.EnterTTab("POP(R5);")
        self.EnterTTab("POP(R4);")
        self.EnterTTab("POP(R3);")
        self.EnterTTab("POP(R2);")
        self.EnterTTab("POP(R1);")


        self.EnterT("     ")
        self.Comment("*************That's it for Motherfucker Application, see you next time********")
        return self.TempOutputCode

class  ApplicTP(Applic):
    def __init__(self, Lambda, ParamList):
        self.Lambda = Lambda
        self.ParamList = ParamList
    def __str__(self):
        return "(" + str(self.Lambda) + " " + ' '.join((map(str,self.ParamList)))+ ")"
    def CodeGenRec(self):
        self.Comment("**************AplicTP FatherFucker***************")
        self.EnterTTab("    ")

        self.Comment("Save the regisry will change in the application")
        for i in range(len(self.ParamList)+4):
            self.EnterTTab("PUSH(IMM(0));")
        self.EnterTTab("PUSH(R1);")
        self.EnterTTab("PUSH(R2);")
        self.EnterTTab("PUSH(R3);")
        self.EnterTTab("PUSH(R4);")
        self.EnterTTab("PUSH(R5);")
        self.EnterTTab("    ")

        self.Comment("Entering all the the application parameters in reverse order after Evaluation")
        self.EnterTTab("MOV(R1,FP);")
        self.Comment("**Magix Parameter**")
        self.EnterTTab("MOV (STACK(R1),IMM(123456)); //Magic Parameter")
        self.EnterTTab("INCR(R1);")
        ReverseParamList=self.ParamList
        ReverseParamList.reverse()
        for param in ReverseParamList:  #Entering all the the application parameters in reverse order after Evaluation
            self.TempOutputCode += param.CodeGenRec()
            self.EnterTTab("MOV(STACK(R1),R0);")
            self.EnterTTab("INCR(R1);")


        self.EnterT("         ")
        self.Comment("*******Number of Parameters***********")
        self.EnterTTab("MOV(STACK(R1),IMM("+ str(len(self.ParamList))+"));")#Number of Parameters
        self.EnterTTab("INCR(R1);")


        self.TempOutputCode+= self.Lambda.CodeGenRec() #Code Generator of the Closure

        self.Comment("Checking whether we got a real Closure")  #Checking whether we got a real Closure
        self.EnterTTab("PUSH(R0);")
        self.EnterTTab("CALL(IS_SOB_CLOSURE);")
        self.EnterTTab("CMP(R0,0);")
        self.EnterTTab("JUMP_EQ(LERROR_NOT_CLOSURE);")
        self.EnterTTab("POP(R0);")
        self.EnterTTab("    ")


        self.EnterTTab("MOV(STACK(R1),INDD(R0,1));")#Pushing the Env
        self.EnterTTab("INCR(R1);")
        self.EnterTTab("MOV(STACK(R1),FPARG(-1));")#Pushing the old return
        self.Comment("*******Size Of the Frame***********")
        self.EnterTTab("MOV(R1,IMM("+str(len(self.ParamList)+9)+"));")#R1 is the Size of the new frame!!!

        notMagic= LabelGen.Next("notMagic")
        self.EnterTTab("MOV(R2,IMM(4));")#!!!
        self.EnterTTab("ADD(R2,FPARG(1));") #R2 is the size of the old frame
        self.EnterTTab("MOV(R3,FPARG(1));")
        self.EnterTTab("ADD(R3,IMM(2));")
        self.EnterTTab("CMP(123456,FPARG(R3));")#Adding one if it includes magig parameter
        self.EnterTTab("JUMP_NE("+notMagic+");")
        self.EnterTTab("INCR(R2);")
        self.EnterT(notMagic+":")
        self.EnterTTab("MOV(R3,FPARG(-2));")#saving the old fp, because were gonna delete it

        FixingTheStacLabelStart = LabelGen.Next("FixingTheStacLabelStart")#Fixing the Stack
        FixingTheStacLabelEnd = LabelGen.Next("FixingTheStacLabelEnd")#Fixing the Stack

        self.Comment("**Deleting the Old Frame begin**")
        self.EnterTTab("MOV(R5,R2);")#R5 will keep the Size of the Old frame ?!?!?!

        self.EnterTTab("MOV(R4,IMM(-3));")#!!!!
        self.EnterTTab("SUB(R2,3);")#!!!!!


        self.EnterT(FixingTheStacLabelStart+":")
        self.EnterTTab("CMP(R1,IMM(0));")
        self.EnterTTab("JUMP_EQ("+FixingTheStacLabelEnd +");")
        self.EnterTTab("MOV(FPARG(R2),FPARG(R4));")
        self.EnterTTab("DECR(R1);")
        self.EnterTTab("DECR(R2);")
        self.EnterTTab("DECR(R4);")
        self.EnterTTab("JUMP("+FixingTheStacLabelStart+");")
        self.EnterT(FixingTheStacLabelEnd+":")

        self.EnterTTab("DROP(R5);")

        self.Comment("**Deleting the Old Frame ends**")
        ApplicMagicDelete = LabelGen.Next("ApplicMagicDelete")#Deleting the Magic Number
        self.EnterTTab("POP(R1);")
        self.EnterTTab("CMP(R1,123456);")
        self.EnterTTab("JUMP_EQ("+ApplicMagicDelete+");")
        self.EnterTTab("PUSH(R1);")
        self.EnterT(ApplicMagicDelete+":")

        self.EnterTTab("MOV(FP,R3);") #Changing the FP

        self.EnterTTab("POP(R5);")
        self.EnterTTab("POP(R4);")
        self.EnterTTab("POP(R3);")
        self.EnterTTab("POP(R2);")
        self.EnterTTab("POP(R1);")

        self.EnterTTab("JUMPA(INDD(R0,2));")#<--Apllication

        return self.TempOutputCode

class Or(AbstractSchemeExpr):
    def __init__(self,orConditions):
        conditions= []
        orConditions=orConditions.Item2
        while(isinstance(orConditions,sexprs.Pair)):
            temp=  AbstractSchemeExpr.parseRec(orConditions.Item1)
            conditions.append(temp)
            orConditions= orConditions.Item2
        self.OrConditions=conditions

        if(len(self.OrConditions) == 0):
            self.OrConditions = [AbstractSchemeExpr.parseRec(sexprs.Boolean(False))]
        #Cond1 = NextItem(orConditions)
        #self.OrCondition1 = AbstractSchemeExpr.parseRec(Cond1.Item1)

        #Cond2 = NextItem(Cond1)
        #self.OrCondition2 = AbstractSchemeExpr.parseRec(Cond2.Item1)

    @staticmethod
    def instanceof(instance):
        if(isinstance(instance, sexprs.Pair)):
            OrLabel = instance.Item1
            return (isinstance(OrLabel, sexprs.Symbol) and (str(OrLabel) == "OR"))
        else:
            return False

    def __str__(self):
        return "(or " + ' '.join((map(str,self.OrConditions))) + ")"
    def CodeGenRec(self):
        self.Comment("----------------Start Or Code --------------------")

        OutOrLabel = LabelGen.Next("OutOr")

        self.Comment("Apply or item until you get true")
        for cond in self.OrConditions:
            self.EnterT(cond.CodeGenRec())
            self.EnterTTab("CMP (R0," + ConsTable.GetAddr(MyBoolConstantFalse) + ");")
            self.EnterTTab("JUMP_NE(" + OutOrLabel + ");")
        self.EnterT(OutOrLabel  + ":")

        self.Comment("----------------End Or Code ----------------------")
        return self.TempOutputCode

class Cond:
    @staticmethod
    def instanceof(instance):
        return StartWith("COND", instance)

    @staticmethod
    def ConvertToIf(input):
        return AbstractSchemeExpr.parseRec(Cond.ConvertToIfRec(input.Item2, True))

    @staticmethod
    def ConvertToIfRec(input, FirstTime):
        if(not isinstance(input, sexprs.Pair)):
            if(FirstTime):
                raise SyntaxError
            return ""
        else:
            CurrCond =  input.Item1
            NextCond = input.Item2
            if(not isinstance(CurrCond, sexprs.Pair)):
                raise SyntaxError

            result =  CurrCond.Item2
            if(not isinstance(result, sexprs.Pair)):
                raise SyntaxError
            if(not isinstance(result.Item2, sexprs.Nil)):
                raise SyntaxError
            result = result.Item1

            if(StartWith("ELSE", CurrCond)):
                if(FirstTime):
                    raise SyntaxError
                return result
            else:
                condition = CurrCond.Item1

                innerIf = Cond.ConvertToIfRec(NextCond, False)
                if(innerIf == ""):
                    ifStatement = sexprs.Nil()
                else:
                    ifStatement = sexprs.Pair(innerIf, sexprs.Nil())

                ifStatement = sexprs.Pair(result, ifStatement)
                ifStatement = sexprs.Pair(condition, ifStatement)
                ifStatement = sexprs.Pair(sexprs.Symbol("IF"), ifStatement)

                return ifStatement

class And:
    @staticmethod
    def instanceof(instance):
        return StartWith("AND", instance)

    @staticmethod
    def ConvertToIf(input):
        if(isinstance(input.Item2, sexprs.Nil)):
            input.Item2 = sexprs.Pair(sexprs.Boolean(True),sexprs.Nil())
        return AbstractSchemeExpr.parseRec(And.ConvertToIfRec(input.Item2, True))

    @staticmethod
    def ConvertToIfRec(input, FirstTime):
        if(not isinstance(input, sexprs.Pair)):
            if(FirstTime):
                raise  SyntaxError
            return ""
        else:

            CurrCond =  input.Item1
            NextCond = input.Item2
            if(isinstance(NextCond,sexprs.Nil)):
                return CurrCond
            if(isinstance(NextCond.Item2,sexprs.Nil)):
                end = AbstractSchemeExpr.parseRec(NextCond.Item1)
            else:
                end = And.ConvertToIfRec( NextCond, False)

            ifStatement = sexprs.Pair(sexprs.Boolean(False),sexprs.Nil())
            ifStatement = sexprs.Pair(end, ifStatement)
            ifStatement = sexprs.Pair(AbstractSchemeExpr.parseRec(CurrCond), ifStatement)
            ifStatement = sexprs.Pair(sexprs.Symbol("if"),ifStatement)


            return ifStatement

class Let:
    @staticmethod
    def instanceof(instance):
        return StartWith("LET", instance)

    @staticmethod
    def ConvertToApplic(input):
        ListParms, ListVars, LetBody = Let.GetLetDetails(input)

        lambdaStatement = sexprs.Pair(ListParms, LetBody)
        lambdaStatement = sexprs.Pair(sexprs.Symbol("LAMBDA"), lambdaStatement)

        applicStatement = sexprs.Pair(lambdaStatement, ListVars)

        return AbstractSchemeExpr.parseRec(applicStatement)

    @staticmethod
    def GetLetDetails(input):
        statement = input.Item2
        if(not isinstance(statement, sexprs.Pair)):
            raise SyntaxError
        LetList = statement.Item1
        if(not isinstance(LetList, sexprs.Pair)):
            if(not isinstance(LetList, sexprs.Nil)):
                raise SyntaxError
        LetBody =  statement.Item2
        if(not isinstance(LetBody, sexprs.Pair)):
            raise SyntaxError
        if(not isinstance(LetBody.Item2, sexprs.Nil)):
            raise SyntaxError

        ListParms, ListVars = Let.SplitList(LetList, sexprs.Nil(), sexprs.Nil())

        return (ListParms, ListVars, LetBody)

    @staticmethod
    def SplitList(input, ParamsList, VarsList):
        if(not isinstance(input, sexprs.Pair)):
            if(not isinstance(input, sexprs.Nil)):
                raise SyntaxError
            else:
                return (ParamsList, VarsList)
        CurrAss = input.Item1
        if(not isinstance(CurrAss, sexprs.Pair)):
            raise SyntaxError
        CurrParam = CurrAss.Item1
        CurrVar = CurrAss.Item2
        if(not isinstance(CurrVar, sexprs.Pair)):
            raise SyntaxError
        if(not isinstance(CurrVar.Item2, sexprs.Nil)):
            raise SyntaxError
        CurrVar = CurrVar.Item1

        ReturnParamsList, ReturnVarsList = Let.SplitList(input.Item2,ParamsList, VarsList)
        return (sexprs.Pair(CurrParam, ReturnParamsList), sexprs.Pair(CurrVar, ReturnVarsList))

class LetAsterisk:
    @staticmethod
    def instanceof(instance):
        return StartWith("LET*", instance)

    @staticmethod
    def Parse(input):
        return AbstractSchemeExpr.parseRec(LetAsterisk.ConvertToLet(input))

    @staticmethod
    def ConvertToLet(input):
        inputWitoutLabel = input.Item2
        if(not isinstance(inputWitoutLabel, sexprs.Pair)):
            raise SyntaxError
        LetParams = inputWitoutLabel.Item1
        LetBody = inputWitoutLabel.Item2
        if(isinstance(LetParams, sexprs.Pair)):
            FirstLet=LetParams.Item1
            OtherLet=LetParams.Item2
            LetParamsStatement = sexprs.Pair(FirstLet, sexprs.Nil())
        elif(isinstance(LetParams, sexprs.Nil)):
            LetParamsStatement=sexprs.Nil()
            OtherLet=sexprs.Nil()
        else:
            raise SyntaxError


        body = ""
        if(not isinstance(OtherLet, sexprs.Nil)):
            LetAsteriskStatement = sexprs.Pair(OtherLet, LetBody)
            LetAsteriskStatement = sexprs.Pair(sexprs.Symbol("LET*"), LetAsteriskStatement)
            LetAsteriskStatement = sexprs.Pair(LetAsteriskStatement, sexprs.Nil())
            LetBody = LetAsteriskStatement


        LetStatement = sexprs.Pair(LetParamsStatement, LetBody)
        LetStatement = sexprs.Pair(sexprs.Symbol("LET"), LetStatement)

        return LetStatement

class Letrec:
    @staticmethod
    def instanceof(instance):
        return StartWith("LETREC", instance)

    @staticmethod
    def ConvertToYag(input):
        ListParms, ListVars, LetBody = Let.GetLetDetails(input)

        ListParms = sexprs.Pair(sexprs.Symbol("g0"), ListParms)

        FirstLambda =  Letrec.BuildLambda(ListParms, LetBody)
        OtherLambdas = Letrec.BuildArgs(ListParms, ListVars)
        allLambda = sexprs.Pair(FirstLambda, OtherLambdas)

        YagStatment = sexprs.Pair(sexprs.Symbol("YAG"), allLambda)

        return AbstractSchemeExpr.parseRec(YagStatment)

    @staticmethod
    def BuildArgs(ListParms, ListVars):
        if(not isinstance(ListVars, sexprs.Pair)):
            return ListVars
        else:
            body = sexprs.Pair(ListVars.Item1, sexprs.Nil())
            CurrLambda = Letrec.BuildLambda(ListParms, body)
            return  sexprs.Pair(CurrLambda, Letrec.BuildArgs(ListParms, ListVars.Item2))

    @staticmethod
    def BuildLambda(ListParms, body):
        lambdaStatement = sexprs.Pair(ListParms, body)
        lambdaStatement = sexprs.Pair(sexprs.Symbol("LAMBDA"), lambdaStatement)
        return lambdaStatement




class CodeGenrator:
    OutputCode = ""
    TempOutputCode = ""

    ObjectsToGen = ""

    def __init__(self, items):
        self.ObjectsToGen = items

    def Enterl(self, line):
        self.OutputCode += line
        self.OutputCode += "\n"
    def EnterT(self, line):
        self.TempOutputCode += line
        self.TempOutputCode += "\n"
    def EnterTTab(self,line):
        self.TempOutputCode+=("\t"+line+"\n")
    def Comment(self, desc):
        self.TempOutputCode += "//"
        self.TempOutputCode += desc
        self.TempOutputCode += "\n"
    def MakeBeginFrame(self):
        self.Enterl("#include <stdio.h>")
        self.Enterl("#include <stdlib.h>")
        self.Enterl("#define DO_SHOW 1")
        self.Enterl('#include "cisc.h"')
        self.Enterl("#if DO_SHOW")
        self.Enterl('#define SHOW(msg, x) { printf("%s %s = %ld\\n", (msg), (#x), (x)); }')
        self.Enterl("#else")
        self.Enterl("#define SHOW(msg, x) {}")
        self.Enterl("#endif")
        self.Enterl("int main()")
        self.Enterl("{")
        self.Enterl("  START_MACHINE;")
        self.Enterl("  JUMP(CONTINUE);")
        self.Enterl('#include "char.lib"')
        self.Enterl('#include "io.lib"')
        self.Enterl('#include "math.lib"')
        self.Enterl('#include "string.lib"')
        self.Enterl('#include "system.lib"')
        self.Enterl('#include "scheme.lib"')
        self.Enterl('#include "compiler.lib"')
        self.Enterl('#include "ConstantFunc.lib"')
        self.Enterl(" CONTINUE:")
    def MakeCloseFrame(self):
        self.Enterl("  ")
        self.Enterl("END_PROG:")
        self.Enterl("DROP(4);")
        self.Enterl(" STOP_MACHINE;")
        self.Enterl(" return 0;")
        self.Enterl("}")
    def InsertInitCode(self):
        self.Enterl("// <<<<<<<<<<<<<<<<<< Yuval and Oron Show Begin!!!! >>>>>>>>>>>>>>>>>>>>>>")
        self.Enterl("  ")

        self.Enterl("// Allocate space for the entry of the symbol table, it will be always in the first place on the memory!")
        self.Enterl("PUSH(1);")
        self.Enterl("CALL(MALLOC);")
        self.Enterl("DROP(1);")

        #Dummy Stack:
        self.Enterl("// <<<<<<<<<<<<<<<<<< Make Dummy stack -start >>>>>>>>>>>>>>>>>>>>>>")
        self.Enterl("// Push dummy of number of args")
        self.Enterl("PUSH(0);")
        self.Enterl(" ")

        self.Enterl("// Push dummy env with 0 levels")
        self.Enterl("PUSH(0);")
        self.Enterl("CALL(MAKE_ENV);")
        self.Enterl("DROP(1);")
        self.Enterl("PUSH(R0);")
        self.Enterl(" ")

        self.Enterl("// Push dummy return address")
        self.Enterl("PUSH(0);")
        self.Enterl(" ")

        self.Enterl("// Push dummy old FP and set the FP like we do in normal function")
        self.Enterl("PUSH(0);")
        self.Enterl("MOV(FP, SP);")
        self.Enterl("// <<<<<<<<<<<<<<<<<< Make Dummy stack -end >>>>>>>>>>>>>>>>>>>>>>")
        self.Enterl("  ")

    def makeVariadicLambda(self):
        VariadicStart = "VariadicStart"
        VariadicEnd = "VariadicEnd"

        LambdaFixingStaticStart = "LambdaFixingStaticStart"
        LambdaFixingStaticEnd = "LambdaFixingStaticEnd"

        self.Enterl("JUMP("+VariadicEnd+");")
        self.Enterl(VariadicStart+":")
        self.Enterl("//Body Variadic Static Application:")

        self.Enterl("//PUSH(FP);")
        self.Enterl("//MOV(FP, SP);")

        #Fixing the Stack


        self.Enterl("MOV(R1,"+ConsTable.GetAddr(MyNilConstant)+");") #R1 is the final object
        self.Enterl("MOV(R2,FPARG(1));")#R2 is the number of parameters left
        self.Enterl("ADD(R2,1);")
        self.Enterl(LambdaFixingStaticStart+":")
        if 1:
            self.Enterl("CMP(2,R2);")
            self.Enterl("JUMP_GT("+LambdaFixingStaticEnd +");")
            self.Enterl("PUSH(R1);")
            self.Enterl("PUSH(FPARG(R2));")
            self.Enterl("CALL(MAKE_SOB_PAIR);")
            self.Enterl("MOV(R1,R0);")
            self.Enterl("DROP(2);")
            self.Enterl("DECR(R2);")
            self.Enterl("JUMP("+LambdaFixingStaticStart +");")
        self.Enterl(LambdaFixingStaticEnd+":")
        self.Enterl("MOV(R2,FPARG(1));")
        self.Enterl("ADD(R2,2);")

        self.Enterl("CMP(FPARG(R2),IMM(123456));")
        self.Enterl("JUMP_EQ(VariadicLambdaMagicDelete);")
        self.Enterl("DECR(R2);")
        self.Enterl("VariadicLambdaMagicDelete:")


        self.Enterl("MOV(FPARG(R2),R1);")
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),1);")
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(0));")
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-1));")
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-2));")
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-3));")#R5
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-4));")#R4
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-5));")#R3
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-6));")#R2
        self.Enterl("DECR(R2);")
        self.Enterl("MOV(FPARG(R2),FPARG(-7));")#R1
        self.Enterl("SUB(FP,R2);")
        self.Enterl("SUB(FP,IMM(2));")
        self.Enterl("POP(R2);")
        self.Enterl("MOV(STACK(FP),R2);")
        self.Enterl("INCR(FP);")
        self.Enterl("MOV(SP,FP);")
        self.Enterl("SUB(FP,IMM(6));")

        self.Enterl("//POP(FP);")
        self.Enterl("RETURN;")

        self.Enterl(VariadicEnd + ":")


    def code_gen(self):
        self.MakeBeginFrame()
        self.InsertInitCode()
        self.makeVariadicLambda()
        for index,item in enumerate(self.ObjectsToGen):
            self.EnterTTab("")
            self.Comment("--------------------------Start Code for Item " + str(index) + " ---------------------------")
            self.TempOutputCode += item.CodeGenRec()

            if(index > 0): #skip yag result
                self.TempOutputCode += "CMP(R0, 4);\n"
                self.TempOutputCode += "JUMP_EQ(L_DONT_PRINT_IT" + str(index) + ");\n"
                self.TempOutputCode += "PUSH(R0);\n"
                self.TempOutputCode += "CALL(WRITE_SOB);\n"
                self.TempOutputCode += "DROP(1);\n"
                self.TempOutputCode += "CALL(NEWLINE);\n"
                self.TempOutputCode += "L_DONT_PRINT_IT" + str(index) + ":\n"
            self.Comment("--------------------------Finish Code for Item " + str(index) + " --------------------------")
        self.OutputCode += ConsTable.InitOutputCode
        self.OutputCode += VarTable.CodeGen()
        self.OutputCode += ConsTable.CodeGen()
        self.OutputCode += ConsFunc.CodeGen()
        self.OutputCode += SymTable.CodeGen()
        self.OutputCode += self.TempOutputCode
        self.MakeCloseFrame()
        return self.OutputCode




VarTable = VariableTable()
ConsFunc = ConstantFucntionsManager(VarTable)

InitConstant = []
MyVoidConstant = VoidConstant(sexprs.Void())
MyNilConstant = NilConstant(sexprs.Nil())
MyBoolConstantFalse = BooleanConstant(sexprs.Boolean(False))
MyBoolConstantTrue = BooleanConstant(sexprs.Boolean(True))
InitConstant.append(MyVoidConstant)
InitConstant.append(MyNilConstant)
InitConstant.append(MyBoolConstantFalse)
InitConstant.append(MyBoolConstantTrue)
ConsTable = ConstantTable(InitConstant, VarTable.NextFreeSpace)

# pay attention! the entry for the symbol table always will be in the first place in the memory!!!
SymTable = SymbolTable(1, ConsTable.GetAddr(MyNilConstant), ConsTable)

YagFunction = "(define Yag \
              (lambda fs            \
              (let ((ms (map        \
              (lambda (fi)       \
              (lambda ms             \
             (apply fi (map (lambda (mi)\
            (lambda args                  \
            (apply (apply mi ms) args))) ms))))\
            fs)))                                \
            (apply (car ms) ms))))"

def Mycompile_scheme_file(source, target):
    schemeFile = open(source, "r+")
    textToParse = schemeFile.read()
    schemeFile.close()

    textToParse = YagFunction + "\n" +textToParse

    ParsingObjects = []
    LastParsingRemaining = textToParse
    ParsingResult,ParsingRemaining= AbstractSchemeExpr.parse(LastParsingRemaining)
    ParsingObjects.append(ParsingResult)
    while((LastParsingRemaining != ParsingRemaining) and (ParsingRemaining != "") ):
        LastParsingRemaining = ParsingRemaining
        ParsingResult,ParsingRemaining= AbstractSchemeExpr.parse(LastParsingRemaining)
        ParsingObjects.append(ParsingResult)

    AnalysisObjects = []
    for item in ParsingObjects:
        AnalysisObjects.append(item.semantic_analysis())

    ConsTable.NextFreeSpace = VarTable.NextFreeSpace
    MyCodeGen = CodeGenrator(AnalysisObjects)
    result = MyCodeGen.code_gen()

    f = open(target, "wb")
    f.write(bytes(result, 'UTF-8'))
    f.close()

    LabelGen.Reset()
    VarTable.Reset()
    ConsFunc.Reset(VarTable)
    SymTable.Reset()
    ConsTable.Reset(VarTable.NextFreeSpace)

