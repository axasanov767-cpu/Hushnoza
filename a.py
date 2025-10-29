# todo proect uchun logging 

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': 'todo_log.log',
#             'formatter': 'verbose'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'todo': {  
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }



# Misol 1 

# from collections import namedtuple

# Person = namedtuple('Person', ['name', 'age', 'city'])
# p1 = Person('Hushnoza', 15, 'Toshkent')

# print(p1.name)
# print(p1.age)

# # misol 2

# Car = namedtuple('Car', ['brand', 'model', 'price'])
# my_car = Car('BMW', 'X7', 120000)


# print(f"{my_car.brand} narxi: ${my_car.price}")

# misol 3 

Book = namedtuple('Book', ['title', 'author', 'pages'])
b1 = Book('Seni topgan kun', 'Mirach Chag‘ri Oqtosh', 256)

print(f"Kitob: {b1.title} — Muallif: {b1.author}")
