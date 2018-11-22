import hashlib

password = '123'
# md5=hashlib.md5(password.encode('utf-8')).hexdigest()
# print(md5)

hl = hashlib.md5()
hl.update(password.encode('utf-8'))
print(password)
sign = hl.hexdigest()
print(sign)



