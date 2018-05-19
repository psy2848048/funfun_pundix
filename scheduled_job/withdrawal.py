import traceback
import sys

from dbConn import DBActions


class WithDraw(object):
    def __init__(self):
        self.connObj = DBActions()

    def withdraw(self, user, amount, fee, txid):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        query_checkBalance = """
            SELECT sum(pundix_share) as money
            FROM pundix_users
            WHERE user_id = %s
        """
        cursor.execute(query_checkBalance, (user, ))
        user_balance = cursor.fetchone()['money']

        if user_balance < (amount + fee):
            print("잔액부족 ㅜㅜ")
            print("잔고: {}".format(user_balance))
            print("신청금액: {}".format(amount+fee))
            sys.exit(1)

        try:
            query_central = """
                INSERT INTO purchase_pundix
                  (type, invested_sbd, purchase_pundix, executed_at)
                VALUES
                  ('withdraw', 0, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query_central, (-1 * (amount+fee), ))

            query_get_purchase_id = """
                SELECT id
                FROM purchase_pundix
                ORDER BY executed_at DESC LIMIT 1
            """
            cursor.execute(query_get_purchase_id)
            purchase_id = cursor.fetchone()['id']

            query_individual = """
                INSERT INTO pundix_users
                  (purchase_id, type, user_id, pundix_share, txid, executed_at)
                VALUES
                  (%s, 'withdraw', %s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query_individual, (purchase_id, user, -1*(amount+fee), txid, ))
            conn.commit()

            print("인출완료")
            print("잔고: {}".format(user_balance))
            print("신청금액: {}".format(amount+fee))
            print("인출후잔액: {}".format(user_balance - amount-fee))

        except:
            conn.rollback()
            traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Note')
    parser.add_argument('--user', type=str, help='User ID')
    parser.add_argument('--amount', type=float, help='Withdraw amount')
    parser.add_argument('--fee', type=float, help='Fee')
    parser.add_argument('--txid', type=str, help='Tx ID')

    args = parser.parse_args()

    user_id = args.user
    amount = float(args.amount)
    fee = float(args.fee)
    txid = args.txid

    pundix = WithDraw()
    pundix.withdraw(user_id, amount, fee, txid)

