# coding=utf8
# pc.py
# Parsing combinators in Python
#
# Programmer: Mayer Goldberg, 2013

class NoMatch(Exception):
    pass

class AbstractParsingCombinator:
    def match(self, s):
        pass

trivialTest = lambda x: True

class const(AbstractParsingCombinator):
    def __init__(self, test=trivialTest):
        self.test = test

    def match(self, s):
        if not s:
            raise NoMatch
        elif self.test(s[0]):
            return (s[0], s[1:])
        else:
            raise NoMatch



class caten(AbstractParsingCombinator):
    def __init__(self, pc1, pc2):
        self.pc1 = pc1
        self.pc2 = pc2

    def match(self, s):
        (e1, s) = self.pc1.match(s)
        (e2, s) = self.pc2.match(s)
        return ((e1, e2), s)


class catenR(AbstractParsingCombinator):
    def __init__(self, pc1, pc2):
        self.pc1 = pc1
        self.pc2 = pc2

    def match(self, s):
        (e1, s) = self.pc1.match(s)
        (e2, s) = self.pc2.match(s)
        return (e1+ e2, s)


class disj(AbstractParsingCombinator):
    def __init__(self, pc1, pc2):
        self.pc1 = pc1
        self.pc2 = pc2

    def match(self, s):
        try:
            return self.pc1.match(s)
        except NoMatch as m:
            return self.pc2.match(s)

class star(AbstractParsingCombinator):
    def __init__(self, pc):
        self.pc = pc

    def match(self, s):
        try:
            (first, s) = self.pc.match(s)
            (result, s) = self.match(s)
            result.insert(0, first)
            return (result, s)
        except NoMatch as m:
            return ([], s)

class starR(AbstractParsingCombinator):
    def __init__(self, pc):
        self.pc = pc

    def match(self, s):
        try:
            (first, s) = self.pc.match(s)
            (result, s) = self.match(s)
            result.insert(0, first)
            return (result, s)
        except NoMatch as m:
            return ([], s)


def plusPacker(m):
    result = m[1]
    result.insert(0, m[0])
    return result

def plus(pc):
    return pack(caten(pc, star(pc)), plusPacker)

class pack(AbstractParsingCombinator):
    def __init__(self, pc, packer):
        self.pc = pc
        self.packer = packer

    def match(self, s):
        (e, s) = self.pc.match(s)
        return (self.packer(e), s)

def maybe(pe):
    return disj(pack(pe, lambda m: (True, m)),
                pack(epsilon(), lambda m: (False, False)))

class butNot(AbstractParsingCombinator):
    def __init__(self, pc1, pc2):
        self.pc1 = pc1
        self.pc2 = pc2

    def match(self, s):
        result = self.pc1.match(s)
        try:
            self.pc2.match(s)
        except NoMatch as m:
            return result
        raise NoMatch

class delayed(AbstractParsingCombinator):
    def __init__(self, thunk):
        self.thunk = thunk

    def match(self, s):
        return self.thunk().match(s)

class end(AbstractParsingCombinator):
    def match(self, s):
        if s:
            raise NoMatch
        else:
            return (True, s)

class debugged(AbstractParsingCombinator):
    def __init__(self, pc, msg):
        self.pc = pc
        self.msg = msg

    def match(self, s):
        print("About to pass the input " + s + \
              " to the <" + self.msg + "> parser")
        return self.pc.match(s)

class epsilon(AbstractParsingCombinator):
    def match(self, s):
        return ([], s)

class rejectAll(AbstractParsingCombinator):
    def match(self, s):
        raise NoMatch

def catenPacker(p):
    (es, a) = p
    es.append(a)
    return es

def catens(*pes):
    result = epsilon()
    for pe in pes:
        result = pack(caten(result, pe), catenPacker)
    return result

def catensR(*pes):
    result = epsilon()
    for pe in pes:
        result = pack(caten(result, pe), catenPacker)
    return result

def disjs(*pes):
    result = rejectAll()
    for pe in pes:
        result = disj(result, pe)
    return result

def pcChar(ch):
    return const(lambda c: c == ch)

def pcCharCI(ch):
    return const(lambda c: c.lower() == ch.lower())

def pcWord(string):
    return catens(*list(map((lambda x: pcChar(x)), string)))

