from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import json

###   APP  INITIATION
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Paranuara Challenge API',
    description='Paranuara is a class-m planet. Those types of planets can support human life, for that reason the '
                'president of the Checktoporov decides to send some people to colonise this new planet and reduce the '
                'number of people in their own country. After 10 years, the new president wants to know how the new '
                'colony is growing, and wants some information about his citizens. Hence he hired you to build a rest '
                'API to provide the desired information.'
                'The government from Paranuara will provide you two json files (located at resource folder) which will '
                'provide information about all the citizens in Paranuara (name, age, friends list, fruits and vegetables '
                'they like to eat...) and all founded companies on that planet. Unfortunately, the systems are not that '
                'evolved yet, thus you need to clean and organise the data before use. For example, instead of providing '
                'a list of fruits and vegetables their citizens like, they are providing a list of favourite food, and '
                'you will need to split that list (please, check below the options for fruits and vegetables).',
)

###   API MODEL
ns = api.namespace('paranuara', description='Paranuara Challenge')

resource_fields = api.model('Resource', {
    'name': fields.String,
})

companies_model = api.model('Company', {
    'index': fields.Integer(readOnly=True, description='The company unique identifier'),
    'company': fields.String(required=True, description='The company name')
})

people_model = api.model('People', {
    '_id': fields.String(readOnly=True),
    'index': fields.Integer(required=True, description='The index unique identifier'),
    'guid': fields.String(readOnly=True ),
    'has_died': fields.Boolean(readOnly=True),
    'balance': fields.String(),
    'picture': fields.Url(),
    'age': fields.Integer(readOnly=True),
    'eyeColor': fields.String(readOnly=True, description='The people Eyecolor'),
    'name': fields.String(readOnly=True, description='The people name'),
    'gender': fields.String(readOnly=True, description='The people gender'),
    'company_id': fields.Integer(readOnly=True),
    'email': fields.String(readOnly=True, description='The people Email'),
    'phone': fields.String(readOnly=True, description='The people Phone'),
    'address':  fields.String(readOnly=True, description='The people address'),
    'about':  fields.String(readOnly=True, description='The people description'),
    'registered': fields.String(readOnly=True, description='The people description'),
    'tags': fields.List(fields.String, description='The people tags'),
    'friends': fields.String(),
    'greeting': fields.String(readOnly=True, description='The people greeting'),
    'favouriteFood': fields.List(fields.String, description='The people favouriteFood')
})
employees_resource = dict({
    'name': fields.String(readOnly=True, description='The people name'),
    'age': fields.Integer(readOnly=True),
    'address': fields.String(readOnly=True, description='The people address'),
    'phone': fields.String(readOnly=True, description='The people Phone')
})
mutual_friends_model = api.model('Paranuara', {
    'employees1': fields.Nested(employees_resource),
    'employees2': fields.Nested(employees_resource),
    'friends': fields.String()
})

food_model = api.model('Paranuara', {
    "username": fields.String(),
    "age": fields.Integer(readOnly=True),
    "fruits": fields.List(fields.String, description='The people favourite fruits'),
    "vegetables": fields.List(fields.String, description='The people favourite vegetables')
})


###   Class

class ParanuaraDAO(object):
    def __init__(self):
        self.people = self._load_data('people')
        self.companies = self._load_data('companies')

    def _load_data(self, name):
            with open('resources/{}.json'.format(name)) as file:
                return json.load(file)

    def get_company(self, name):
        for company in self.companies:
            if company['company'].lower()  == name.lower():
                return company
        api.abort(404, "company {} doesn't exist".format(name))

    def get_employee(self, name):
        for employee in self.people:
            if employee['name'].lower() == name.lower():
                return employee
        api.abort(404, "employee {} doesn't exist".format(name))

    def get_employee_id(self, id):
        for employee in self.people:
            if employee['index'] == id:
                return employee
        api.abort(404, "employee {} doesn't exist".format(id))

pDEO = ParanuaraDAO()


###   API Routes

# @ns.route('/companies')
class CompaniesList(Resource):
    '''Shows a list of all companies'''
    @ns.doc('list_companies')
    @ns.marshal_list_with(companies_model)
    def get(self):
        '''List all Companies'''
        return pDEO.companies

# @ns.route('/people')
class PeopleList(Resource):
    '''Shows a list of all People'''

    @ns.doc('list_people')
    @ns.marshal_list_with(people_model)
    def get(self):
        '''List all People'''
        return pDEO.people

@ns.route('/people/company/<name>/')
class EmployeesList(Resource):
    @ns.doc('company\'s employees')
    @ns.marshal_list_with(people_model)
    @api.expect(body=resource_fields)
    @api.response(200, 'Success', people_model)
    def get(self, name):
        '''List of all employees for a Company'''
        employees= []
        _comp = pDEO.get_company(name)
        if len(_comp) > 0: id = _comp.get('index', None)
        if id:
            employees =[employee for employee in pDEO.people if employee['company_id'] == id]
        return employees

@ns.route('/people/employee1/<first_employee_name>/employee2/<second_employee_name>')
class MutualFriendsList(Resource):
    @ns.doc('mutual friends')
    @ns.marshal_list_with(mutual_friends_model)
    @api.response(200, 'Success', mutual_friends_model)
    def get(self, first_employee_name, second_employee_name):
        '''Show two people and their a Mutual friends that are live nad have brown eyecolor
        test names : Collins Berger  Shelby Duke
        '''
        if first_employee_name and second_employee_name:
            employees1 = pDEO.get_employee(first_employee_name)
            employees2 = pDEO.get_employee(second_employee_name.lower())
            _mut_fri =[]
            if employees1 and employees2:
                for em in [x for x in employees1['friends'] if x in employees2['friends']]:
                    __mutfriend = pDEO.get_employee_id(em['index'])
                    print (__mutfriend)
                    if __mutfriend:
                        if __mutfriend['eyeColor'] == 'brown' and not __mutfriend['has_died']:
                            _mut_fri.append(__mutfriend)

                _mutual_friens = {
                    'employees1':{
                        'name':employees1['name'],
                        'age':employees1['age'],
                        'address':employees1['address'],
                        'phone':employees1['phone'],
                    },
                    'employees2': {
                     'name': employees2['name'],
                     'age': employees2['age'],
                     'address': employees2['address'],
                     'phone': employees2['phone'],
                    },
                     'friends': _mut_fri
                }

                return _mutual_friens

@ns.route('/people/<people_name>/foods')
class CompanyObject(Resource):
    @ns.doc('faviourates\'s food')
    @ns.marshal_list_with(food_model)
    @api.response(200, 'Success', food_model)
    def get(self, people_name):
        '''Show a person's faviourats Fruits/Vegs'''
        fruits = []
        vegetables = []
        employees = [employee for employee in pDEO.people if employee['name'].lower() == people_name.lower()]
        _favourite_food = employees[0]["favouriteFood"]
        for food in _favourite_food:
            if food in ["beetroot", "lettuce", "cucumber", "carrot", "celery"]:
                vegetables.append((food))
            else:
                fruits.append(food)
        return {"username": employees[0]['name'],
                "age": employees[0]['age'],
                "fruits": fruits,
                "vegetables": vegetables
                }

if __name__ == '__main__':
    app.run(debug=True)

