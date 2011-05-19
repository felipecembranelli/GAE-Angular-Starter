'''
Created on April 25, 2011

@author: Chris Boesch
'''
import unittest
#from google.appengine.ext import db
import logging
from tournament import models
from tournament import views

class Test_Tournament_Views(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        for x in models.User.all(): x.delete()
        
    def test_user_creation(self):  
        self.assertEqual(1, 1)
        user = models.User(user_id ='Bob').save()
        results = models.User.all()
        self.assertEqual(results.count(),1)

    def test_run_round(self):
        numPlayers = 2;
        for player in range(numPlayers):
          app = models.App(name='TestApp '+str(player), url='DEFAULT_TICTACTOE')
          app.put()
        
        tournamentHeat = models.TournamentHeat(name='TestTournament')
        tournamentHeat.put()
        #tournamentHeat = models.TournamentHeat.all().get()
        numGames = models.Game.all().count()
        self.assertEqual(0, numGames)
        
        result = views.run_round(tournamentHeat)
        
        self.assertTrue('points' in result)
        self.assertTrue('losses' in result)
        self.assertTrue('appNames' in result)
        self.assertTrue('matchResults' in result)
        self.assertTrue('appIDs' in result)
        self.assertTrue('ids' in result)
        
        self.assertEqual(numPlayers, len(result['points']))

        numGames = models.Game.all().count()
        self.assertEqual(2, numGames)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
