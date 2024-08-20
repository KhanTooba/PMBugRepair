from z3 import *
"""
V1:
This file takes in the output generated after steps 1 and 2 and process it for step 3 i.e lock insertion. 
It produces the final repaired program.
Output in ../outputFiles/locksBasedEncoding.txt

V2:
Modified version of insertingLocks.py
What are the modifications?
The bug encoding works on elimnating faulty encodings instead of enforcing locks. 
Thus, the encoding can automatically figure out the need of a lock.
Output in ../outputFile/interleaveBasedOutput.txt
"""
last = 10
threads = 2
"""
To restrict: The interleaving of statements of two threads--> insert locks automatically there.
"""
def printer(model):
    dict = {}
    dict["pc_1"] = ['x=10', '1']
    dict["pc_2"] = ['clflush(&x)', '1']
    dict["pc_3"] = ['y=x', '2']
    dict["pc_4"] = ['clflushopt(&y)', '2']
    dict["pc_5"] = ['sfence()', '2']
    dict["pc_6"] = ['Lock(&a)', '1']
    dict["pc_7"] = ['UNLock(&a)', '1']
    dict["pc_8"] = ['Lock(&a)', '2']
    dict["pc_9"] = ['UNLock(&a)', '2']
    for i in range(1, last):
        for m in model:
            # print(m)
            if str(i) in str(model[m]) and not "pt" in str(m) and not "interleave" in str(m):
                print(i, dict[str(m)])


def constructConstraint(i, j, s):
    a, b = 0, 0
    for s_i in s:
        if "pc_"+str(i) in str(s_i):
            # print(s_i, s[s_i])
            a = int(str(s[s_i]))
        if "pc_"+str(j) in str(s_i):
            # print(s_i, s[s_i])
            b = int(str(s[s_i]))
    
    if a<b:
        return Int("pc_"+str(i))<Int("pc_"+str(j))
    else:
        return Int("pc_"+str(i))>Int("pc_"+str(j))

solver = Solver()

pc = []

for i in range(1, last):
    pc.append(Int("pc_"+str(i))<last)
    pc.append(Int("pc_"+str(i))>0)
    pc.append(Int("interleave_"+str(i))<last)
    pc.append(Int("interleave_"+str(i))>0)

for i in range(1, last):
    for j in range(i+1, last):
        pc.append(Int("pc_"+str(i))!=Int("pc_"+str(j)))
        pc.append(Int("interleave_"+str(i))!=Int("interleave_"+str(j)))
# pc.append(Int("pc_4")>Int("pc_3"))
pc.append(Int("pc_1")<Int("pc_3"))
persist = []
# persist.append(Int("pc_3")>Int("pc_2"))
# persist.append(Int("pc_5")>Int("pc_1"))

sequen = []
sequen.append(Int("pc_1")<Int("pc_2"))
sequen.append(Int("pc_3")<Int("pc_4"))
sequen.append(Int("pc_4")<Int("pc_5"))


lock = []
lock.append(Or(Int("pc_6")>Int("pc_9"), Int("pc_6")<Int("pc_8")))
lock.append(Or(Int("pc_8")>Int("pc_7"), Int("pc_8")<Int("pc_6")))
lock.append(And(Int("pc_7")>Int("pc_6"), Int("pc_9")>Int("pc_8")))

pt = []
# pt.append(Int("pt_1")<=Int("pc_2"))
# pt.append(Int("pt_1")>=Int("pc_1"))
# pt.append(Int("pt_2")<=Int("pc_5"))
# pt.append(Int("pt_2")>=Int("pc_3"))

bug = []
"""
Bugs should say that either read on x is not atomic or write on x is not atomic. 
Give me all traces where either is not atomic.
Either 1, 2 should execute before 3, 4, 5 or entirely after that.
Define a symbolic variable called "interleave". 
Interleave can have values that are possible for statements.
Find the configuration in which interleave is not possible.
Which interleavings are erroneous?
1-3-4-5-2
1-3-2-4-5
1-3-4-2-5
"""

