# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# modules/base58.py - Base58 인코딩/디코딩을 담당하는 스크립트입니다.
#
# ianoxley님의 base58.py 스크립트를 바탕으로 부동소숫점 정확도를 향상시킨 스크립트입니다.
# 참고: https://gist.github.com/ianoxley/865912/e10cb707cda6aac9e9a6b61d846381300e91498c

from decimal import Decimal

alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
base_count = len(alphabet)


def encode(num):
    """ Returns num in a base58-encoded string """
    encoded = ''

    if num < 0:
        return ''

    while num >= base_count:
        mod = num % base_count
        encoded = alphabet[int(mod)] + encoded
        num = Decimal(num) / base_count

    if num:
        encoded = alphabet[int(num)] + encoded

    return encoded


def decode(s):
    """ Decodes the base58-encoded string s into an integer """
    decoded = 0
    multi = 1
    s = s[::-1]
    for char in s:
        decoded += multi * alphabet.index(char)
        multi = multi * base_count
    return decoded
