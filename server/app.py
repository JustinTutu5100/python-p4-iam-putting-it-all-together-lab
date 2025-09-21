from flask import request, session, jsonify
from flask_restful import Resource
from config import app, db, api
from models import User, Recipe

# ------------------- SIGNUP -------------------
class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"errors": str(e)}, 422

api.add_resource(Signup, '/signup')


# ------------------- AUTO-LOGIN -------------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Not logged in"}, 401
        user = User.query.get(user_id)
        if not user:
            return {"error": "Not logged in"}, 401
        return {
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }, 200

api.add_resource(CheckSession, '/check_session')


# ------------------- LOGIN -------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200
        return {"error": "Invalid credentials"}, 401

api.add_resource(Login, '/login')


# ------------------- LOGOUT -------------------
class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Not logged in"}, 401
        session.pop('user_id')
        return {}, 204

api.add_resource(Logout, '/logout')


# ------------------- RECIPES -------------------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get(user_id)
        if not user:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return [{
            "title": r.title,
            "instructions": r.instructions,
            "minutes_to_complete": r.minutes_to_complete,
            "user": {
                "id": r.user.id,
                "username": r.user.username
            }
        } for r in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get(user_id)
        if not user:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return {
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"errors": str(e)}, 422

api.add_resource(RecipeIndex, '/recipes')


# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(debug=True)
