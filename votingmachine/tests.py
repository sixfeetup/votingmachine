from nose import tools
from pyramid import testing


class TestResultsView(object):

    def setup(self):
        self.config = testing.setUp()

    def teardown(self):
        testing.tearDown()

    def no_votes_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [],
        )
        results = results_view(context, request)
        tools.assert_equal(results['scores'], [])

    def one_category_no_weight_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [{'vote_category': 'One Category', 'weight': '1.0'}],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '1'}}}]
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 1.0)

    def one_category_with_weight_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [{'vote_category': 'One Category', 'weight': 0.5}],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '1'}}}]
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 0.5)

    def one_category_with_weight_3_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [{'vote_category': 'One Category', 'weight': '0.5'}],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '3'}}}]
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 1.5)

    def one_category_with_weight_multiple_votes_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [{'vote_category': 'One Category', 'weight': '0.5'}],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '3'}}}],
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '1'}}}],
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '2'}}}],
            [{'team_hidden': '0', 'rankings': {'': {'One Category': '2'}}}],
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 4.0)

    def one_category_with_weight_multiple_votes_and_teams_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [{'vote_category': 'One Category', 'weight': '0.5'}],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context['teams'].add_team(Team('Team One'))
        context.results = [
            [
                {'team_hidden': '0', 'rankings': {'': {'One Category': '3'}}},
                {'team_hidden': '1', 'rankings': {'': {'One Category': '1'}}},
            ],
        ]
        results = results_view(context, request)
        tools.assert_equal(len(results['scores']), 2)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 1.5)
        tools.assert_equal(results['scores'][1][0].title, 'Team One')
        tools.assert_equal(results['scores'][1][1], 0.5)

    def multiple_categories_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [
                {'vote_category': 'One Category', 'weight': '1.0'},
                {'vote_category': 'Two Category', 'weight': '0.5'},
            ],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '1', 'Two Category': '1'}}},
            ]
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 1.5)

    def multiple_categories_multiple_votes_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [
                {'vote_category': 'One Category', 'weight': '1.0'},
                {'vote_category': 'Two Category', 'weight': '0.5'},
            ],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '3', 'Two Category': '2'}}},
            ],
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '2', 'Two Category': '2'}}},
            ],
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '1', 'Two Category': '1'}}},
            ]
        ]
        results = results_view(context, request)
        tools.assert_equal(results['scores'][0][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][0][1], 8.5)

    def multiple_categories_multiple_votes_multiple_teams_test(self):
        from datetime import datetime
        from votingmachine.views import results_view
        from votingmachine.models import VotingBooth
        from votingmachine.models import TeamFolder
        from votingmachine.models import Team
        request = testing.DummyRequest()
        context = VotingBooth(
            'Test Voting Booth',
            datetime(2011, 10, 5, 19, 0, 15, 0),
            datetime(2011, 10, 6, 19, 0, 15, 0),
            [
                {'vote_category': 'One Category', 'weight': '1.0'},
                {'vote_category': 'Two Category', 'weight': '0.5'},
            ],
        )
        context['teams'] = TeamFolder()
        context['teams'].add_team(Team('Team Zero'))
        context['teams'].add_team(Team('Team One'))
        context.results = [
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '1', 'Two Category': '3'}}},
             {'team_hidden': '1', 'rankings': {'': {
                'One Category': '3', 'Two Category': '2'}}},
            ],
            [{'team_hidden': '1', 'rankings': {'': {
                'One Category': '2', 'Two Category': '2'}}},
             {'team_hidden': '0', 'rankings': {'': {
                'One Category': '3', 'Two Category': '2'}}},
            ],
            [{'team_hidden': '0', 'rankings': {'': {
                'One Category': '1', 'Two Category': '1'}}},
             {'team_hidden': '1', 'rankings': {'': {
                'One Category': '1', 'Two Category': '1'}}},
            ]
        ]
        results = results_view(context, request)
        tools.assert_equal(len(results['scores']), 2)
        tools.assert_equal(results['scores'][0][0].title, 'Team One')
        tools.assert_equal(results['scores'][0][1], 8.5)
        tools.assert_equal(results['scores'][1][0].title, 'Team Zero')
        tools.assert_equal(results['scores'][1][1], 8)
