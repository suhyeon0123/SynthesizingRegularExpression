#Regular Expression Implementation ,Written by Adrian Stoll
import copy

class Hole:
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return '#'
    def hasHole(self):
        return True
    def spread(self, case):
        return False
    def spreadAll(self):
        return KleenStar(Or(Character('0'), Character('1')))
    def spreadNp(self):
        return Character('@emptyset')
    def unroll(self):
        return
    def split(self, side):
        return False



class RE:
    def __lt__(self, other):
        return False
    def __init__(self, r=Hole()):
        self.r = r
        self.hasHole2 = True
        self.string = None
        self.first = True

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
    def spread(self, case):
        self.string = None

        if self.first:
            self.r = case
            self.first = False
            return True
        else:
            return self.r.spread(case)
    def spreadAll(self):
        self.string = None
        if type(self.r) == type((Hole())):
            self.r = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.r.spreadAll()

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
        s1 = copy.deepcopy(self.r.r)
        s2 = copy.deepcopy(self.r)
        r = Concatenate(Concatenate(s1,s1),s2)
    def split(self, side):
        self.r.split(side)
        self.string = None


class Epsilon(RE):
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return '@epsilon'
    def hasHole(self):
        return False
    def spread(self, case):
        return False
    def spreadAll(self):
        return
    def spreadNp(self):
        return
    def unroll(self):
        return
    def split(self, side):
        return False


class EpsilonBlank(RE):
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return ''
    def hasHole(self):
        return False
    def spread(self, case):
        return False
    def spreadAll(self):
        return
    def spreadNp(self):
        return
    def unroll(self):
        return
    def split(self, side):
        return False


class Character(RE):
    def __init__(self, c):
        self.c = c
        self.level = 0
    def __repr__(self):
        return self.c
    def hasHole(self):
        return False
    def spread(self, case):
        return False
    def spreadAll(self):
        return self.c
    def spreadNp(self):
        return self.c
    def unroll(self):
        return
    def split(self, side):
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

    def spread(self, case):
        self.string = None

        if type(self.r)==type((Hole())):
            if type(case) != type(KleenStar(Hole())) and type(case) != type(Question(Hole())):
                self.r = case
                return True
            else:
                return False

        return self.r.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = Or(Character('0'), Character('1'))
        else:
            self.r.spreadAll()

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
            if side == 0:
                if type(self.r.a) == type(KleenStar()):
                    self.r = copy.deepcopy(self.r.a.r)
                else:
                    self.r = copy.deepcopy(self.r.a)
                return True
            else:
                if type(self.r.b) == type(KleenStar()):
                    self.r = copy.deepcopy(self.r.b.r)
                else:
                    self.r = copy.deepcopy(self.r.b)
                return True
        return self.r.split(side)


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

    def spread(self, case):
        self.string = None

        if type(self.r)==type((Hole())):
            if type(case) != type(KleenStar(Hole())) and type(case) != type(Question(Hole())):
                self.r = case
                return True
            else:
                return False

        return self.r.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.r.spreadAll()

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
            if side == 0:
                self.r = copy.deepcopy(self.r.a)
                return True
            else:
                self.r = copy.deepcopy(self.r.b)
                return True
        return self.r.split(side)


