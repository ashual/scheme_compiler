import reader

class AbstractSexpr:
    @staticmethod
    def readFromString(string):
        return reader.pSexpr.match(string)
    def __str__(self):
        return ""

class Symbol(AbstractSexpr):
    def __init__(self,s):
        capital=''
        for e in s:
            if(e>='a' and e<='z'):
                capital=capital+chr(ord(e)+ord('A')-ord('a'))
            else:
                capital=capital+e
        self.sym= capital
    def __str__(self):
        return self.sym

class String(AbstractSexpr):
    def __init__(self,s):
        self.sym= s
    def __str__(self):
        return self.sym

class Boolean(AbstractSexpr):
    def __init__(self,s):
        self.value= s
    def __str__(self):
        if self.value :
            return '#T'
        else:
            return '#F'

class Char(AbstractSexpr):
    def __init__(self,s):
        self.sym= s
    def __str__(self):
        return "#\\" + self.sym

class Integer(AbstractSexpr):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Fraction(AbstractSexpr):
    def __init__(self,Numerator , Denominator):
        self.Numerator = Numerator
        self.Denominator = Denominator
    def __str__(self):
        return str(self.Numerator) + "/" + str(self.Denominator)

class Nil(AbstractSexpr):
    def __str__(self):
        return "()"

class Pair(AbstractSexpr):
    def __init__(self, Item1, Item2):
        self.Item1=Item1
        self.Item2=Item2
    def __str__(self):
        return  "(" + PairToString(self.Item1,self.Item2) + ")"

def PairToString(i1,i2):
    if(isinstance(i2, Nil)):
        return str(i1)
    elif(isinstance(i2, Pair)):
        return str(i1) + " " + PairToString(i2.Item1, i2.Item2)
    else:
        return str(i1) + " . " + str(i2)

def PairToList(i1,i2):
    if(isinstance(i2, Nil)):
        return [i1]
    elif(isinstance(i2, Pair)):
        return [i1] +  PairToList(i2.Item1, i2.Item2)
    else:
        return [i1, i2]

class Vector(AbstractSexpr):
    def __init__(self, Item):
        if(isinstance(Item,Nil)):
            self.values=""
        else:
            self.values= PairToList(Item.Item1, Item.Item2)
    def __str__(self):
        return "#" + str(self.values)

class Void(AbstractSexpr):
    def __str__(self):
        return ""



