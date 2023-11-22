from enryption.alphabet import alphabet_a, alphabet_key


def key_digit(key):
    pre_key = []

    for i, letter in enumerate(key):
        for j, letter_al in enumerate(alphabet_a):
            if letter == letter_al:
                pre_key.append(j)
                break

    return pre_key


def encrypt(message, key):
    en_message = ''
    c = 0

    digit_key = key_digit(key[-7:-1])
    len_key = len(digit_key)

    for i, letter_m in enumerate(message):
        for j, letter_a in enumerate(alphabet_a):
            if letter_m == letter_a:
                en_message += alphabet_key[digit_key[c]][j]
                c += 1
                if c >= len_key:
                    c = 0
                break

    return en_message


def decrypt(en_message, key):
    standard_message = ''
    c = 0

    digit_key = key_digit(key[-7:-1])
    len_key = len(digit_key)

    for i, letter_em in enumerate(en_message):
        for j, letter_ak in enumerate(alphabet_key[digit_key[c]]):
            if letter_em == letter_ak:
                standard_message += alphabet_a[j]
                break
        c += 1
        if c >= len_key:
            c = 0

    return standard_message
