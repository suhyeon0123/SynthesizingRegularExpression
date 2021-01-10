#Regular Expression Implementation ,Written by Adrian Stoll
import copy
import random
import re2 as re
from config import *

def get_rand_re(depth):

    case = random.randrange(0,2+depth)

    if case > 2:
        cha = True
    else:
        cha = False

    if cha :
        case = random.randrange(0,2)
        if case == 0:
            return Character('0')
        else:
            return Character('1')
    else :
        case = random.randrange(0,5)
        if case <= 0:
            return Or()
        elif case <= 1:
            return Concatenate(Hole(),Hole())
        elif case <= 2:
            return KleenStar()
        elif case <= 3:
            return Question()
        else:
            return Hole()


class Hole:
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return '#'
    def hasHole(self):
        return True
    def spread(self, case, parentId):
        return False
    def spreadAll(self):
        return KleenStar(Or(Character('0'), Character('1')))
    def spreadRand(self):
        return Character('0') if random.random() <0.5 else Character('1')
    def spreadNp(self):
        return Character('@emptyset')
    def unroll(self):
        return
    def split(self, side):
        return False
    def make_child(self):
        return
    def overlap(self):
        return False
    def equivalent_KO(self, parentId):
        return False
    def getn(self):
        return 0
    def orinclusive(self):
        return False
    def kinclusive(self):
        return False


class RE:
    def __lt__(self, other):
        return False
    def __init__(self, r=Hole()):
        self.r = r
        self.hasHole2 = True
        self.string = None
        self.first = True
        self.cost = HOLE_COST

    def __repr__(self):
        if not self.string:
            self.string = repr(self.r)

        return self.string
    def hasHole(self):
        if not self.hasHole2:
            return False
        if not self.r.hasHole():
            self.hasHole2 = False
        return self.hasHole2
    def spread(self, case, parentId):

        if type(case) == type(Concatenate(Hole(),Hole())):
            self.cost += HOLE_COST + CONCAT_COST
        elif type(case) == type(Or()):
            self.cost += HOLE_COST + UNION_COST
        elif type(case) == type(KleenStar()) or type(case) == type(Question()):
            self.cost += CLOSURE_COST
        else:
            self.cost += - HOLE_COST + SYMBOL_COST

        self.string = None

        if self.first:
            self.r = case
            self.first = False
            return True
        else:
            return self.r.spread(case,10)
    def spreadAll(self):
        self.string = None
        if type(self.r) == type((Hole())):
            self.r = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.r.spreadAll()
    def spreadRand(self):
        self.string = None
        self.r.spreadRand()
    def spreadNp(self):
        self.string = None
        if type(self.r) == type((Hole())):
            self.r = Character('@emptyset')
        else:
            self.r.spreadNp()
    def unroll(self):
        self.string = None
        self.r.unroll()
    def unroll_entire(self):
        self.string = None
        s1 = copy.deepcopy(self.r.r)
        s2 = copy.deepcopy(self.r.r)
        s3 = copy.deepcopy(self.r)
        self.r = Concatenate(s1,s2,s3)
        for index, regex in enumerate(self.r.list):
            self.r.list[index].unroll()
    def split(self, side):
        self.string = None
        if type(self.r) == type(Or()):
            if type(self.r.list[side]) == type(KleenStar()):
                self.r = copy.deepcopy(self.r.list[side].r)
            else:
                self.r = copy.deepcopy(self.r.list[side])
            return True

        return self.r.split(side)
    def make_child(self, count):
        if type(self.r) == type((Hole())):
            self.r = get_rand_re(count)
        else:
            self.r.make_child(count)
    def overlap(self):
        return self.r.overlap()
    def equivalent_KO(self, parentId):
        return self.r.equivalent_KO(10)
    def getn(self):
        return self.r.getn()
    def orinclusive(self):
        return self.r.orinclusive()
    def kinclusive(self):
        return self.r.kinclusive()

class Epsilon(RE):
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return '@epsilon'
    def hasHole(self):
        return False
    def spread(self, case, parentId):
        return False
    def spreadAll(self):
        return
    def spreadRand(self):
        return
    def spreadNp(self):
        return
    def unroll(self):
        return
    def split(self, side):
        return False
    def make_child(self, count):
        return
    def overlap(self):
        return False
    def equivalent_KO(self, parentId):
        return False
    def getn(self):
        return 0
    def orinclusive(self):
        return False
    def kinclusive(self):
        return False

class EpsilonBlank(RE):
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return ''
    def hasHole(self):
        return False
    def spread(self, case, parentId):
        return False
    def spreadAll(self):
        return
    def spreadRand(self):
        return
    def spreadNp(self):
        return
    def unroll(self):
        return
    def split(self, side):
        return False
    def make_child(self, count):
        return
    def overlap(self):
        return False
    def equivalent_KO(self, parentId):
        return False
    def getn(self):
        return 0
    def orinclusive(self):
        return False
    def kinclusive(self):
        return False

