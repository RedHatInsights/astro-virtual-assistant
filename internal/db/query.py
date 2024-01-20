import internal.db as db


class Query:
    query = ""

    def select(self, columns):
        self.query = "SELECT {}".format(columns)
        return self

    def from_table(self, table_name):
        self.query += " FROM {}".format(table_name)
        return self

    def where(self, conditions):
        if len(conditions) == 0:
            return self
        conditions_string = " WHERE"
        for condition in conditions:
            conditions_string += condition.to_string()
        self.query += conditions_string
        return self

    def limit(self, limit):
        self.query += " LIMIT {}".format(limit)
        return self

    def offset(self, offset):
        self.query += " OFFSET {}".format(offset)
        return self

    def order_by(self, order_by):
        self.query += " ORDER BY {}".format(order_by)
        return self

    def execute(self):
        with db.db_cursor() as cur:
            cur.execute(self.query)
            rows = cur.fetchall()
        return rows
