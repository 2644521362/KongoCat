
from flask import Flask, redirect, request, jsonify


app = Flask(__name__)

@app.route('/alwaysRight/kongoREG', methods=["POST"])
def kongoREG():
    getData = request.get_json()
    Username = getData.get("Username")
    Password = getData.get("Password")
    NickName = getData.get("NickName")
    print(Username, Password, NickName)

    sql = "insert into user(Username,Password,Nickname) values (%s,%s,%s)"



    return jsonify(msg="ok")

if __name__ == '__main__':
    app.run(host="0.0.0.0")
