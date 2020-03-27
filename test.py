a=1
def b():
    global a
    try:
        raise Exception()
    except :
        a=2
        return
b()
print(a)