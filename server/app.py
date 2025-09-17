# server/app.py

from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Message
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    @app.route('/messages', methods=['GET'])
    def get_messages():
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([m.to_dict() for m in messages]), 200

    @app.route('/messages', methods=['POST'])
    def create_message():
        data = request.get_json() if request.is_json else request.form
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({"error": "Missing body or username"}), 400

        new_msg = Message(body=body, username=username)
        db.session.add(new_msg)
        db.session.commit()

        return jsonify(new_msg.to_dict()), 201

    @app.route('/messages/<int:id>', methods=['PATCH'])
    def update_message(id):
        msg = Message.query.get(id)
        if msg is None:
            abort(404, description=f"Message with id {id} not found")

        data = request.get_json() if request.is_json else request.form
        if 'body' in data:
            msg.body = data['body']
        # you could update other fields if needed

        db.session.commit()
        return jsonify(msg.to_dict()), 200

    @app.route('/messages/<int:id>', methods=['DELETE'])
    def delete_message(id):
        msg = Message.query.get(id)
        if msg is None:
            abort(404, description=f"Message with id {id} not found")

        db.session.delete(msg)
        db.session.commit()
        return jsonify({"message": f"Message {id} successfully deleted"}), 200

    return app

# create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)



