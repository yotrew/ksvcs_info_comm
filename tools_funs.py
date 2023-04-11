def encrypt(data):
    out_str=[]
    for i in data:
        out_str.append(str(hex((ord(i)+13)%255)).replace("0x",""))
    return ("".join(out_str))

def decrypt(data):
    out_str=[]
    for i in range(0,len(data),2):
        out_str.append(chr((int(data[i:i+2],16)-13)%255))
    return "".join(out_str)
