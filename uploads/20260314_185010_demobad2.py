import os
import sys
import math
import random
import datetime
import json
import time
import sqlite3

# global variables
x = 0
y = []
z = {}

print("Welcome to student system")

name=input("Enter name")
age=input("Enter age")
marks=input("Enter marks")

age=int(age)
marks=int(marks)

if marks>90:
 print("Grade A")
elif marks>70:
 print("Grade B")
elif marks>50:
 print("Grade C")
else:
 print("Fail")

# bad loop logic
for i in range(0,10):
 print(i)
 if i==5:
  print("halfway")
 else:
  pass

# unused variable
temp = 100

# random calculation
a=10
b=20
c=a+b
d=a*b
e=a/b
f=a-b

print("sum",c)
print("mul",d)
print("div",e)
print("sub",f)

# inefficient prime checker
n=int(input("Enter number to check prime"))
flag=0
for i in range(2,n):
 if n%i==0:
  flag=1
 if flag==1:
  break

if flag==0:
 print("Prime")
else:
 print("Not Prime")

# bad list handling
list=[1,2,3,4,5]
for i in range(len(list)):
 print(list[i])

list.append(10)
list.append(20)
list.append(30)

print(list)

# dictionary misuse
student={}
student["name"]=name
student["age"]=age
student["marks"]=marks

print(student)

# useless nested loops
for i in range(5):
 for j in range(5):
  for k in range(3):
   print(i,j,k)

# file writing without closing properly
file=open("data.txt","w")
file.write("Student name:"+name)
file.write("\nAge:"+str(age))
file.write("\nMarks:"+str(marks))

# no file.close()

# bad exception handling
try:
 num=int(input("enter number"))
 result=100/num
 print(result)
except:
 print("error happened")

# unnecessary sleep
time.sleep(1)

# database connection but not used properly
conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER,name TEXT)")
cursor.execute("INSERT INTO users VALUES(1,'admin')")

# not committing properly
# conn.commit()

# messy logic
numbers=[5,3,7,2,8,1]

largest=0
for i in numbers:
 if i>largest:
  largest=i

print("largest number is",largest)

# random useless operations
for i in range(100):
 x=x+1
 y.append(i)
 z[i]=i*i

print(x)
print(len(y))
print(len(z))

# repeated code
print("Program finished")
print("Program finished")
print("Program finished")
print("Program finished")
print("Program finished")