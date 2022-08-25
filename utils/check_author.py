def check(author):
    def inner_check(message):
        return message.author == author

    return inner_check