class Concatenate(RE):
    def __init__(self, a=Hole(), b=Hole()):
        self.a, self.b = a, b
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

        if '@emptyset' in repr(self.a) or '@emptyset' in repr(self.b):
            self.string = '@emptyset'
            return self.string

        if '@epsilon' == repr(self.a):
            self.string = formatSide(self.b)
            return self.string
        elif '@epsilon' == repr(self.b):
            self.string = formatSide(self.a)
            return self.string

        self.string = formatSide(self.a) + formatSide(self.b)
        return self.string

    def hasHole(self):

        if not self.hasHole2:
            return False

        self.hasHole2 = self.a.hasHole() or self.b.hasHole()

        return self.hasHole2

    def spread(self, case):
        self.string = None

        if type(self.a)==type((Hole())):
            self.a = case
            return True
        elif type(self.b)==type((Hole())):
            self.b = case
            return True
        if self.a.spread(case):
            return True
        else:
            return self.b.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.a)==type((Hole())):
            self.a = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.a.spreadAll()
        if type(self.b)==type((Hole())):
            self.b = KleenStar(Or(Character('0'), Character('1')))

        else:
            self.b.spreadAll()

    def spreadNp(self):
        self.string = None
        if type(self.a)==type((Hole())):
            self.a = Character('@emptyset')
        else:
            self.a.spreadNp()

        if type(self.b)==type((Hole())):
            self.b = Character('@emptyset')
        else:
            self.b.spreadNp()

    def unroll(self):
        self.string = None
        if type(self.a) == type(KleenStar()) and type(self.a.r) != type(Hole()):
            s = copy.deepcopy(self.a.r)
            self.a = Concatenate(Concatenate(s, s), KleenStar(s))

            self.a.a.unroll()
            self.a.b.unroll()

        else:
            self.a.unroll()

        if type(self.b) == type(KleenStar()) and type(self.b.r) != type(Hole()):
            s = copy.deepcopy(self.b.r)
            self.b = Concatenate(Concatenate(s, s), KleenStar(s))

            self.b.a.unroll()
            self.b.b.unroll()

        else:
            self.b.unroll()

    def split(self, side):
        self.string = None

        if type(self.a) == type(Or()):
            if side == 0:
                self.a = copy.deepcopy(self.a.a)
                return True
            else:
                self.a = copy.deepcopy(self.a.b)
                return True

        elif type(self.b) == type(Or()):
            if side == 0:
                self.b = copy.deepcopy(self.b.a)
                return True
            else:
                self.b = copy.deepcopy(self.b.b)
                return True

        if self.a.split(side):
            return True
        else:
            return self.b.split(side)


class Or(RE):
    def __init__(self, a=Hole(), b=Hole()):
        self.a, self.b = a, b
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

        if repr(self.a) == '@emptyset':
            self.string = formatSide(self.b)
            return self.string
        elif repr(self.b) == '@emptyset':
            self.string = formatSide(self.a)
            return self.string

        self.string = formatSide(self.a) + '|' + formatSide(self.b)
        return self.string

    def hasHole(self):

        if not self.hasHole2:
            return False

        self.hasHole2 = self.a.hasHole() or self.b.hasHole()

        return self.hasHole2

    def spread(self, case):
        self.string = None

        if type(self.a)==type((Hole())) and type(case)!=type(Question()):
            self.a = case
            return True
        elif type(self.b)==type((Hole())) and type(case)!=type(Question()) :
            if type(self.a) == type(Character('')) and type(case) == type(Character('')):
                if self.a.c == case.c:
                    return False
            self.b = case
            return True

        if self.a.spread(case):
            return True
        else:
            return self.b.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.a)==type((Hole())):
            self.a = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.a.spreadAll()
        if type(self.b)==type((Hole())):
            self.b = KleenStar(Or(Character('0'), Character('1')))
        else:
            self.b.spreadAll()

    def spreadNp(self):
        self.string = None

        if type(self.a) == type((Hole())):
            self.a = Character('@emptyset')
        else:
            self.a.spreadNp()
        if type(self.b) == type((Hole())):
            self.b = Character('@emptyset')
        else:
            self.b.spreadNp()

    def unroll(self):
        self.string = None
        if type(self.a) == type(KleenStar()) and not self.a.hasHole():
            s = copy.deepcopy(self.a.r)
            self.a = Concatenate(Concatenate(s, s), KleenStar(s))

        if type(self.b) == type(KleenStar()) and not self.b.hasHole():
            s = copy.deepcopy(self.b.r)
            self.a = Concatenate(Concatenate(s, s), KleenStar(s))


        self.a.unroll()
        self.b.unroll()


    def split(self, side):
        self.string = None

        if type(self.a) == type(Or()):
            if side == 0:
                self.a = copy.deepcopy(self.a.a)
                return True
            else:
                self.a = copy.deepcopy(self.a.b)
                return True

        elif type(self.b) == type(Or()):
            if side == 0:
                self.b = copy.deepcopy(self.b.a)
                return True
            else:
                self.b = copy.deepcopy(self.b.b)
                return True

        if self.a.split(side):
            return True
        else:
            return self.b.split(side)


