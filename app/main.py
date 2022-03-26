from flask import Flask, jsonify, request
from  flask_restful import Api, Resource, reqparse, abort
from flask_cors import CORS
# from flask_pymongo import pymongo
import app.db_config as database

app = Flask(__name__)
api = Api(app)
CORS(app)

post_students_args = reqparse.RequestParser()

post_students_args.add_argument("id", type=int, help="ERROR id value need to be an integer",required=True)
post_students_args.add_argument("first_name", type=str, help="ERROR first_name is required",required=True)
post_students_args.add_argument("last_name", type=str, help="ERROR last_name is required",required=True)
post_students_args.add_argument("image", type=str, help="ERROR you need to add image URL",required=True)
post_students_args.add_argument("group", type=str, required=False)
post_students_args.add_argument("career", type=str, required=False)


patch_students_args = reqparse.RequestParser()

patch_students_args.add_argument("id", type=int, help="ERROR id value need to be an integer",required=False)
patch_students_args.add_argument("first_name", type=str, help="ERROR first_name is required",required=False)
patch_students_args.add_argument("last_name", type=str, help="ERROR last_name is required",required=False)
patch_students_args.add_argument("image", type=str, help="ERROR you need to add image URL",required=False)
patch_students_args.add_argument("group", type=str, required=False)
patch_students_args.add_argument("career", type=str, required=False)

class Test(Resource):

    def get(self):
        return jsonify({"message":"You are connected"})

class Students(Resource):
    
    def get(self):
        response = list(database.db.students.find())
        students = []
        for student in response:
            del student['_id']
            students.append(student)
        return jsonify({'results':students})


class Student(Resource):

    def get(self, id):
        response = database.db.students.find_one({'id':id})
        del response['_id']
        return jsonify(response)

    def post(self):
        self.abort_id_id_exist(request.json['id'])
        args = post_students_args.parse_args()
        print(args)
        database.db.students.insert_one({
            'id':args['id'],
            'first_name': args['first_name'],
            'last_name': args['last_name'],
            'image': args['image'],
            'group': args['group'],
            'career': args['career'],
        })
        return jsonify(args)

    def put(self, id):
        args = post_students_args.parse_args()
        self.abort_if_not_exist(id)
        database.db.students.update_one(
            {'id': id},
            {'$set': {
                'id': args['id'],
                'first_name': args['first_name'],
                'last_name': args['last_name'],
                'image': args['image'],
                'group': args['group'],
                'career': args['career'],
            }}
        )
        return jsonify(args)
    
    def patch(self, id):
        student = self.abort_if_not_exist(id)
        args = patch_students_args.parse_args()

        database.db.students.update_one(
            {'id': id},
            {'$set': {
                'id': args['id'],
                'first_name': args['first_name'],
                'last_name': args['last_name'],
                'image': args['image'],
                'group': args['group'],
                'career': args['career'],
            }}
        )

    def delete(self,id):
        student = self.abort_if_not_exist(id)
        database.db.students.delete_one({'id':id})
        del student['_id']
        return jsonify({'deleted': student})

    def abort_id_id_exist(self,id):
        if database.db.students.find_one({'id':id}):
            abort(jsonify({'status':'406','error': f"The student with the id; {id} already exist"}))
    
    def abort_if_not_exist(self,id):
        student = database.db.students.find_one({'id': id})
        if not student:
            abort(jsonify({'status':'404', 'error': f"The student with the id: {id} not found"}))

        else:
            return student

api.add_resource(Test,'/test/')
api.add_resource(Students,'/students/')
api.add_resource(Student, '/student/', '/student/<int:id>')
if __name__ == '__main__':
    app.run(load_dotenv=True, port=8000)
