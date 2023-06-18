from random import randrange

salt = 3901


# Url Shortener
def id2url(num):
    """convert the integer to a character string that is at most 6 characters long"""
    character_map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_url = ""
    num = num + salt
    # for each digit find the base 62
    while num > 0:
        short_url += character_map[num % 62]
        num //= 62

    # reversing the shortURL
    return short_url[len(short_url):: -1]


def url2id(short_url):
    """convert character string to integer"""
    num = 0
    for i in short_url:
        val_i = ord(i)
        if ord('a') <= val_i <= ord('z'):
            num = num * 62 + val_i - ord('a')
        elif ord('A') <= val_i <= ord('Z'):
            num = num * 62 + val_i - ord('A') + 26
        else:
            num = num * 62 + val_i - ord('0') + 52
    num = num - salt
    return num
