from flask import Flask, request, jsonify, redirect
from flask_restful import Api, Resource
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and allow any origin
api = Api(app)

# MongoDB Connection
client = MongoClient('mongodb+srv://proyecto:papas123@cluster0.etmm0wb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.get_database('mydatabase')
collection = db.get_collection('students')

class Student(Resource):
    def get(self, student_id):
        student = collection.find_one({"_id": ObjectId(student_id)})
        if student:
            student['_id'] = str(student['_id'])
            return jsonify(student)
        return {'message': 'Student not found'}, 404

    def post(self):
        data = request.get_json()
        result = collection.insert_one(data)
        return {'message': 'Student created', 'id': str(result.inserted_id)}, 201

    def put(self, student_id):
        data = request.get_json()        
        # Remove _id from the data to avoid attempting to update the immutable field
        if '_id' in data:
            del data['_id']
        result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": data})
        if result.matched_count:
            return {'message': 'Student updated'}
        return {'message': 'Student not found'}, 404

    def delete(self, student_id):
        result = collection.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count:
            return {'message': 'Student deleted'}
        return {'message': 'Student not found'}, 404

class Students(Resource):
    def get(self):
        students = list(collection.find())
        for student in students:
            student['_id'] = str(student['_id'])
        return jsonify(students)

api.add_resource(Student, '/student/<string:student_id>')
api.add_resource(Students, '/students')

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Student Management API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def index():
    return redirect('/swagger')

@app.route('/swagger.json')
def swagger_json():
    swagger_config = {
        "swagger": "2.0",
        "info": {
            "title": "Student Management API",
            "description": "API documentation for managing students",
            "version": "1.0.0"
        },
        "host": request.host,  # Dynamically set the host
        "basePath": "/",
        "schemes": ["http"],
        "paths": {
            "/students": {
                "get": {
                    "summary": "Retrieve all students",
                    "responses": {
                        "200": {
                            "description": "Students retrieved"
                        }
                    }
                },
                "post": {
                    "summary": "Create a new student",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "age": {"type": "integer"},
                                    "course": {"type": "string"},
                                    "school": {"type": "string"}
                                },
                                "required": ["name", "age", "course", "school"]
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Student created"
                        },
                        "400": {
                            "description": "Invalid input"
                        }
                    }
                }
            },
            "/student/{student_id}": {
                "get": {
                    "summary": "Retrieve a specific student by ID",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Student retrieved"
                        },
                        "404": {
                            "description": "Student not found"
                        }
                    }
                },
                "put": {
                    "summary": "Update an existing student",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "age": {"type": "integer"},
                                    "course": {"type": "string"},
                                    "school": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Student updated"
                        },
                        "404": {
                            "description": "Student not found"
                        }
                    }
                },
                "delete": {
                    "summary": "Delete a student",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Student deleted"
                        },
                        "404": {
                            "description": "Student not found"
                        }
                    }
                }
            }
        }
    }
    return jsonify(swagger_config)

if __name__ == '__main__':
    app.run(debug=True)