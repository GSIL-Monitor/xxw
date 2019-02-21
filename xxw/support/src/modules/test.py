
filename ='./task.py'
file = open(filename,'r').readlines()
for _ in file:
    if _.startswith("class"):
        print(_.split(" ")[-1].split("(")[0])

filename.