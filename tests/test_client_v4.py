from unittest import TestCase, main
import logging
import os
import sys

from tempoapiclient.client_v4 import Tempo

# please set TEMPO_AUTH_TOKEN to environment before running this test

log = logging.getLogger()


class TestClient(TestCase):

    def setUp(self):
        self.tempo = Tempo(auth_token=os.environ.get('TEMPO_AUTH_TOKEN'))
        self.dateFrom = "2020-09-01"
        self.dateTo = "2020-10-01"

        self.accountId = os.environ.get('TEMPO_ACCOUNT_ID')
        self.issueId = os.environ.get('TEMPO_ISSUE_ID')

    
    def test_client_creation(self):
        self.assertTrue(isinstance(self.tempo, Tempo))
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

    @staticmethod
    def _compare_worklog_to_parameters(worklog, parameters):
        """
        Compares worklog values to parameters of create_worklog and update_worklog methods

        :param worklog: Worklog returned from Tempo
        :param parameters: parameters for create_worklog and update_worklog methods
        """
        return (
            all((
                worklog[keys[0]] == parameters[keys[1]] for keys in (
                    ("startDate", "dateFrom", ),
                    ("timeSpentSeconds", "timeSpentSeconds", ),
                    ("description", "description", ),
                )
            ))
            and
            worklog["author"]["accountId"] == parameters["accountId"]
        )

    @staticmethod
    def _compare_worklogs(worklog_a, worklog_b):
        """
        Compares values of two worklogs together
        """
        return all((
            worklog_a[key] == worklog_b[key] for key in (
                "tempoWorklogId", "author", "issue", "startDate",
                "timeSpentSeconds", "description", )
        ))

    def test_worklog_cycle(self):
        """
        Tests worklog creation, read, update and deletion

        This test creates a new worklog, reads it, updated it and finally deletes it.
        Thus, you may not want to run this test in a production environment.

        The following environments are required in order to run this test:
        * TEMPO_ACCOUNT_ID: the Jira account id to be set as the author of the worklog
        * TEMPO_ISSUE_ID: the Jira issue id the Worklog is created
        """

        # Test worklog creation (and read)
        create_parameters = {
            "accountId": self.accountId,
            "issueId": self.issueId,
            "dateFrom": self.dateFrom,
            "timeSpentSeconds": 7200,
            "description": "TEST worklog",
        }

        created_worklog = self.tempo.create_worklog(**create_parameters)

        log.debug("created_worklog: %r", created_worklog)
        print(f"test_worklog_cycle: created worklog with ID: "
              f"{created_worklog.get('tempoWorklogId')}")

        self.assertIsInstance(created_worklog, dict)
        self.assertEqual(created_worklog["issue"]["id"], int(create_parameters["issueId"]))
        self.assertTrue(self._compare_worklog_to_parameters(created_worklog,
                                                            create_parameters))

        read_created_worklog = self.tempo.get_worklogs(
            self.dateFrom, self.dateFrom,
            worklogId=created_worklog.get('tempoWorklogId')
        )
        log.debug("read_created_worklog: %r", read_created_worklog)

        self.assertIsInstance(read_created_worklog, dict)
        self.assertTrue(self._compare_worklogs(created_worklog, read_created_worklog))

        # Test worklog update (and read)
        update_parameters = {
            "id": created_worklog["tempoWorklogId"],
            "accountId": self.accountId,
            "dateFrom": self.dateFrom,
            "timeSpentSeconds": 10800,
            "description": "Updated TEST worklog",
        }

        updated_worklog = self.tempo.update_worklog(**update_parameters)

        log.debug("updated_worklog: %r", updated_worklog)
        print(f"test_worklog_cycle: updated worklog with ID: "
              f"{updated_worklog.get('tempoWorklogId')}")

        self.assertIsInstance(updated_worklog, dict)
        self.assertEqual(created_worklog["tempoWorklogId"], updated_worklog["tempoWorklogId"])
        self.assertTrue(self._compare_worklog_to_parameters(updated_worklog,
                                                            update_parameters))

        read_updated_worklog = self.tempo.get_worklogs(
            self.dateFrom, self.dateFrom,
            worklogId=created_worklog.get('tempoWorklogId')
        )
        log.debug("read_updated_worklog: %r", read_updated_worklog)

        self.assertIsInstance(read_updated_worklog, dict)
        self.assertTrue(self._compare_worklogs(updated_worklog, read_updated_worklog))

        # Test worklog deletion
        deleted_worklog = self.tempo.delete_worklog(created_worklog['tempoWorklogId'])

        log.debug("deleted_worklog: %r", deleted_worklog)

        self.assertIsInstance(deleted_worklog, dict)
        self.assertFalse(deleted_worklog)

        # The worklog should not exist anymore
        with self.assertRaises(SystemExit) as exc:
            read_deleted_worklog = self.tempo.get_worklogs(
                self.dateFrom, self.dateFrom,
                worklogId=created_worklog.get('tempoWorklogId')
            )

        print(f"test_worklog_cycle: deleted worklog with ID: {created_worklog.get('tempoWorklogId')}")

    def test_get_worklogs(self):
        """
        Tests reading worklogs
        """
        worklogs = self.tempo.get_worklogs(self.dateFrom, self.dateTo)

        log.debug("worklogs: %r", worklogs)
        print(f"get_worklogs: {len(worklogs)}")

        self.assertIsInstance(worklogs, list)

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
