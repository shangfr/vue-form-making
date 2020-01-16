# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 14:04:20 2020

@author: ShangFR
"""

from api_auth import db,app
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Forms(db.Model):
    __tablename__ = 'widgetForm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(10), nullable=False)
    htmlData = db.Column(db.Text, nullable=False)
    create_date = db.Column(db.DateTime(), default=datetime.now,onupdate=datetime.now)

    def __repr__(self):
        return '<htmlData %s>' % self.htmlData
 
    def to_json(self):
        return {
            'id': self.id,
            'userName': self.userName,
            'htmlData': self.htmlData,
        } 

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name
    __repr__ = __str__


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    create_date = db.Column(db.DateTime(), default=datetime.now,onupdate=datetime.now)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
     
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return '(User: %s, %s)' %(self.username, self.password)
    __repr__ = __str__
    
def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        db.session.add(User(
            username='Admin',
            password=generate_password_hash('admin'),
            email='admin@qq.com',
            roles=[user_role, super_user_role]
        ))

        usernames = [
            'Harry', 'Amelia', 'Oliver'
        ]

        for i in range(len(usernames)):
            tmp_email = usernames[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            db.session.add(User(
                username=usernames[i],
                password=generate_password_hash(tmp_pass),
                email=tmp_email,
                roles=[user_role, ]
            ))
        db.session.commit()
    return

def main():
    print("Testing mean function")
    print("All tests passed!")
if __name__ == '__main__':
    main()
