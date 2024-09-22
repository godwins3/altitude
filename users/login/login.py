from sql_conn import mysql_conn
from tokenz import tokens
import bcrypt
from users.normal.persistence import get_user_info


def login(msg_received):
    try:
        key = str(msg_received["key"]).replace(" ", "").replace("_deleted", "")
        plain_password = str(msg_received["password"]).encode('utf-8')
    except KeyError:
        return {"Message": "A key is missing", "statusCode": 401}

    users_id = " "

    conn = mysql_conn.create()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users where phone_number = %s ;", (key,))

    row = cursor.fetchall()

    # while row is not None:
    locator = ""
    hashed_password = ""
    if len(row) == 1:
        for record in row:
            # print(record)

            user_id = int(record[0])
            locator = str(record[3])
            hashed_password = str(record[2]).encode('utf8')

        if bcrypt.checkpw(plain_password, hashed_password):

            tkn = str(tokens.generate_token(user_id, locator))
            cursor.close()
            conn.close()

            return {"Message": "Sign in successful", "token": tkn, "statusCode": 200}

        else:
            cursor.close()
            conn.close()
            return {"Message": "wrong login details provided", "statusCode": 404}

    else:
        cursor.close()
        conn.close()
        return {"Message": "wrong login details provided", "statusCode": 404}
