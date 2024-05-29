from z3 import *

def printer(model):
    dict = {}
    dict["pc_1"] = ['x=10', '1']
    dict["pc_2"] = ['y=x', '2']
    dict["pc_3"] = ['clflushopt(&y)', '2']
    dict["pc_4"] = ['sfence()', '2']
    dict["pc_5"] = ['clflush(&x)', '2']
    dict["pc_6"] = ['Lock(&a)', '1']
    dict["pc_7"] = ['UNLock(&a)', '1']
    dict["pc_8"] = ['Lock(&a)', '2']
    dict["pc_9"] = ['UNLock(&a)', '2']
    for i in range(1, 10):
        for m in model:
            if str(i) in str(model[m]) and not "pt" in str(m):
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

solver.add(Int("pc_1")<Int("pc_2"))
pc = []

for i in range(1, 10):
    pc.append(Int("pc_"+str(i))<10)
    pc.append(Int("pc_"+str(i))>0)

for i in range(1, 10):
    for j in range(i+1, 10):
        pc.append(Int("pc_"+str(i))!=Int("pc_"+str(j)))
pc.append(Int("pc_4")>Int("pc_3"))

persist = []
# persist.append(Int("pc_3")>Int("pc_2"))
# persist.append(Int("pc_5")>Int("pc_1"))

lock = []
lock.append(Or(Int("pc_6")>Int("pc_9"), Int("pc_6")<Int("pc_8")))
lock.append(Or(Int("pc_8")>Int("pc_7"), Int("pc_8")<Int("pc_6")))
lock.append(And(Int("pc_7")>Int("pc_6"), Int("pc_9")>Int("pc_8")))

pt = []
pt.append(Int("pt_1")<=Int("pc_5"))
pt.append(Int("pt_1")>=Int("pc_1"))
pt.append(Int("pt_2")<=Int("pc_4"))
pt.append(Int("pt_2")>=Int("pc_2"))

bug = []
bug.append(Int("pt_1")<Int("pt_2"))

solver.add(pc)
solver.add(persist)
solver.add(lock)
solver.add(pt)
solver.add(Not(And(bug)))

print("Initial configuration:")
model = ''
if solver.check()==sat:
    model = solver.model()
    printer(model)
    print()


i = 1
sais = []
while solver.check()==sat:
    print("After blocking constraint ", i, ":")
    i += 1
    sai = []
    sai.append(constructConstraint(6, 8, model))
    sai.append(constructConstraint(1, 3, model))
    sai.append(constructConstraint(1, 4, model))
    sai.append(constructConstraint(2, 5, model))
    # sai.append(constructConstraint(1, 6, model))
    # sai.append(constructConstraint(2, 8, model))
    # sai.append(constructConstraint(1, 8, model))
    # sai.append(constructConstraint(2, 6, model))
    # sai.append(constructConstraint(3, 5, model))
    # sai.append(constructConstraint(4, 5, model))
    solver.add(Not(And(sai)))
    sais.append(Not(And(sai)))

    if solver.check()==sat:
        model = solver.model()
        # print(model)
        printer(model)
        print()
        


# print(sais)

s = Solver()
s.add(Int("pc_1")<Int("pc_2"))
s.add(pc)
s.add(persist)
s.add(lock)
s.add(pt)
s.add(Not(And(bug)))
s.add(And(sais)) #CHECK HOW THIS CLAUSE SHOULD BE FORMED.
# print(s)
if s.check()==sat: 
    print("\nRepaired program:")
    printer(s.model())
    print(s.model())
else:
    print("UNSAT")

