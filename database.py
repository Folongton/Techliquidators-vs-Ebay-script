import sqlite3


class Database:
    def __init__(self, name=None):
        self.conn = None
        self.cursor = None
        if name:
            self.open(name)

    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'create table if not exists items (id int  not null constraint items_pk primary key, added date not null);')
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error connecting to database!")
        finally:
            self.delete_trash()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def get(self, table, columns, limit=None):
        query = f"SELECT {columns} from {table};"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[len(rows) - limit if limit else 0:]

    def insert_many(self, table, items):
        if items:
            items = [f'({item},  date("now"))' for item in items]
            query = "INSERT INTO {0} (ID, ADDED) VALUES {1}".format(table, ','.join(items))
            # query = "INSERT INTO " + table + " (ID, ADDED) VALUES "
            self.cursor.execute(query)
            self.conn.commit()

    def query(self, sql):
        self.cursor.execute(sql)

    def delete_trash(self):
        self.cursor.execute('DELETE FROM items WHERE added < date("now","-30 day")')
