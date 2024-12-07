# from snowflake.core import Root
from snowflake.snowpark import Session

connection_parameters = {
    "account": 'your account name',
    "user":'your user name',
    "password":'your password',
    "database":'database name',
    "schema":'schema name',
    "role":'role if needed',
    "warehouse":'warehouse name',
}

session = Session.builder.config("connection_name", "sfconnection").create()

print(root)
