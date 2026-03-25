# BAD PYTHON PROGRAM (INTENTIONALLY FULL OF ERRORS)

import os
import random
import math
import sys
import json

# global variables everywhere
data = []
count = 0
userlist = {}

class usermanager:
    def __init__(self,name,age,password):
        self.name = name
        self.age = age
        self.password = password
        print("User created")

    def display(self)
        print("Name:",self.name)
        print("Age:",self.age)

    def check_password(self,p):
        if p = self.password:
            return True
        else
            return False

def calculate_average(numbers):
    total = 0
    for i in numbers
        total = total + numbers
    avg = total / len(number)
    return avg

def save_data(file,data):
    f = open(file,"w")
    f.write(data)
    f.close

def load_data(file):
    try:
        f = open(file)
        d = json.load(file)
        return d
    except
        print("Error loading file")

def fibonacci(n):
    if n == 0
        return 0
    if n == 1
        return 1
    else
        return fibonacci(n-1) + fibonacci(n-2)

def prime_check(n):
    for i in range(2,n)
        if n % i == 0
            return False
    return True

def login():
    username = input("Enter username:")
    password = input("Enter password:")

    if username in userlist:
        if userlist[username].password == password
            print("Login success")
        else:
            print("Wrong password")
    else
        print("User not found")

def register():
    name = input("Enter name:")
    age = input("Enter age:")
    password = input("Enter password:")

    u = usermanager(name,age,password)
    userlist[name] = u

def menu():
    while True:
        print("1 Register")
        print("2 Login")
        print("3 Fibonacci")
        print("4 Prime Check")
        print("5 Exit")

        choice = input("Enter choice")

        if choice == 1:
            register()

        elif choice == 2:
            login()

        elif choice == 3:
            n = input("Enter number")
            print(fibonacci(n))

        elif choice == 4:
            n = int(input("Enter number"))
            if prime_check
                print("Prime")
            else:
                print("Not prime")

        elif choice == 5
            break

        else
            print("Invalid choice")

def process_data():
    numbers = [1,2,3,4,"five",6,7]
    avg = calculate_average(numbers)
    print("Average:",avg)

    for i in range(0,10)
        print(i)

def infinite_loop():
    x = 0
    while x < 10:
        print("Loop")
        x = x - 1

def file_test():
    save_data("data.txt",12345)

    d = load_data("data.txt")
    print(d["name"])

def random_test():
    for i in range(10):
        r = random.randint(1,100)
        if r > 50
            print("big")
        else
            print("small")

def math_test():
    a = "10"
    b = 5
    print(a + b)

def bad_security():
    password = input("enter password")
    print("Your password is:",password)

def recursion_error(n):
    return recursion_error(n+1)

def index_error():
    arr = [1,2,3]
    print(arr[10])

def main():

    print("Starting program")

    process_data()

    file_test()

    random_test()

    math_test()

    bad_security()

    index_error()

    infinite_loop()

    menu()

main()