class Character(RE):
    def __init__(self, c):
        self.c = c
        self.level = 0
    def __repr__(self):
        return self.c
    def hasHole(self):
        return False
    def spread(self, case, parentId):
        return False
    def spreadAll(self):
        return self.c
    def spreadRand(self):
        return
    def spreadNp(self):
        return self.c
    def unroll(self):
        return
    def split(self, side):
        return False
    def make_child(self, count):
        return
    def overlap(self):
        return False
    def equivalent_KO(self, parentId):
        return False
    def getn(self):
        return 0
    def orinclusive(self):
        return False
    def kinclusive(self):
        return False

class KleenStar(RE):
    def __init__(self, r=Hole()):
        self.r = r
        self.level = 1
        self.string = None
        self.hasHole2 = True
    def __repr__(self):
        if self.string:
            return self.string

        if '{}'.format(self.r) == '@emptyset':
            self.string = '@epsilon'
            return self.string

        if '{}'.format(self.r) == '@epsilon':
            self.string = '@epsilon'
            return self.string

        if self.r.level > self.level:
            self.string = '({})*'.format(self.r)
            return self.string
        else:
            self.string = '{}*'.format(self.r)
            return self.string

    def hasHole(self):
        if not self.hasHole2:
            return False

        if not self.r.hasHole():
            self.hasHole2 = False
        return self.hasHole2

    def spread(self, case, parentId):
        self.string = None

        if type(self.r)==type((Hole())):
            if type(case) != type(KleenStar(Hole())) and type(case) != type(Question(Hole())):
                self.r = case
                return True
            else:
                return False

        return self.r.spread(case,0)

    def spreadAll(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = Or(Character('0'), Character('1'))
        else:
            self.r.spreadAll()
    def spreadRand(self):
        self.string = None
        if type(self.r) == type((Hole())):
            self.r = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.r.spreadRand()
    def spreadNp(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = Character('@emptyset')
        else:
            self.r.spreadNp()

    def unroll(self):
        self.string = None
        self.r.unroll()

    def split(self, side):
        self.string = None
        if type(self.r) == type(Or()):
            if side == -1:
                self.r = Hole()
            elif type(self.r.list[side]) == type(KleenStar()):
                self.r = copy.deepcopy(self.r.list[side].r)
            else:
                self.r = copy.deepcopy(self.r.list[side])
            return True

        '''elif type(self.r) == type(Question()):
            if side == 0:
                self.r = copy.deepcopy(self.r.r.r)
            else:
                self.r = Epsilon()
            return True'''

        return self.r.split(side)

    def make_child(self, count):
        if type(self.r) == type((Hole())):
            while True:
                x = get_rand_re(count)
                if type(x) != type(KleenStar()) and type(x) != type(Question()):
                    self.r = x
                    break
        else:
            self.r.make_child(count)
    def overlap(self):
        return self.r.overlap()
    def equivalent_KO(self, parentId):
        return self.r.equivalent_KO(0)
    def getn(self):
        return self.r.getn()
    def orinclusive(self):
        return self.r.orinclusive()
    def kinclusive(self):
        if type(self.r) == type(Concatenate()):
            for regex in self.r.list:
                if type(regex) == type(KleenStar()) and not regex.hasHole():
                    count = 0
                    for regex2 in self.r.list:
                        if repr(regex.r) == repr(regex2) or repr(regex)==repr(regex2):
                            count +=1
                    if count == len(self.r.list):
                        return True
                if regex.kinclusive():
                    return True
        if type(self.r) == type(Concatenate()):
            if '(0|1)*' in repr(self.r):
                return True

        '''if type(self.r) == type(Or()):
            for regex in self.r.list:
                if type(regex) == type(Concatenate()):
                    for regex2 in regex.list:
                        if type(regex2) == type(KleenStar()) and not regex2.hasHole():
                            count = 0
                            for regex3 in regex.list:
                                if repr(regex2.r) == repr(regex3) or repr(regex2)==repr(regex3):
                                    count+=1
                            if count == len(self.r.list):
                                print('type2')
                                return True'''






class Question(RE):
    def __init__(self, r=Hole()):
        self.r = r
        self.level = 1
        self.string = None
        self.hasHole2 = True
    def __repr__(self):
        if self.string:
            return self.string

        if '{}'.format(self.r) == '@emptyset':
            self.string = '@epsilon'
            return self.string

        if '{}'.format(self.r) == '@epsilon':
            self.string = '@epsilon'
            return self.string

        if self.r.level > self.level:
            self.string = '({})?'.format(self.r)
            return self.string
        else:
            self.string = '{}?'.format(self.r)
            return self.string

    def hasHole(self):
        if not self.hasHole2:
            return False

        if not self.r.hasHole():
            self.hasHole2 = False
        return self.hasHole2

    def spread(self, case, parentId):
        self.string = None

        if type(self.r)==type((Hole())):
            if type(case) != type(KleenStar(Hole())) and type(case) != type(Question(Hole())):
                self.r = case
                return True
            else:
                return False

        return self.r.spread(case, 1)

    def spreadAll(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.r.spreadAll()

    def spreadRand(self):
        self.string = None
        if type(self.r) == type((Hole())):
            self.r = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.r.spreadRand()

    def spreadNp(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = Character('@emptyset')
        else:
            self.r.spreadNp()

    def unroll(self):
        self.string = None
        self.r.unroll()

    def split(self, side):
        return

    def make_child(self, count):
        if type(self.r) == type((Hole())) :
            while True:
                x = get_rand_re(count)
                if type(x) != type(Question()) and type(x) != type(KleenStar()):
                    self.r = x
                    break
        else:
            self.r.make_child(count)
    def overlap(self):
        return self.r.overlap()
    def equivalent_KO(self, parentId):
        return self.r.equivalent_KO(1)
    def getn(self):
        return self.r.getn()
    def orinclusive(self):
        return self.r.orinclusive()
    def kinclusive(self):
        return self.r.kinclusive()

class Concatenate(RE):
    def __init__(self, *regexs):
        self.list = list()
        for regex in regexs:
            self.list.append(regex)
        self.level = 2
        self.string = None
        self.hasHole2 = True

    def __repr__(self):

        if self.string:
            return self.string

        def formatSide(side):
            if side.level > self.level:
                return '({})'.format(side)
            else:
                return '{}'.format(side)

        for regex in self.list:
            if '@emptyset' in repr(regex):
                self.string = '@emptyset'
                return self.string

        str_list = []
        for regex in self.list:
            if '@epsilon' != repr(regex):
                str_list.append(formatSide(regex))
        return ''.join(str_list)

    def hasHole(self):
        if not self.hasHole2:
            return False

        self.hasHole2 = any(list(i.hasHole() for i in self.list))
        return self.hasHole2

    def spread(self, case, parentId):
        self.string = None

        for index, regex in enumerate(self.list):
            if type(regex) == type(Hole()) and type(case) == type(Concatenate(Hole(),Hole())):
                self.list.append(Hole())
                return True
            elif type(regex) == type(Hole()):
                self.list[index] = case
                return True
            if self.list[index].spread(case, 2):
                return True

        return False

    def spreadAll(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(Hole()):
                self.list[index] = KleenStar(Or(Character('0'), Character('1')))
            else:
                self.list[index].spreadAll()

    def spreadRand(self):
        self.string = None
        if type(self.a) == type((Hole())):
            self.a = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.a.spreadRand()
        if type(self.b) == type((Hole())):
            self.b = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.b.spreadRand()

    def spreadNp(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(Hole()):
                self.list[index] = Character('@emptyset')
            else:
                self.list[index].spreadNp()

    def unroll(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(KleenStar()) and not regex.hasHole():
                a = copy.deepcopy(regex.r)
                b = copy.deepcopy(regex.r)
                c = copy.deepcopy(regex)
                self.list[index] = Concatenate(a,b,c)
                self.list[index].list[0].unroll()
                self.list[index].list[1].unroll()
                self.list[index].list[2].r.unroll()
            else:
                self.list[index].unroll()

    def split(self, side):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(Or()):
                if side == -1:
                    self.list[index] = Hole()
                else:
                    self.list[index] = copy.deepcopy(self.list[index].list[side])
                return True
            if self.list[index].split(side):
                return True

        '''elif type(self.a) == type(Question()):
                    self.a = copy.deepcopy(self.a.r) if side == 0 else Epsilon()
                    return True
                elif type(self.b) == type(Or()):
                    self.b = copy.deepcopy(self.b.a) if side == 0 else copy.deepcopy(self.b.b)
                    return True
                elif type(self.b) == type(Question()):
                    self.b = copy.deepcopy(self.b.r) if side == 0 else Epsilon()
                    return True'''

        return False

    def make_child(self, count):
        if type(self.a) == type((Hole())):
            self.a = get_rand_re(count)
        else:
            self.a.make_child(count)

        if type(self.b) == type((Hole())):
            self.b = get_rand_re(count)
        else:
            self.b.make_child(count)
    def overlap(self):
        return any(list(i.overlap() for i in self.list))
    def equivalent_KO(self, parentId):
        if parentId == 0 and not self.hasHole():
            return bool(re.fullmatch(repr(self), '0')) and bool(re.fullmatch(repr(self), '1'))
        for regex in self.list:
            if regex.equivalent_KO(3):
                return True
        return False

    def getn(self):
        for index, regex in enumerate(self.list):
            tmp = regex.getn()
            if tmp != 0:
                return tmp
        return 0
    def orinclusive(self):
        return any(list(i.orinclusive() for i in self.list))
    def kinclusive(self):
        return any(list(i.kinclusive() for i in self.list))

class Or(RE):
    def __init__(self, a=Hole(), b=Hole()):
        self.list = list()
        self.list.append(a)
        self.list.append(b)
        self.level = 3
        self.string = None
        self.hasHole2 = True

    def __repr__(self):
        if self.string:
            return self.string

        def formatSide(side):
            if side.level > self.level:
                return '({})'.format(side)
            else:
                return '{}'.format(side)

        str_list = []
        for regex in self.list:
            if repr(regex) != '@emptyset':
                if str_list:
                    str_list.append("|")
                str_list.append(formatSide(regex))
        if not str_list:
            return '@emptyset'
        else:
            return ''.join(str_list)

    def hasHole(self):
        if not self.hasHole2:
            return False

        self.hasHole2 = any(list(i.hasHole() for i in self.list))
        return self.hasHole2


    def spread(self, case, parentId):
        self.string = None

        for index, regex in enumerate(self.list):
            if type(regex) == type((Hole())) and type(case)==type(Or()):
                self.list.append(Hole())
                self.list.sort(key=lambda regex: repr(regex))
                return True
            elif type(regex)==type((Hole())) and type(case)!=type(Question()) and not (parentId == 0 and type(case) == type(KleenStar())):
                self.list[index] = case
                self.list.sort(key=lambda regex: repr(regex))
                return True
            if self.list[index].spread(case, 3):
                self.list.sort(key=lambda regex: repr(regex))
                return True
        return False

    def spreadAll(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex)==type(Hole()):
                self.list[index] = KleenStar(Or(Character('0'), Character('1')))
            else:
                self.list[index].spreadAll()

    def spreadNp(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(Hole()):
                self.list[index] = Character('@emptyset')
            else:
                self.list[index].spreadNp()
    def spreadRand(self):
        self.string = None
        if type(self.a) == type((Hole())):
            self.a = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.a.spreadRand()
        if type(self.b) == type((Hole())):
            self.a = Character('0') if random.random() <0.5 else Character('1')
        else:
            self.b.spreadRand()

    def unroll(self):
        self.string = None
        for index, regex in enumerate(self.list):
            if type(regex) == type(KleenStar()) and not regex.hasHole():
                self.list[index] = Concatenate(regex.r, regex.r, KleenStar(regex.r))
                for index2, regex2 in enumerate(self.list[index].list):
                    self.list[index].list[index2].unroll()
            else:
                self.list[index].unroll()

    def split(self, side):
        return

    def make_child(self, count):
        if type(self.a) == type((Hole())):
            self.a = get_rand_re(count)
        else:
            self.a.make_child(count)

        if type(self.b) == type((Hole())):
            self.b = get_rand_re(count)
        else:
            self.b.make_child(count)

    def overlap(self):
        noholelist = []
        for regex in self.list:
            if not regex.hasHole():
                noholelist.append(repr(regex))
        noholeset = set(noholelist)
        #print(noholelist,"  ",noholeset)
        if len(noholelist) != len(noholeset):
            return True

        for regex in self.list:
            if regex.overlap():
                return True
        return False

    def equivalent_KO(self, parentId):
        return any(list(i.equivalent_KO(2) for i in self.list))



    def getn(self):
        for regex in self.list:
            if type(regex) == type(Hole()):
                return -1
            if type(regex) == type(KleenStar()) and type(regex.r) == type(Hole()):
                return -1
            if type(regex) == type(Concatenate(Hole(), Hole())):
                for regex2 in regex.list:
                    if type(regex2) == type(Hole()) or (type(regex2) == type(KleenStar()) and type(regex2.r) == type(Hole()) ):
                        return -1
        return len(self.list)

    def orinclusive(self):
        for regex in self.list:

            if type(regex) == type(KleenStar()) and not regex.hasHole():
                for regex2 in self.list:

                    if repr(regex.r) == repr(regex2):
                        return True

                    if type(regex2) == type(Concatenate()):
                        count = 0
                        for inconcat in regex2.list:
                            if repr(inconcat) != repr(regex.r):
                                break
                            count += 1
                        if count == len(regex2.list):
                            #print("type2")
                            return True


            if type(regex) == type(KleenStar()) and type(regex.r) == type(Or()):
                for inconcat in regex.r.list:
                    if not inconcat.hasHole():
                        for x in self.list:
                            if repr(x) == repr(inconcat):
                                #print("type3")
                                return True


            if regex.orinclusive():
                return True

        return False
    def kinclusive(self):
        return any(list(i.kinclusive() for i in self.list))