def pcWordCI(string):
    return catens(*list(map((lambda x: pcCharCI(x)), string)))

def pcOneOf(string):
    return disjs(*list(map((lambda x: pcChar(x)), string)))

def pcOneOfCI(string):
    return disjs(*list(map((lambda x: pcCharCI(x)), string)))

def pcRange(fromChar, toChar):
    return const(lambda ch: fromChar <= ch and ch <= toChar)

def pcRangeCI(fromChar, toChar):
    fromChar = fromChar.lower()
    toChar = toChar.lower()

    def inRange(ch):
        ch = ch.lower()
        return fromChar <= ch and ch <= toChar

    return const(inRange)

# The parser stack provides for a simple way
# to compose complex grammars without having
# to define intermediate parsers.

class catenRSpecial(AbstractParsingCombinator):
    def __init__(self, pc1, pc2):
        self.pc1 = pc1
        self.pc2 = pc2

    def match(self, s):
        (e1, s) = self.pc1.match(s)
        (e2, s) = self.pc2.match(s)
        return (str(e1)+ str(e2), s)

class ParserStack:
    def catenRSpecial(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(catenRSpecial(pc1, pc2))
    def __init__(self):
        self.init()

    def init(self):
        self.stack = []
        return self

    def done(self):
        result = self.pop()
        self.init()
        return result

    def pop(self):
        result = self.stack[0]
        self.stack = self.stack[1:]
        return result

    def push(self, x):
        self.stack.insert(0, x)
        return self

    def const(self, test=trivialTest):
        return self.push(const(test))

    def parser(self, pc):
        return self.push(pc)

    def delayed_parser(self, thunk):
        self.push(delayed(thunk))
        return self

    def caten(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(caten(pc1, pc2))
    def butNot(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(butNot(pc1, pc2))

    def catenR(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(catenR(pc1, pc2))
    def butNot(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(butNot(pc1, pc2))


    def disj(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(disj(pc1, pc2))

    def butNot(self):
        pc2 = self.pop()
        pc1 = self.pop()
        return self.push(butNot(pc1, pc2))

    def star(self):
        pc = self.pop()
        return self.push(star(pc))

    def starR(self):
        pc = self.pop()
        return self.push(starR(pc))

    def plus(self):
        pc = self.pop()
        return self.push(plus(pc))

    def maybe(self):
        pc = self.pop()
        return self.push(maybe(pc))

    def pack(self, packer):
        pc = self.pop()
        return self.push(pack(pc, packer))

    def debug(self, msg):
        pc = self.pop()
        return self.push(debugged(pc, msg))

    def catens(self, n):
        pcs = self.stack[0:n]
        pcs.reverse()
        self.stack = self.stack[n:]
        return self.push(catens(*pcs))

    def catensR(self, n):
        pcs = self.stack[0:n]
        pcs.reverse()
        self.stack = self.stack[n:]
        return self.push(catensR(*pcs))

    def disjs(self, n):
        pcs = self.stack[0:n]
        pcs.reverse()
        self.stack = self.stack[n:]
        return self.push(disjs(*pcs))

    def word(self, aString):
        return self.push(pcWord(aString))

    def wordCI(self, aString):
        return self.push(pcWordCI(aString))
    def report(self):
        print('stack size = ' + str(len(self.stack)))
        return self

pcWhite1 = const(lambda ch: ch <= ' ')
pcWhiteStar = star(pcWhite1)
pcWhitePlus = plus(pcWhite1)

pcEverythingButN=const(lambda ch: ch!='\n')
pcEverythingStar=star(pcEverythingButN)

pcEverythingString=const(lambda ch: ch!='"')
pcEverythingStringStar=plus(pcEverythingString)

pcAscii= const(lambda ch: (ch>='0'and ch<='9') or (ch>='a'and ch<='f') or (ch>='A'and ch<='F'))

pcLettersAndNumbers=const(lambda ch: (ch>='0'and ch<='9') or (ch>='a'and ch<='z') or (ch>='A'and ch<='Z')or (ch>='<'and ch<='?') or (ch=='!') \
        or (ch=='$')or (ch=='^')or (ch=='*') or (ch=='-') or (ch=='_') or (ch=='+')or (ch=='/'))
pcEverythingSymbolStar=plus(pcLettersAndNumbers)

pcEveryChar=const(lambda ch: 1==1)