from unittest import TestCase, main
import os
import sys

from tempoapiclient import client

# please set TEMPO_AUTH_TOKEN to environment before running this test


class TestClient(TestCase):

    def setUp(self):
        self.tempo = client.Tempo(auth_token=os.environ.get('TEMPO_AUTH_TOKEN'))
        self.dateFrom = "2020-09-01"
        self.dateTo = "2020-10-01"
    
    def test_client_creation(self):
        self.assertTrue(isinstance(self.tempo, client.Tempo))
        pass

    def test_get_accounts(self):
        l = self.tempo.get_accounts()
        print("get_accounts: ", len(l))
        pass

    def test_get_account_categories(self):
        l = self.tempo.get_account_categories()
        print("get_account_categories: ", len(l))
        pass

    def test_get_account_category_types(self):
        l = self.tempo.get_account_category_types()
        print("get_account_category_types: ", len(l))

    def test_get_customers(self):
        l = self.tempo.get_customers()
        print("get_customers: ", len(l))

    def test_get_holiday_schemes(self):
        l = self.tempo.get_holiday_schemes()
        print("get_holiday_schemes: ", len(l))

    def test_get_periods(self):
        l = self.tempo.get_periods(dateFrom=self.dateFrom, dateTo=self.dateTo)
        print("get_periods: ", len(l))

    def test_get_plans(self):
        l = self.tempo.get_plans(dateFrom=self.dateFrom, dateTo=self.dateTo)
        print("get_plans: ", len(l))

    def test_get_teams(self):
        l = self.tempo.get_teams()
        print("get_teams: ", len(l))

    def test_get_team_members(self):
        team_id = [int(i['id']) for i in self.tempo.get_teams()][0]
        team_members = self.tempo.get_team_members(teamId=team_id)
        self.assertIsInstance(team_members, list)
        self.assertIsInstance(team_members[0], dict)
        self.assertIsInstance(team_members[0]['member'], dict)

    #def test_get_team_memberships(self):
        # l = self.tempo.get_team_memberships(membershipId=)
        # display(l)

    #def test_get_account_team_membership(self):
        # l = self.tempo.get_account_team_membership(teamId=1, accountId=8)
        # print("get_account_team_membership: ", len(l))

    #def test_get_account_team_memberships(self):
        # l = self.tempo.get_account_team_memberships(teamId=1, accountId=8)
        # print("get_account_team_memberships: ", len(l))

    def tearDown(self):
        self.tempo.close()


if __name__ == "__main__":
    main()
