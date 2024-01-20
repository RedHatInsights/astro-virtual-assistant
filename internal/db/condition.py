class Condition:
    column = ""
    relation = ""
    value = ""

    def __init__(self, column, relation, value):
        self.column = column
        self.relation = relation
        self.value = value

    def to_string(self):
        if self.relation.upper() == 'BETWEEN':
            if isinstance(self.value, (list)) and len(self.value) == 2:
                return " {} BETWEEN {} AND {}".format(self.column, self.value[0], self.value[1])
            else:
                raise ValueError("Between condition must be a list of 2 values")
        return " {} {} '{}'".format(self.column, self.relation, self.value)


class Operator:
    operator = ""

    def __init__(self, operator):
        self.operator = operator

    def to_string(self):
        return " {}".format(self.operator)
