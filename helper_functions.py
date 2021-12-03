def salt_password(password):
    #every 2 chars insert a "bingbong"
    iterations = 0
    password_array = []
    for char in password:
        iterations += 1
        password_array.append(char)
        if iterations % 2 ==0:
            password_array.append('bingbong')

    return ''.join(password_array)

