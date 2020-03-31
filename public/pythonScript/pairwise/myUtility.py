def returnParameters(str):
    parameters = []

    for word in str.split():
        if (word.startswith("$")):
            parameters.append(word[2:-1])

    return parameters

def isValidCombo(row):
    n = len(row)
    if n > 1:
        if "qwe" == row[1] and "abc" == row[0]:
            return False
    return True
