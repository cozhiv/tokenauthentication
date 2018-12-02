#from run import db
from sqlalchemy import create_engine, func, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Column, Integer, String, DateTime
import pymysql

engine = create_engine(
      "mysql+pymysql://root:root@localhost/otnovo")
#?encoding=utf8
#?host=localhost?port=3306
#engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    username = Column(String(120), unique = True, nullable = False)
    password = Column(String(120), nullable = False)
    signedup = Column(DateTime, default=func.now())
    portfolios = relationship(
        "PortfolioModel",
        secondary='portfolio_usermodel_link'
    )
    def __init__(self, username=None, password=None, signedup=func.now()):
        self.username = username
        self.password = password
        self.signedup = signedup

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    def save_to_db(self):
        db_session.add(self)
        db_session.commit()
    

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    def add_portfolio(self, portfolio):
        self.portfolios.append(portfolio)
        #db_session.add(self)
        #db_session.commit()
    def add_data(self):
        db_session.add(self)
    def get_portfolio(self, table, portfolio):
        return db_session.query(self).filter(self.portfolios.any(table.name == portfolio)).all()[0].name

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db_session.query(cls).delete()
            db_session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}
    
    

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key = True)
    jti = Column(String(120))

    def __init__(self, jti=None):
        self.jti = jti

    def add(self):
        db_session.add(self)
        db_session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


class PortfolioModel(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable = False)
    made_on = Column(DateTime, default=func.now())
    owner = relationship(
        UserModel,
        secondary='portfolio_usermodel_link'
    )
    def __init__(self, name = None, made_on = func.now()):
        self.name = name
        self.made_on = made_on
        #self.owner = owner
    
    def __repr__(self):
        return '<Portfolio %r>' % (self.name)

    def add_user(self, user):
        self.owner.append(user)
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.name,
                'owner': x.owner

            }
        return {'portfolios': list(map(lambda x: to_json(x), PortfolioModel.query.all()))}
    
    def get_user(self, table, owner):
        return db_session.query(self).filter(self.owner.any(table.name == owner)).all()[0].name

    def add_data(self):
        db_session.add(self) 
    def commit(self):
        db_session.commit()

class PorfolioUserModelLink(Base):
    __tablename__ = 'portfolio_usermodel_link'
    #id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), primary_key=True)
    usermodel_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    #from models import User
    Base.metadata.create_all(bind=engine)

#https://www.pythoncentral.io/sqlalchemy-association-tables/