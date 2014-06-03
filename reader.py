import pc
import sexprs

ps=pc.ParserStack()

def RemoveCatenPack(x):
    return ''.join(x)
removeCatenStar= lambda x: RemoveCatenPack(x)

pWhiteSpace= pc.const(lambda x: x<=' ')

def pEverything():
    return pc.const(lambda x: x<='z' and x> 'A' )

pBoolean = ps.parser(pc.pcChar('#')) \
    .parser(pc.pcWord('t')) \
    .parser(pc.pcWord('T')) \
    .disjs(2) \
    .pack(lambda x: sexprs.Boolean(True)) \
    .parser(pc.pcWord('f')) \
    .parser(pc.pcWord('F')) \
    .disjs(2) \
    .pack(lambda x: sexprs.Boolean(False)) \
    .disjs(2) \
    .caten() \
    .pack(lambda x: x[1]) \
    .done()

pLineComment=  ps.parser(pc.pcChar(';')) \
    .parser(pc.pcEverythingStar) \
    .pack(removeCatenStar) \
    .parser(pc.pcChar('\n')) \
    .caten() \
    .caten() \
    .done()

pSexprsComment=  ps.parser(pc.pcChar('#')) \
    .parser(pc.pcChar(';')) \
    .delayed_parser(lambda : pSexpr) \
    .caten() \
    .caten() \
    .done()

pCommentsAndWhitespaces= ps.parser(pWhiteSpace) \
    .parser(pSexprsComment) \
    .parser(pLineComment) \
    .disjs(3) \
    .star() \
    .done()

pSymbol= ps.parser(pc.pcEverythingSymbolStar) \
    .pack(removeCatenStar) \
    .pack(lambda x: sexprs.Symbol(x)) \
    .done()

pString= ps.parser(pc.pcChar('"')) \
    .parser(pc.pcWord("\l")) \
    .parser(pc.pcWord("\"")) \
    .parser(pc.pcEverythingStringStar) \
    .pack(removeCatenStar) \
    .disjs(3) \
    .catenRSpecial() \
    .parser(pc.pcChar('"')) \
    .catenRSpecial() \
    .parser(pc.pcChar('"')) \
    .parser(pc.pcChar('"')) \
    .catenRSpecial() \
    .disj() \
    .pack(lambda x: sexprs.String(x[1:-1])) \
    .done()

pNamedChars= ps.parser(pc.pcWord("newline")) \
    .parser(pc.pcWord("return")) \
    .parser(pc.pcWord("tab")) \
    .parser(pc.pcWord("page")) \
    .parser(pc.pcWord("lambda")) \
    .disjs(5) \
    .pack(removeCatenStar) \
    .done()

pHexChars= ps.parser(pc.pcChar('x')) \
    .parser(pc.pcChar('X')) \
    .disj() \
    .parser(pc.pcAscii) \
    .parser(pc.pcAscii) \
    .parser(pc.pcAscii) \
    .parser(pc.pcAscii) \
    .catenR() \
    .catenR() \
    .catenR() \
    .parser(pc.pcAscii) \
    .parser(pc.pcAscii) \
    .catenR() \
    .disj() \
    .catenR() \
    .done()

pChar=ps.parser(pc.pcChar('#')) \
    .parser(pc.pcChar('\\')) \
    .parser(pNamedChars) \
    .parser(pHexChars) \
    .parser(pc.pcEveryChar) \
    .disjs(3) \
    .catenR() \
    .catenR() \
    .pack(lambda x: sexprs.Char(x[2:])) \
    .done()

def QuoteGen(prefix,name):
    return ps.parser(pc.pcWord(prefix)) \
        .pack(removeCatenStar) \
        .delayed_parser(lambda: pSexpr) \
        .caten() \
        .pack(lambda m: sexprs.Pair(sexprs.Symbol(name), sexprs.Pair(m[1], sexprs.Nil()))) \
        .done()

pQuote= QuoteGen("'", 'quote')
pQuasiQuote= QuoteGen("`",'quasiquote')
pUnquoteSlicing= QuoteGen(",@",'unquote-splicing')
pUnquote= QuoteGen(",",'unquote')

def ListToPair(myList,endOfList) :
    if myList:
        return sexprs.Pair(myList[0], ListToPair(myList[1:], endOfList))
    else :
        return endOfList


def RemoveMaybePack(x):
    if x[0]:
        return x[1]
    else:
        return ''

def RemoveCatenPack(x):
    return ''.join(x)

def RemoveConstPack(x):
    return x[0]

def HandleSign (x):
    if(x[0] == ''):
        return x[1]
    else:
        if(x[0][0] == '-'):
            return sexprs.Integer(int(0 - int(str(x[1]))))
        else:
            return x[1]

pZero = ps.parser(pc.pcWord('0')).pack(lambda x: RemoveConstPack(x)) \
    .plus().pack(lambda x: RemoveCatenPack(x)) \
    .done()

pHexaPrefix =  ps.parser(pc.pcWord('0')) \
    .parser(pc.pcWord('x')) \
    .parser(pc.pcWord('X')) \
    .parser(pc.pcWord('h')) \
    .parser(pc.pcWord('H')) \
    .disjs(4) \
    .caten() \
    .done()