bug.append(Or(Int("interleave_1")<Int("pc_8"),Int("interleave_1")>Int("pc_9")))
bug.append(Or(Int("interleave_2")<Int("pc_8"),Int("interleave_2")>Int("pc_9")))
bug.append(Or(Int("interleave_3")<Int("pc_6"),Int("interleave_3")>Int("pc_7")))
bug.append(Or(Int("interleave_4")<Int("pc_6"),Int("interleave_4")>Int("pc_7")))
bug.append(Or(Int("interleave_5")<Int("pc_6"),Int("interleave_5")>Int("pc_7")))

# bug.append(Or(
#             And(Int("interleave_1")<Int("interleave_3"), Int("interleave_3")<Int("interleave_4"), 
#                   Int("interleave_4")<Int("interleave_2"), Int("interleave_2")<Int("interleave_5")),
#             And(Int("interleave_1")<Int("interleave_3"), Int("interleave_3")<Int("interleave_4"), 
#                   Int("interleave_4")<Int("interleave_5"), Int("interleave_5")<Int("interleave_2")),
#             And(Int("interleave_1")<Int("interleave_3"), Int("interleave_3")<Int("interleave_2"), 
#                   Int("interleave_2")<Int("interleave_4"), Int("interleave_4")<Int("interleave_5"))))

# bug.append(Or(Int("pc_1")<Int("pc_8"),Int("pc_1")>Int("pc_9")))
# bug.append(Or(Int("pc_2")<Int("pc_8"),Int("pc_2")>Int("pc_9")))
# bug.append(Or(Int("pc_3")<Int("pc_6"),Int("pc_3")>Int("pc_7")))
# bug.append(Or(Int("pc_4")<Int("pc_6"),Int("pc_4")>Int("pc_7")))
# bug.append(Or(Int("pc_5")<Int("pc_6"),Int("pc_5")>Int("pc_7")))
bug.append(Int("interleave_1")>Int("interleave_3"))

for b in bug:
    print(b)

"""
What I want? That untill my shared variable is written/read and committed to PM, I shouldn't be able to release lock. 
Atomicity!
"""

# solver.add(Int("pc_1")<Int("pc_2"))
solver.add(pc)
solver.add(sequen)
solver.add(persist)
solver.add(lock)
solver.add(pt)
solver.add(And(bug))
#

# for a in solver.assertions():
#     print("("+str(a)+") \land ", end="")
# print(solver.assertions())
print()
print("Initial configuration:")
model = ''
if solver.check()==sat:
    model = solver.model()
    printer(model)
    print()


s = Solver()
# s.add(Int("pc_1")<Int("pc_2"))
s.add(pc)
s.add(persist)
s.add(sequen)
s.add(lock)
s.add(pt)


i = 1
while solver.check()==sat:
    # print("After blocking constraint ", i, ":")
    # i += 1
    sai = []
    """
    Somehow explain to the solver via constraints that thread switching is not allowed in case of locks. 
    And that the scenario of [Store -> clflushopt-> Dependent Store] is UNSAFE.
    """
    sai.append(constructConstraint(1, 6, model))
    sai.append(constructConstraint(3, 8, model))
    sai.append(constructConstraint(2, 7, model))
    sai.append(constructConstraint(5, 9, model))

    print("Blocking constraint ", i, ":", sai)
    print("---------------------------------------------------------------------------------------------------------")
    i += 1
    solver.add(Not(And(sai)))
    s.add(Not(And(sai)))

    if solver.check()==sat:
        model = solver.model()
        print(model)
        printer(model)
        print()
        

# print(s.assertions())
r = 1
while s.check()==sat:
    print("\nRepaired program:", r)
    r += 1
    m = s.model()
    printer(m)
    print(m)
    cons = []
    for mi in m:
        if "pc" in str(mi):
            cons.append(Int(str(mi))!=m[mi]) 
    s.append(Or(cons))
