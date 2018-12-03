from flask_restful import Resource, reqparse
from models import UserModel, RevokedTokenModel, PortfolioModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims)
import json
from flask import request
parser = reqparse.RequestParser()



class UserRegistration(Resource):
    def post(self):
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}
        
        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password'])
        )
        
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        print(current_user)
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()
    
    def delete(self):
        return UserModel.delete_all()


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }
class Mirror(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        print(data)
        return {
            'you': json.dumps(data)
        }
class Portfolio(Resource):
    @jwt_required
    def post(self):
        #try:           
        parser.add_argument('portfolio', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        name = data['portfolio']
        current_user = get_jwt_identity()
        current_user_model = UserModel.find_by_username(current_user)
        new_portfolio = PortfolioModel(name = name)
        current_user_model.add_portfolio(new_portfolio)
        new_portfolio.add_data()
        current_user_model.add_data()
        new_portfolio.commit()
        return { "message": "{0} created {1}".format(current_user, name)}
        #except:
            #return {"message":"Something went wrong"}
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        porto = []
        for i in current_user_model.portfolios:
            porto.append(i.name)
        return {"user":current_user,"portfolios":porto}
class PortfolioSpecific(Resource):
    @jwt_required
    def get(self, id):
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        return {"portfolio":current_user_model.portfolios[id+1].name}
        #index out of range exception possible
    @jwt_required
    def put(self, id):
        #parser.add_argument('portfolio', help = 'This field cannot be blank', required = True)
        #data = parser.parse_args()
        data = request.get_json(silent=True)
        new_name = data['portfolio']
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        new_portfolio = PorfolioModel(name = new_name)
        old_name = current_user_model.portfolios[id+1].name
        current_user_model.portfolios[id+1] = new_portfolio
        current_user_model.add_data()
        new_portfolio.add_data()
        new_portfolio.commit()
        return {"message": "Portfolio {} has been changed to {}".format(old_name, new_name)}
    @jwt_required
    def delete(self, id):
        #parser.add_argument('portfolio', help = 'This field cannot be blank', required = True)
        #data = parser.parse_args()
        data = request.get_json(silent=True)
        delete_name = data['portfolio']
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        return {"message": "{}'s Porfolio {} wasn't deleted cause this functionality is still not implementd".format(current_user, delete_name)}

class TestRest(Resource):
    def post(self):
        dada = request.get_json()
        print(dada)
        return {"whatvar":dada}





        


