import traceback

from dbConn import DBActions


class PurchasePundix(object):
    def __init__(self):
        self.connObj = DBActions()

    def _checkPurchasePermlinks(self):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        query = """
            SELECT permlink, payout_sbd
            FROM posting
            WHERE is_invested = false
        """
        cursor.execute(query)
        ret = cursor.fetchall()

        total_sbd = 0
        result_permlinks = []
        for item in ret:
            total_sbd += item['payout_sbd']
            result_permlinks.append(item['permlink'])

        print("Total: {}".format(total_sbd))
        print(result_permlinks)

        return total_sbd, result_permlinks

    def _checkContributionRate(self, total_sbd, permlinks, amount):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        print(permlinks)
        string_permlinks = [ "'{}'".format(item) for item in permlinks ]

        query = """
            SELECT user_id, sum(sbd_contribution) as running_contribution
            FROM voted_users
            WHERE permlink IN ({})
            GROUP BY user_id
        """.format(', '.join(string_permlinks))
        cursor.execute(query)
        ret = cursor.fetchall()

        users_list = []
        whole_users = len(ret)
        for item in ret:
            item['rate'] = item['running_contribution'] / total_sbd
            item['share_by_contribution'] = item['rate'] * (amount * 0.8)
            item['share_by_participation'] = (amount * 0.2) / whole_users
            item['sum'] = item['share_by_contribution'] + item['share_by_participation']
            users_list.append(item)
            print(item)

        self.connObj.closeConnection(conn)
        return users_list

    def _checkInterestAmount(self, amount):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        query_whole = """
            SELECT sum(pundix_share) as whole_amount
            FROM pundix_users
        """
        cursor.execute(query_whole)
        current_whole_amount = cursor.fetchone()['whole_amount']

        query_individual = """
            SELECT user_id, sum(pundix_share) as individual_sum
            FROM pundix_users
            GROUP BY user_id
        """
        cursor.execute(query_individual)
        ret = cursor.fetchall()
        result = []

        for item in ret:
            item['sum'] = item['individual_sum'] / current_whole_amount * amount
            result.append(item)

        return result

    def _dbInput(self, purchase_type, permlinks, total_sbd, amount, users_list):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        try:
            if purchase_type == "purchase":
                string_permlinks = [ "'{}'".format(item) for item in permlinks ]
                query_invested_update = """
                    UPDATE posting
                      SET is_invested = true
                    WHERE permlink IN ({})
                """.format(', '.join(string_permlinks))
                cursor.execute(query_invested_update)

            query_pundix_purchase = """
                INSERT INTO purchase_pundix
                  (type, invested_sbd, purchase_pundix, executed_at)
                VALUES
                  (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query_pundix_purchase, (purchase_type, total_sbd, amount, ))

            query_get_purchase_id = """
                SELECT id
                FROM purchase_pundix
                ORDER BY executed_at DESC LIMIT 1
            """
            cursor.execute(query_get_purchase_id)
            purchase_id = cursor.fetchone()['id']

            query_permlink_record = """
                INSERT INTO purchase_permlink
                  (purchase_id, permlinks)
                VALUES
                  (%s, %s)
            """
            # 이자수입 입력의 경우 자동으로 건너뛰어질 것이다.
            for link in permlinks:
                cursor.execute(query_permlink_record, (purchase_id, link, ))

            query_user_distribution = """
                INSERT INTO pundix_users
                  (purchase_id, user_id, type, share_by_contribution, share_by_participation, pundix_share, executed_at)
                VALUES
                  (%s,          %s,      %s,   %s,                    %s,                     %s,           CURRENT_TIMESTAMP)
            """
            for item in users_list:
                cursor.execute(query_user_distribution, (
                      purchase_id
                    , item['user_id']
                    , purchase_type
                    , item.get('share_by_contribution')
                    , item.get('share_by_participation')
                    , item['sum']
                    , ))

        except:
            conn.rollback()
            traceback.print_exc()

        finally:
            conn.commit()
            self.connObj.closeConnection(conn)

    def report(self, user_list):
        print("|     ID     |    SBD 기여비율     |     배당 PundiX     |")
        print("|------------|---------------------|---------------------|")

        for item in user_list:
            print("|   {}    |     {}     |    {}     |".format(item['user_id'], "{0:.2f}%".format(item['rate'] * 100), item['sum']))

    def input(self, purchase_type, amount):
        if purchase_type == "purchase":
            total_sbd, result_permlinks = self._checkPurchasePermlinks()
            user_list = self._checkContributionRate(total_sbd, result_permlinks, amount)
            self._dbInput(purchase_type, result_permlinks, total_sbd, amount, user_list)

        elif purchase_type == "interest":
            user_list = self._checkInterestAmount(amount)
            self._dbInput(purchase_type, [], 0, amount, user_list)

        self.report(user_list)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Note')
    parser.add_argument('--type', type=str, choices=("purchase", "interest"), help='Type of purchasement')
    parser.add_argument('--amount', type=float, help='Purchase amount')

    args = parser.parse_args()

    purchase_type = args.type
    amount = float(args.amount)

    pundix = PurchasePundix()
    pundix.input(purchase_type, amount)

