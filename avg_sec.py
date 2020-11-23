#!/usr/bin/python

total = 0
fp = open('time_result.txt', "r")
lines = fp.readlines()
fp.close()

for i in range(len(lines)):
    print(float(lines[i]))
    total += float(lines[i])
print("avg sec:", total/len(lines))

