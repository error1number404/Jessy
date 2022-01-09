def check(author):
    def inner_check(message):
        if message.author != author:
            return False
        return True

    return inner_check
