#Regular Expression Implementation ,Written by Adrian Stoll
import sys
import copy

class Node:
    def __lt__(self, other):
        return False
    # All nodes have the following field and method:
    # level - stores prededence information to inform us of when to add parenthesis when pretty pritting
    # __repr__ - prints the regex represented by the parse tree with with any uneccearry parens removed
    pass

class Hole(Node):
    def __init__(self):
        self.level = 0
    def __repr__(self):
        return '#'
    def hasHole(self):
        return True
    def spread(self):
        return
    def spreadAll(self):
        return copy.deepcopy(KleenStar(Or(Character('0'), Character('1'))))
    def spreadNp(self):
        return Character('@emptyset')


class Epsilon(Node):
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

class EpsilonBlank(Node):
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

class Character(Node):
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

class KleenStar(Node):
    def __init__(self, r):
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
            if type(case) != type(KleenStar(Hole())):
                self.r = case
                return True
            else:
                return False

        return self.r.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = copy.deepcopy(Or(Character('0'), Character('1')))
        else:
            self.r.spreadAll()

    def spreadNp(self):
        self.string = None

        if type(self.r) == type((Hole())):
            self.r = Character('@emptyset')
        else:
            self.r.spreadNp()


class Concatenate(Node):
    def __init__(self, a, b):
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
            self.a = copy.deepcopy(case)
            return True
        elif type(self.b)==type((Hole())):
            self.b = copy.deepcopy(case)
            return True
        if self.a.spread(case):
            return True
        else:
            return self.b.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.a)==type((Hole())):
            self.a = copy.deepcopy(KleenStar(Or(Character('0'), Character('1'))))
        else:
            self.a.spreadAll()
        if type(self.b)==type((Hole())):
            self.b = copy.deepcopy(KleenStar(Or(Character('0'), Character('1'))))

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

class Or(Node):
    def __init__(self, a, b):
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

        if type(self.a)==type((Hole())):
            self.a = copy.deepcopy(case)
            return True
        elif type(self.b)==type((Hole())):
            self.b = copy.deepcopy(case)
            return True
        if self.a.spread(case):
            return True
        else:
            return self.b.spread(case)

    def spreadAll(self):
        self.string = None

        if type(self.a)==type((Hole())):
            self.a = copy.deepcopy(KleenStar(Or(Character('0'), Character('1'))))
        else:
            self.a.spreadAll()
        if type(self.b)==type((Hole())):
            self.b = copy.deepcopy(KleenStar(Or(Character('0'), Character('1'))))
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
