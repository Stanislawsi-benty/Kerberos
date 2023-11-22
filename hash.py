import bcrypt


def to_hash(password):
    salt = b'$2b$12$Tm2WtS851uQ.oU..kY2Eb.'

    password_en = password.encode('utf-8')

    hashed_password = bcrypt.hashpw(password_en, salt)

    return hashed_password.decode('utf-8')
