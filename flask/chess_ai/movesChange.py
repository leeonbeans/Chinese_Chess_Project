
s = "b2b9"
#先横再竖
def movesToDP(s:str):
    res = ''
    a = {'a':'0','b':'1','c':'2','d':'3','e':'4','f':'5','g':'6','h':'7','i':'8'}
    b = {'0': '9', '1': '8', '2': '7', '3': '6', '4': '5', '5': '4', '6': '3', '7': '2', '8': '1', '9': '0'}
    res = res + a[s[0]]
    res = res + b[s[1]]
    res = res + a[s[2]]
    res = res + b[s[3]]
    return res


def movesToFen(s:str):
    res = ''
    a = {'0': 'a', '1': 'b', '2': 'c', '3': 'd', '4': 'e', '5': 'f', '6': 'g', '7': 'h', '8': 'i'}
    b = {'0': '9', '1': '8', '2': '7', '3': '6', '4': '5', '5': '4', '6': '3', '7': '2', '8': '1', '9': '0'}

    res = res + a[s[0]]
    res = res + b[s[1]]
    res = res + a[s[2]]
    res = res + b[s[3]]
    return res

# print(movesToDP(s))
# print(movesToFen(movesToDP(s)))