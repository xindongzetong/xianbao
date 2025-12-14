import sqlite3


class SqlAct:
    def __init__(self, db_name='xian_bao.db'):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def close_con(self):
        self.cur.close()
        self.conn.close()

    def create_tabel(self, sql):
        try:
            self.cur.executescript(sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("[CREATE TABLE ERROR]", e)
            return False

    def fetch_sql(self, sql, limit_flag=True):
        """
        :param sql:
        :param limit_flag: 查询条数选择，False 查询一条，True 全部查询
        :return:
        """
        try:
            self.cur.execute(sql)
            if limit_flag is True:
                r = self.cur.fetchall()
                return r
            elif limit_flag is False:
                r = self.cur.fetchone()
                return r
        except Exception as e:
            print("[SELECT TABLE ERROR]", e)
            return False

    def delete_table(self, sql):
        """
        :param sql:
        :return: True or False
        """
        try:
            if 'DELETE' in sql.upper():
                self.cur.execute(sql)
                self.conn.commit()
                return True
        except Exception as e:
            print("[DELETE TABLE ERROR]", e)
            return False

    def insert_update_table(self, sql):
        """
        :param sql:
        :return:
        """
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            print("[INSERT/UPDATE TABLE ERROR]", e)
            return False
