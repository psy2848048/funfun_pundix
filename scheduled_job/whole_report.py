import traceback
import sys

from dbConn import DBActions


class BalanceReport(object):
    def __init__(self):
        self.connObj = DBActions()

    def getBalance(self):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        query = """
            SELECT
                sub.user_id as user_id
              , sum(sub.income) as income
              , sum(sub.withdraw) as withdraw
              , ( sum(sub.income) + sum(sub.withdraw) ) as balance
            FROM 
            (
                SELECT
                    user_id
                  , CASE
                      WHEN pundix_share >= 0 THEN pundix_share ELSE 0 END AS income
                  , CASE
                      WHEN pundix_share < 0 THEN pundix_share ELSE 0 END AS withdraw
                FROM pundix_users
            ) sub
            GROUP BY user_id
            ORDER BY sub.user_id ASC
        """
        cursor.execute(query)
        ret = cursor.fetchall()
        self.connObj.closeConnection(conn)

        return ret

    def printMarkdown(self, ret):
        print("|     ID     |    적립 NPXS     |     인출 NPXS     |    잔고 NPXS     |")
        print("|------------|------------------|-------------------|------------------|")

        for item in ret:
            print("|   @{}    |     {}     |    {}     |     {}      |".format(item['user_id'], item['income'], abs(item['withdraw']), item['balance']))


if __name__ == "__main__":
    pundix = BalanceReport()
    ret = pundix.getBalance()
    pundix.printMarkdown(ret)

