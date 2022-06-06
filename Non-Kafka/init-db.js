db = db.getSiblingDB("user_db");
db.user_login_tb.drop();

db.user_login_tb.insertMany([
    {
        "username": "gauravla",
        "password": "gauravla"
    },
    {
        "username": "deshp",
        "password": "deshp"
    },
]);