pHexaAddition =  ps.parser(pc.pcRangeCI('a', 'f')) \
    .done()

pSignPrefix =  ps.parser(pc.pcWord('+')) \
    .parser(pc.pcWord('-')) \
    .disj() \
    .maybe().pack(lambda x: RemoveMaybePack(x)) \
    .done()

pSimpleDecNumber = ps.parser(pc.pcRange('0','9')) \
    .plus().pack(lambda x: RemoveCatenPack(x)) \
    .done()

pPositivDecNumber =  ps.parser(pc.pcWord('0')).pack(lambda x: RemoveConstPack(x)) \
    .star().pack(lambda x: RemoveCatenPack(x)) \
    .parser(pc.pcRange('1','9')) \
    .caten().pack(lambda x: RemoveCatenPack(x)) \
    .parser(pc.pcRange('0','9')) \
    .star().pack(lambda x: RemoveCatenPack(x)) \
    .caten().pack(lambda x: RemoveCatenPack(x)) \
    .done()

pHexaNumberPart  =  ps.parser(pSimpleDecNumber) \
    .parser(pHexaAddition) \
    .disj() \
    .plus().pack(lambda x: RemoveCatenPack(x)) \
    .done()

pSimpleHexaNumber =  ps.parser(pHexaPrefix) \
    .parser(pHexaNumberPart) \
    .caten() \
    .pack(lambda x: x[1]) \
    .done()

pPositivHexaNumber =   ps.parser(pHexaPrefix) \
    .parser(pPositivDecNumber) \
    .parser(pZero) \
    .maybe() \
    .parser(pHexaAddition) \
    .caten().pack(lambda x: x[1]) \
    .disj() \
    .caten().pack(lambda x: x[1]) \
    .parser(pHexaNumberPart) \
    .star().pack(lambda x: RemoveCatenPack(x)) \
    .caten().pack(lambda x: RemoveCatenPack(x)) \
    .done()

pSimpleNumber = ps.parser(pSimpleHexaNumber).pack(lambda x: sexprs.Integer(int(x, 16))) \
    .parser(pSimpleDecNumber).pack(lambda x: sexprs.Integer(int(x))) \
    .disj() \
    .done()

pPositivNumber = ps.parser(pPositivHexaNumber).pack(lambda x: sexprs.Integer(int(x, 16))) \
    .parser(pPositivDecNumber).pack(lambda x: sexprs.Integer(int(x))) \
    .disj() \
    .done()

pSignNumber =  ps.parser(pSignPrefix) \
    .parser(pSimpleNumber) \
    .caten() \
    .pack(lambda x: HandleSign(x)) \
    .done()

pFractions = ps.parser(pSignNumber) \
    .parser(pc.pcWord('/')) \
    .caten() \
    .parser(pPositivNumber) \
    .caten() \
    .pack(lambda x: sexprs.Fraction(x[0][0],x[1] )) \
    .done()
########################################### end of number part ###########################################

pNil = ps.parser(pc.pcWord('(')) \
    .parser(pCommentsAndWhitespaces) \
    .parser(pc.pcWord(')')) \
    .catens(3) \
    .pack(lambda x: sexprs.Nil()) \
    .done()

########################################### end of nil part ###########################################

pSexpr = ps.parser(pCommentsAndWhitespaces) \
    .delayed_parser(lambda : pProperList) \
    .delayed_parser(lambda : pImproperList) \
    .delayed_parser(lambda : pVector) \
    .parser(pBoolean) \
    .parser(pFractions) \
    .parser(pSignNumber) \
    .parser(pNil) \
    .parser(pQuote) \
    .parser(pQuasiQuote) \
    .parser(pUnquote) \
    .parser(pUnquoteSlicing) \
    .parser(pChar) \
    .parser(pSymbol) \
    .parser(pString) \
    .disjs(14) \
    .caten() \
    .parser(pCommentsAndWhitespaces) \
    .caten() \
    .pack(lambda x: x[0][1]) \
    .done()

pProperList = ps.parser(pc.pcWord('(')) \
    .parser(pSexpr) \
    .star() \
    .parser(pc.pcWord(')')) \
    .catens(3) \
    .pack(lambda x: ListToPair(x[1], sexprs.Nil())) \
    .done()

pImproperList = ps.parser(pc.pcWord('(')) \
    .parser(pSexpr) \
    .plus() \
    .parser(pc.pcWord('.')) \
    .parser(pSexpr) \
    .parser(pc.pcWord(')')) \
    .catens(5) \
    .pack(lambda x: ListToPair(x[1], x[3])) \
    .done()

pVector = ps.parser(pc.pcWord('#')) \
    .parser(pProperList) \
    .caten() \
    .pack(lambda x: sexprs.Vector(x[1])) \
    .done()



#p, p2=pCommentsAndWhitespaces.match("(if x x (z))")
#sd= '#t'
#p, p2=sexprs.AbstractSexpr.readFromString("(lambda () 2")
#print(p,"remaining:",p2)
