from queue import PriorityQueue
from util import *
import argparse
from examples import*

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--examples", type=int,
                    help="Example number")
parser.add_argument("-u", "--unambiguous", help="Set ambiguity",
                    action="store_true")
args = parser.parse_args()


sys.setrecursionlimit(5000000)

import faulthandler

faulthandler.enable()



w = PriorityQueue()

scanned = set()

w.put((RE().cost, RE()))
if args.examples:
    examples = Examples(args.examples)
else:
    examples = Examples(5)
answer = examples.getAnswer()

print(examples.getPos(), examples.getNeg())

i = 0
traversed = 1
start = time.time()
prevCost = 0

finished = False


while not w.empty() and not finished:
    tmp = w.get()
    s = tmp[1]
    cost = tmp[0]

    prevCost = cost
    hasHole = s.hasHole()

    #print("state : ", s, " cost: ",cost)
    if hasHole:

        for j, new_elem in enumerate([Character('0'), Character('1'), Or(),  Or(Character('0'),Character('1')),Concatenate(Hole(),Hole()), KleenStar(),Question()]):

            #print(repr(s), repr(new_elem))

            k = copy.deepcopy(s)

            if i ==0 and (type(new_elem)==type(Question())):
                continue
            elif not k.spread(new_elem):
                #print("false")
                continue

            traversed += 1
            if repr(k) in scanned:
                # print("Already scanned?", repr(k))
                # print(list(scanned))
                continue
            else:
                scanned.add(repr(k))

            '''if star_normal_form(k):
                print(repr(k), "star_normal_form")
                continue'''

            if (type(new_elem) == type(KleenStar()) or type(new_elem) == type(Question())) and k.kok():
                #print(repr(k), "is kok")
                continue

            if type(new_elem)==type(Character('0')) and is_pdead(k, examples):
                #print(repr(k), "is pdead")
                continue

            if (type(new_elem)==type(Character('0')) or type(new_elem)==type(KleenStar()) or type(new_elem)==type(Question())) and is_ndead(k, examples):
                #print(repr(k), "is ndead")
                continue


            if type(new_elem)==type(Character('0')):
                if is_overlap(k):
                    #print(repr(k), "is overlap")
                    continue

                if is_orinclusive(k):
                    #print(repr(k), "is orinclusive")
                    continue

                if is_equivalent_K(k):
                    #print(repr(k), "is equivalent_KO")
                    continue

                if is_kinclusive(k):
                    #print(repr(k), "is kinclusive")
                    continue

                if k.equivalent_concat():
                    #print(repr(k), "is equivalent_concat")
                    continue

                if k.equivalent_QCK():
                    #print(repr(k), "is equivalent_QCK")
                    continue

                if is_new_redundant2(k, examples):
                    #print(repr(k), "is redundant")
                    continue



            #print(k)
            if not k.hasHole():
                if is_solution(repr(k), examples, membership):
                    end = time.time()
                    print("Spent computation time:", end-start)
                    print("Iteration:", i, "\tCost:", cost, "\tScanned REs:", len(scanned), "\tQueue Size:", w.qsize(), "\tTraversed:", traversed)
                    # print("Result RE:", repr(k), "Verified by FAdo:", is_solution(repr(k), examples, membership2))
                    print("Result RE:", repr(k))
                    finished = True
                    break

            w.put((k.cost, k))



    if i % 1000 == 0:
        print("Iteration:", i, "\tCost:", cost, "\tScanned REs:", len(scanned), "\tQueue Size:", w.qsize(), "\tTraversed:", traversed)
    i = i+1

print("--end--")
print("count = ")
print(i)
print("answer = " + answer)





