
import sys
import os

from flask import Flask, request, Response
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import json
from flask_cors import CORS
from database import database
from s3 import upload_file_to_s3
from config import S3_LOCATION, S3_KEY, S3_SECRET, S3_BUCKET
sys.path.append(os.path.abspath('../pdf-parser/parser'))
import script
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['CORS_HEADERS'] = ['Content-Type']
app.config["S3_BUCKET"] = S3_BUCKET
cors = CORS(app, resources={r"/api": {"origins": "*"}})

api = Api(app)

try:
    cur = database().cursor()
    print("connected")
except ValueError:
    print("Oops! Cannot connect to the database...")


class Rule_Helper:
    _company_id = None

    def __init__(self, id=None):
        self._company_id = id

    def query(self, column, table):
        if (self._company_id is None):
            return """SELECT %s FROM %s""" % (column, table)
        else:
            return """SELECT %s FROM %s WHERE Company_ID = %s""" % (
                column, table, self._company_id)

    def get_company(self):
        sql = self.query("*", "Company")
        cur.execute(sql)
        result = cur.fetchall()
        return result

    def get_format(self):
        sql = self.query(
            "*", "Company_Financial_Statement_Format")
        cur.execute(sql)
        result = cur.fetchone()
        return result

    def get_column_headers(self):
        result = []
        sql = self.query("Column_Header_Text",
                         "Financial_Statement_Column_Header")
        cur.execute(sql)
        data_set = cur.fetchall()
        for row in data_set:
            result.append(row["Column_Header_Text"])
        return result

    def get_keyword_match(self):
        result = []
        if (self._company_id is None):
            sql = """SELECT Word.Key_Word_Text, IA.IA_Classification_Text
                FROM Key_words_IA_Clasification Rel
                LEFT JOIN Key_words Word ON Word.Key_Word_Code = Rel.Key_Word_Code
                LEFT JOIN IA_Clasification IA ON IA.IA_Classification_Code =  Rel.IA_Classification_Code"""
        else:
            sql = """SELECT Word.Key_Word_Text, IA.IA_Classification_Text
                FROM Key_words_IA_Clasification Rel
                LEFT JOIN Key_words Word ON Word.Key_Word_Code = Rel.Key_Word_Code
                LEFT JOIN IA_Clasification IA ON IA.IA_Classification_Code =  Rel.IA_Classification_Code
                WHERE Rel.Company_ID = %s""" % (self._company_id)

        cur.execute(sql)
        data_set = cur.fetchall()
        for row in data_set:
            _pattern = {
                row["Key_Word_Text"]: row["IA_Classification_Text"]
            }
            result.append(_pattern)
        return result


class Helpers:
    @staticmethod
    def convert_list_to_dic(items):
        result = {}
        for item in items:
            for attr, value in item.items():
                result[attr] = value
        return result


class Rules(Resource):
    def get(self, id=None):
        result = []
        _companies = Rule_Helper().get_company()

        for row in _companies:
            _id = row["Company_ID"]
            _rules = {}
            # Get format, headers and keyword_match
            _format = Rule_Helper(_id).get_format()
            for attr, value in _format.items():
                _rules[attr] = value

            _rules["headers"] = Rule_Helper(_id).get_column_headers()
            _rules["keyword_match"] = Helpers.convert_list_to_dic(
                Rule_Helper(_id).get_keyword_match())

            _company = {
                row["Company_Name"]: _rules
            }
            result.append(_company)

        return result


class Rule(Resource):

    def get(self, id):
        _format = Rule_Helper(id).get_format()
        _headers = Rule_Helper(id).get_column_headers()
        _keyword_match = Helpers.convert_list_to_dic(
            Rule_Helper(id).get_keyword_match())
        result = {
            "format": _format,
            "headers": _headers,
            "keyword_match": _keyword_match
        }
        return result


class IA_Helper:
    _code = None
    _name = None

    def __init__(self, id=None, name=None):
        self._code = id
        self._name = name

    def get_code(self):
        sql = """SELECT IA_Classification_Code FROM IA_Clasification WHERE IA_Classification_Text= %s""" % (
            self._name)
        cur.execute(sql)
        return cur.fetchone()

    def get_name(self):
        sql = """SELECT IA_Classification_Text FROM IA_Clasification WHERE IA_Classification_Code= %s""" % (
            self._code)
        cur.execute(sql)
        return cur.fetchone()


class Transaction(Resource):
    def get(self, id):
        result = {}
        sql = """SELECT IA_Classification_Code, Accounting_Transaction_Amount
         FROM Calculated_Transaction WHERE Company_ID= %s""" % (id)

        cur.execute(sql)
        data_set = cur.fetchall()

        for row in data_set:
            _IA_text = IA_Helper(row["IA_Classification_Code"]).get_name()[
                'IA_Classification_Text']
            result[_IA_text] = float(row["Accounting_Transaction_Amount"])
        return result

    def post(self, data):
        return data


class Upload(Resource):
    def post(self):
        files = request.files.getlist("files[]")
        print(request.files.keys())
        for file in files:
            print("counttt")
            filename = secure_filename(file.filename)
            self.process_file(file, filename)

    def process_file(self, file, name):
        # Save S3 Link
        # output = upload_file_to_s3(file, app.config["S3_BUCKET"])

        _id = self.get_company_id(
            self.get_file_business_unit(name))
        # self.save_s3_link(output, _id)

        # Save Final Transaction
        result = script.process_pdf(
            file.read(), self.get_rules(name))
        print('result!!!!!!!!!', result)

        return result

    def options(self):
        resp = Response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Allow-Methods'] = 'POST'
        return resp

    def get_company_id(self, business_unit):
        sql = """SELECT company_id FROM Business_Unit WHERE value = %s""" % (
            business_unit)
        cur.execute(sql)
        return cur.fetchone()["company_id"]

    def get_file_business_unit(self, name):
        print('business unit', name.split("_")[0])
        return name.split("_")[0]

    def get_rules(self, name):
        _id = self.get_company_id(self.get_file_business_unit(name))
        return Rule().get(_id)

    def save_s3_link(self, link, id):
        sql = """"UPDATE Company SET S3_Link = %s WHERE Company_Id = %s""" % (
            link, id)
        cur.execute(sql)
        cur.commit()
        return link

    def save_final_transaction(self, calculated_data, id):
        for row in calculated_data:
            _code = IA_Helper(row["category"])
            _amount = row["amount"]
            sql = """INSERT INTO Calculated_Transaction 
            (Company_Id, IA_Classification_Code, Accounting_Transaction_Amount) values (%s, %s, %s)""" % (
                id, _code, _amount)
            cur.execute(sql)
            cur.commit
            ()
        return calculated_data


api.add_resource(Rules, '/api/rules', methods=['GET'])
api.add_resource(Rule, '/api/rules/<id>',
                 methods=['GET', 'POST', 'DELETE', 'PUT'])
api.add_resource(Upload, '/api/upload', methods=['POST', 'OPTIONS'])
api.add_resource(Transaction, '/api/transaction/<id>', methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
