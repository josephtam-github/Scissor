import re
import urllib


def validate_url(url: str):
    # Gotten from https://stackoverflow.com/a/55827638/15600487
    # Check https://regex101.com/r/A326u1/5 for reference
    DOMAIN_FORMAT = re.compile(
        r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
        r"(?:(?:(?=\S{0,253}(?:$|:))"  # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
        r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
        r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
        r"|localhost)"  # accept also "localhost" only
        r"(:\d{1,5})?",  # port [optional]
        re.IGNORECASE
    )
    SCHEME_FORMAT = re.compile(
        r"^(http|hxxp|ftp|fxp)s?$",  # scheme: http(s) or ftp(s)
        re.IGNORECASE
    )

    url = url.strip()

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not url:
        raise Exception("No URL specified")
    elif len(url) > 2048:
        raise Exception("URL exceeds its maximum length of 2048 characters (given length={})".format(len(url)))
    elif not scheme:
        raise Exception("No URL scheme specified")
    elif not re.fullmatch(SCHEME_FORMAT, scheme):
        raise Exception("URL scheme must either be http(s) or ftp(s) (given scheme={})".format(scheme))
    elif not domain:
        raise Exception("No URL domain specified")
    elif not re.fullmatch(DOMAIN_FORMAT, domain):
        raise Exception("URL domain malformed (domain={})".format(domain))

    return url


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
