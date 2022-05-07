from email import message
import resource
import sqlite3
import flask_sqlalchemy
from termios import TIOCPKT_DOSTOP
from typing_extensions import Required
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
db = SQLAlchemy(app)


class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))


# db.create_all()

todos = {
    # 1: {"task": "Flask Videos", "Summary": "Watch flask tutorial videos"},
    # 2: {"task": "TelMax Code Exploration", "Summary": "Go through the codes of Telmax"},
}

resource_fields = {
    "id": fields.Integer,
    "task": fields.String,
    "summary": fields.String,
}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help="Task is required", required=True)
task_post_args.add_argument(
    "summary", type=str, help="Summary is required", required=True
)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task", type=str)
task_put_args.add_argument("summary", type=str)


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Could not find the task")
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="ID already taken")

        todo = ToDoModel(id=todo_id, task=args["task"], summary=args["summary"])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Task doesn't exist")
        if args["task"]:
            task.task = args["task"]
        if args["summary"]:
            task.summary = args["summary"]
        db.session.commit()
        return task

    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task:
            db.session.delete(task)
        return "ToDo deleted", 204


class ToDoList(Resource):
    def get(self):
        tasks = ToDoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task": task.task, "summary": task.summary}
        return todos


api.add_resource(ToDo, "/todos/<int:todo_id>")
api.add_resource(ToDoList, "/todolist/")

if __name__ == "__main__":
    app.run(debug=True)
