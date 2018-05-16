class CalcFunding:
    def __init__(self):
        pass

    def _calcDistribution(self, period):
        # DB에서 현 회차의 스달량을 긁어온다.
        query = """
            SELECT funding_sbd, operation_sbd
            FROM posting
            WHERE period = %s
        """
        cursor.execute(query, (period, ))
        ret = cursor.fetchone()
        if ret is None or len(ret) < 1:
            return -1

        curr_total_sbd = ret['funding_sbd']

        return curr_total_sbd

    def getTotalPoolWithPeriod(self, start, end):
        subtotal = 0
        for per in range(start, end):
            curr = self._calcDistribution(per)
            if curr > 0:
                subtotal += self._calcDistribution(per)
            else:
                break

        return subtotal

    def getLatestPool(self):
        query = """
            SELECT max(period) as curr_period
            FROM posting
        """
        cursor.execute(query)
        curr_period = cursor.fetchone()['curr_period']
        
        return self._calcDistribution(curr_period)

    def getIndividualDistributionByPost(self, period):
        total = self.getTotalPoolWithPeriod(start, end)
        query = """
            SELECT period, user, portion
            FROM voting
            WHERE period = %s
        """
        cursor.execute(query, (period, ))
        ret = cursor.fetchall()
        recalc = [ [period, user, portion/total] for period, user, portion in ret ]
        return recalc

    def getIndividualDistributionWithPeriod(self, start, end):
        result = {}
        for period in range(start, end):
            sub_result = self.getIndividualDistributionWithPeriod(period)
            result[period] = sub_result

        return result

    def executionSBDWidthdrawl(self, period):
        query = """
            UPDATE posting
              SET is_widthdrawed = true
            WHERE period = %s
        """
        try:
            cursor.execute(query, (period, ))
        except:
            conn.rollback()
            return False

        conn.commit()
        return True

    def inputPurchasedPundix(self, period, purchased_pundi):
        query = """
            INSERT INTO purchased_pundi
                (period, purchased_pundi)
            VALUES
                (%s, %s)
        """
        try:
            cursor.execute(query, (period, purchased_pundi,))
        except:
            conn.rollback()
            return False

        conn.commit()
        return True
