import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Walid$1990','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who was the 33rd president of the U.S.A?',
            'answer': 'Harry S. Truman',
            'category': '4',
            'difficulty': '2'
            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_paginated_question(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_sent_requesting_beyond_valide_page(self):
        res = self.client().get('/questions?page=100', json={'category': '3'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method_not_found')

    # def test_delete_question(self):
    #     res = self.client().delete('questions/87')
    #     data = json.loads(res.data)

    #     question = Question.query.filter(Question.id == 87).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'], 87)
    #     self.assertTrue(data['questions'])
    #     self.assertTrue(data['total_questions'])
    #     self.assertEqual(question, None)

    def test_422_if_question_does_not_excit(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        res = self.client().post('/questions/create', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_creat_question_error(self):
        res = self.client().post('/questions/create')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_question_error(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

    def test_question_cateory(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['category'])
        self.assertTrue(data['questions'])

    def test_question_cateory_error(self):
        res = self.client().get('/categories/10/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])
        
    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': '1', 'type': 'Science'}, 'previous_questions': [5]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['previousQuestions'])

    def test_405_get_for_quiz(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method_not_allowd')

    def test_400_quizz(self):
        res = self.client().post('/quizzes', json={'quiz_category': "{'id': '1', 'type': 'Science'},",  'previous_questions': [5]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()