import hashlib
def md5(str):
    md5 = hashlib.md5()
    md5.update(str.encode(encoding='utf-8'))
    return md5.hexdigest()