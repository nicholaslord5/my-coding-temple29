from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    membership_type = db.Column(db.String(50), nullable=False)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    type = db.Column(db.String(100), nullable=False)

    member = db.relationship('Member', backref=db.backref('workout_sessions', lazy=True))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

from flask import request, jsonify

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'], membership_type=data['membership_type'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'New member created!', 'id': new_member.id}), 201

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify({'id': member.id, 'name': member.name, 'email': member.email, 'membership_type': member.membership_type})

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    member.membership_type = data.get('membership_type', member.membership_type)
    db.session.commit()
    return jsonify({'message': 'Member updated!'})

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted!'})

@app.route('/workouts', methods=['POST'])
def add_workout():
    data = request.get_json()
    new_workout = WorkoutSession(member_id=data['member_id'], date=data['date'], duration=data['duration'], type=data['type'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'Workout session added!', 'id': new_workout.id}), 201

@app.route('/workouts/<int:workout_id>', methods=['GET'])
def get_workout(workout_id):
    workout = WorkoutSession.query.get_or_404(workout_id)
    return jsonify({'id': workout.id, 'member_id': workout.member_id, 'date': workout.date.isoformat(), 
                    'duration': workout.duration, 'type': workout.type})

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_workouts_for_member(member_id):
    member = Member.query.get_or_404(member_id)
    workouts = [workout.to_dict() for workout in member.workout_sessions]
    return jsonify(workouts)

# Assuming you have a method `to_dict` in your model for serialization:
class WorkoutSession(db.Model):
    # ... previous definitions

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'date': self.date.isoformat(),
            'duration': self.duration,
            'type': self.type
        }