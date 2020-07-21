import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions =  questions[start:end]

    return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app)

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

-
  @app.route('/categories')
  def retrieve_categories():
    categories = {}

    selection = Category.query.order_by(Category.id).all()
    for cat in selection:
      categories[cat.id] = cat.type

    return jsonify({
      'success': True,
      'categories': categories
    })


  @app.route('/questions')
  def retrieve_questions():
    categories = {}
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    selection_ = Category.query.order_by(Category.id).all()

    for cat in selection_:
      categories[cat.id] = cat.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': categories
      
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):

    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


  @app.route('/questions/create', methods=['POST'])
  def add_questions():
    try:
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)

      try:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()
        return jsonify({
          'success': True,
          'created': question.id
          })
      except:
        abort(422)
    except:
      abort(500)

 
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:
      body = request.get_json()
      search = body.get('searchTerm', None)

      try:
        if search:
          selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))
          current_questions = paginate_questions(request, selection)
          
          return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection.all())
            })
      except:
        abort(422)
    except:
      abort(500)


  @app.route('/categories/<int:category_id>/questions')
  def question_category(category_id):

    selection = Question.query.filter(Question.category == category_id).all()
    questions = [question.format() for question in selection]
    selection_ = Category.query.filter(Category.id == category_id)
    categories = [category.format() for category in selection_]

    return jsonify({
      'success': True,
      'category': categories,
      'questions': questions
    })



  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      category = body.get('quiz_category', None)
      previousQuestions = body.get('previous_questions')
      try:
        if category['id'] == 0:
          selection = Question.query.all()
        else:
          selection = Question.query.filter(Question.category == category['id']).all()  

        questions = [question.format() for question in selection]
        question = random.choice(questions)

        # Handle the case where all questions are already passed before finishing the quiz
        questions_id = [question.id for question in selection]
        questions_id.sort()
        previousQuestions.sort()
        if questions_id == previousQuestions:
          return jsonify({
            'success': True,
          })

        while question['id'] in  previousQuestions:
          question = random.choice(questions)

        previousQuestions.append(question)

        return jsonify({
          'success':True,
          'question': question,
          'previousQuestions': previousQuestions,
          
        })
      except:
        abort(404)
    except:
      abort(400)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'method_not_found'
    }), 404

  @app.errorhandler(405)
  def not_allowd(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method_not_allowd'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422

  @app.errorhandler(500)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500

  return app

    