from allpairspy import AllPairs
import numpy as np
print ("Pairwise testing")


parameters = [
    ["high","medium","low"],
    ["high","medium","low"],
    ["vip","regular","everyone"],
    ["checking", "non-checking"],
    ["10yrs", "20yrs", "30yrs"],
    ["large","medium","small"],
    ["70%", "80%", "90%"],
    ["no", "verification"],
    ["apartment","condo","house"],
    ["flm","flnm","il","nc"],
    ["investment","primary","rental"]
]

print len(parameters)
print (parameters[0][0])
"""
tested = [
    ["Brand X", "98", "Modem", "Hourly", 10],
    ["Brand X", "98", "Modem", "Hourly", 15],
    ["Brand Y", "NT", "Internal", "Part-Time", 10],
]
"""


tested = []

p0 = list()

a = int(input("Enter parameters to consider at once "))
print("PAIRWISE:")
for i, pairs in enumerate(AllPairs(parameters, previously_tested=tested, n=a)):
    print("{:2d}: {}".format(i, pairs))
    #p0.append(pairs[0])


#a = np.array(set(p0))