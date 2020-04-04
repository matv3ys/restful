from main import reqparse

news_parser = reqparse.RequestParser()
news_parser.add_argument('title', required=True)
news_parser.add_argument('content', required=True)
news_parser.add_argument('is_private', required=True, type=bool)
news_parser.add_argument('user_id', required=True, type=int)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True)
user_parser.add_argument('surname', required=True)
user_parser.add_argument('age', required=True, type=int)
user_parser.add_argument('position', required=True)
user_parser.add_argument('speciality', required=True)
user_parser.add_argument('address', required=True)
user_parser.add_argument('email', required=True)