import sqlite3


class Database:
    def __init__(self, name=None):  #__init__  method (CONSTRUCTOR) requires defined variables when creating new instance(object) out of this class.  https://www.youtube.com/watch?v=KzZhAqu3s4M
        self.conn = None           # https://stackoverflow.com/questions/8985806/python-constructors-and-init
        self.cursor = None         # None is null in Python. Why name=None ??? --> https://graysonkoonce.com/always-use-none-for-default-args-in-python/
        if name:                   # So, if there is no name was given here -> **db = Database('techliquidators.sqlite')**, then it would do nothing ?
            self.open(name)


    def open(self, name):                          # try/except/finally block see: https://docs.python.org/2.5/whatsnew/pep-341.html
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'create table if not exists items (id int  not null constraint items_pk primary key, added date not null);')
            self.conn.commit()
        except sqlite3.Error as e:                 #variable 'e' was not used
            print("Error connecting to database!")
            print("Database error: %s" % e)        # I added this line
        finally:
            self.delete_trash()

    def close(self):
        if self.conn:              #  Do we need 'if' statement. We can do 3 lines after and that's all, doesn't we ?
            self.conn.commit()     # this line is not necessary ? or we need it in case ?
            self.cursor.close()
            self.conn.close()

    def get(self, table, columns, limit=None):
        query = f"SELECT {columns} from {table};"        # formatted string literals -> https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python
        self.cursor.execute(query)
        rows = self.cursor.fetchall()                    # Takes all rows (auction numbers) which are already ni DB
        return rows[len(rows) - limit if limit else 0:]  # why do we need limit ?

    def insert_many(self, table, items):
        if items:                                                        # for all items
            items = [f'({item},  date("now"))' for item in items]        # (New python 3.6 formating f') Adds NOW date to all Auction numbers
            query = "INSERT INTO {0} (ID, ADDED) VALUES {1}".format(table, ','.join(items))  # Older formating
            # query = "INSERT INTO " + table + " (ID, ADDED) VALUES "
            self.cursor.execute(query)
            self.conn.commit()

    def query(self, sql):
        self.cursor.execute(sql)

    def delete_trash(self):
        self.cursor.execute('DELETE FROM items WHERE added < date("now","-7 day")')
