import unittest
from server import Server
from follower import Follower
from candidate import Candidate
from leader import Leader

class TestCandidateServer( unittest.TestCase ):
	def setUp( self ):
		state = Follower()
		self.oserver = Server( 0, state, [], [] )
		state = Candidate()
		self.server = Server( 1, state, [], [ self.oserver ] )
		self.oserver._neighbors.append( self.server )

	def test_candidate_server_had_intiated_the_election( self ):
		self.assertEquals(1, len( self.oserver._board ) )
		self.oserver.on_message( self.oserver.get_message() )
		self.assertEquals(1, len( self.server._board ) )
		self.assertEquals(True, self.server.get_message().data["response"] )

	def test_candidate_server_had_gotten_the_vote( self ):
		self.oserver.on_message( self.oserver.get_message() )
		self.assertEquals( 1, len( self.server._board ) )
		self.assertEquals( True, self.server.get_message().data["response"] )

	def test_candidate_server_wins_election( self ):
		state = Follower()
		server0 = Server( 0, state, [], [] )
		state = Follower()
		oserver = Server( 1, state, [], [] )
		state = Candidate()
		server = Server( 2, state, [], [ oserver, server0 ] )
		server0._neighbors.append( server )
		oserver._neighbors.append( server )
		oserver.on_message( oserver.get_message() )
		server0.on_message( server0.get_message() )
		server._total_nodes = 3
		server.on_message( server.get_message() )
		server.on_message( server.get_message() )
		self.assertEquals( type( server._state ), Leader )

	def test_two_candidates_tie( self ):
		followers = []

		for i in range( 4 ):
			state = Follower()
			followers.append( Server( i, state, [], [] ) )

		state = Candidate()
		c0 = Server( 5, state, [], followers[0:2] )

		state = Candidate()
		c1 = Server( 6, state, [], followers[2:] )

		for i in range( 2 ):
			followers[i]._neighbors.append( c0 )
			followers[i].on_message( followers[i].get_message() )

		for i in range( 2, 4 ):
			followers[i]._neighbors.append( c1 )
			followers[i].on_message( followers[i].get_message() )

		c0._total_nodes = 6
		c1._total_nodes = 6

		for i in range( 2 ):
			c0.on_message( c0.get_message() )
			c1.on_message( c1.get_message() )

		self.assertEquals( type( c0._state ), Candidate )
		self.assertEquals( type( c1._state ), Candidate )

	def test_two_candidates_one_wins( self ):
		followers = []
		for i in range( 6 ):
			state = Follower()
			followers.append( Server( i, state, [], [] ) )

		state = Candidate()
		c0 = Server( 7, state, [], followers[0:2] )

		state = Candidate()
		c1 = Server( 8, state, [], followers[2:] )

		for i in range( 2 ):
			followers[i]._neighbors.append( c0 )
			followers[i].on_message( followers[i].get_message() )

		for i in range( 2, 6 ):
			followers[i]._neighbors.append( c1 )
			followers[i].on_message( followers[i].get_message() )

		c0._total_nodes = 8
		c1._total_nodes = 8

		for i in range( 2 ):
			c0.on_message( c0.get_message() )
			
		for i in range( 4 ):
			c1.on_message( c1.get_message() )

		self.assertEquals( type( c0._state ), Candidate )
		self.assertEquals( type( c1._state ), Leader )

	def test_candidate_fails_to_win_election_so_resend_request( self ):
		pass

	def test_multiple_candidates_fail_to_win_so_resend_requests( self ):
		pass

