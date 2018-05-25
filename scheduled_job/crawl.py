from decimal import Decimal
from datetime import datetime, timedelta
import sys
import traceback

from steem import Steem
from dbConn import DBActions

# 스팀잇에서 현황 긁어오는데 사용

class SteemPosting(object):
    def __init__(self):
        self.steem = Steem()
        self.account = "funfund"

        overview = self.steem.get_reward_fund("post")
        steem_prices = self.steem.get_current_median_history_price()

        self.reward_balance = Decimal(overview['reward_balance'].replace(' STEEM', ''))
        self.recent_claims = Decimal(overview['recent_claims'])
        self.feed_price = Decimal(steem_prices['base'].replace(' SBD', ''))

        print("Reward balance: {}".format(self.reward_balance))
        print("Recent claims: {}".format(self.recent_claims))
        print("Feed price: {}".format(self.feed_price))

        self.connObj = DBActions()

    def _calcContribution(self, post_data):
        voters = post_data['active_votes']
        total_payout_value = Decimal(post_data['total_payout_value'].replace(" SBD", "")) / 2

        voter_lists = []
        net_rshare = 0
        for unit in voters:
            net_rshare += Decimal(unit['rshares'])
            amount = self.reward_balance * self.feed_price * Decimal(unit['rshares']) / self.recent_claims
            voter = unit['voter']
            unit_amount = {'voter':voter, 'amount': amount}
            voter_lists.append(unit_amount)

        total_votes_in_dollar = self.reward_balance * self.feed_price * net_rshare / self.recent_claims

        for item in voter_lists:
            item['sbd_contribution'] = item['amount'] / total_votes_in_dollar * total_payout_value
            print(item)

        print("Total payout : {} SBD".format(total_payout_value))

        return {
                     "permlink": post_data['root_permlink']
                   , "total_sbd":total_payout_value
                   , "voters": voter_lists
                   , "created": post_data['created']
               }

    def getRecentPaidOutPostPermlinks(self):
        # 이미 보상 받은 포스팅 목록 가져요기

        ret = self.steem.get_blog(self.account, entry_id=0, limit=10)

        candidate_perlinks = []
        for unit_post in ret:
            created = datetime.strptime(unit_post['comment']['created'], '%Y-%m-%dT%H:%M:%S')
            print(created)
            if created + timedelta(days=7) < datetime.now():
                permlink = unit_post['comment']['root_permlink']
                candidate_perlinks.append(permlink)
                print(permlink)

        return candidate_perlinks

    def getValidPermlinks(self, permlinks):
        if len(permlinks) < 1:
            return []

        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        stringed_permlinks = [ "'{}'".format(item) for item in permlinks ]

        query = """
            SELECT permlink
            FROM posting
            WHERE permlink IN ({})
        """.format(','.join(stringed_permlinks))

        cursor.execute(query)
        ret = cursor.fetchall()

        if ret is None or len(ret) < 1:
            return permlinks

        valid_permlinks = []
        queryRes = [ item['permlink'] for item in ret ]
        for unit in permlinks:
            if unit not in queryRes:
                valid_permlinks.append(unit)

        self.connObj.closeConnection(conn)

        return valid_permlinks

    def getCalcDataFromPermlinks(self, permlinks):
        result = []
        for unit_link in permlinks:
            unit_data = self.steem.get_content(self.account, unit_link)
            result.append(self._calcContribution(unit_data))

        return result

    def insertPostRecord(self, postdata):
        conn = self.connObj.getConnection()
        cursor = conn.cursor()

        query_posting = """
            INSERT INTO posting
                (permlink, created, payout_sbd, is_invested)
            VALUES
                (%s, %s, %s, false)
        """

        query_userVote = """
            INSERT INTO voted_users
                (user_id, permlink, sbd_contribution)
            VALUES
                (%s, %s, %s)
        """

        try:
            for unit_posting in postdata:
                cursor.execute(query_posting, (
                      unit_posting['permlink']
                    , unit_posting['created']
                    , unit_posting['total_sbd']
                    ,
                    ))

                for unit_userVote in unit_posting['voters']:
                    cursor.execute(query_userVote, (
                          unit_userVote['voter']
                        , unit_posting['permlink']
                        , unit_userVote['sbd_contribution']
                        ,
                        ))

        except:
            conn.rollback()
            traceback.print_exc()

        conn.commit()
        self.connObj.closeConnection(conn)

if __name__ == "__main__":
    st = SteemPosting()
    permlinks = st.getRecentPaidOutPostPermlinks()
    if len(permlinks) < 1:
        print("Nothing to record")
        sys.exit(0)

    filtered_permlinks = st.getValidPermlinks(permlinks)
    if len(filtered_permlinks) < 1:
        print("Nothing to record")
        sys.exit(0)

    result = st.getCalcDataFromPermlinks(filtered_permlinks)
    print("DB recording...")
    st.insertPostRecord(result)
