from decimal import Decimal
from datetime import datetime, timedelta

from steem import Steem

# 스팀잇에서 현황 긁어오는데 사용

class SteemPosting(object):
    def __init__(self):
        self.steem = Steem()
        self.account = "bryanrhee"

        overview = self.steem.get_reward_fund("post")
        steem_prices = self.steem.get_current_median_history_price()

        self.reward_balance = Decimal(overview['reward_balance'].replace(' STEEM', ''))
        self.recent_claims = Decimal(overview['recent_claims'])
        self.feed_price = Decimal(steem_prices['base'].replace(' SBD', ''))

        print("Reward balance: {}".format(self.reward_balance))
        print("Recent claims: {}".format(self.recent_claims))
        print("Feed price: {}".format(self.feed_price))

    def _calcContribution(self, post_data):
        voters = post_data['active_votes']
        total_payout_value = Decimal(post_data['total_payout_value'].replace(" SBD", "")) / 2

        voter_lists = []
        for unit in voters:
            amount = self.reward_balance * self.feed_price * Decimal(unit['rshares']) / self.recent_claims
            voter = unit['voter']
            unit_amount = {'voter':voter, 'amount': amount}
            voter_lists.append(unit_amount)
            print(unit_amount)

        print("Total payout : {} SBD".format(total_payout_value))

        return {"total_sbd":total_payout_value, "voters": voter_lists}

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
        conn = self.getConnection()

    def getCalcDataFromPermlinks(self, permlinks):
        result = {}
        for unit_link in permlinks:
            unit_data = self.steem.get_content(self.account, unit_link)
            result[unit_link] = self._calcContribution(unit_data)

        return result

if __name__ == "__main__":
    st = SteemPosting()
    permlinks = st.getRecentPaidOutPostPermlinks()
    result = st.getCalcDataFromPermlinks(permlinks)
