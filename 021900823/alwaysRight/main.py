# coding=utf-8
from flask import Flask, redirect, request, jsonify, session,send_from_directory
from Works.works_method import WorksMethod, AudioWorkMethod, ArticleWorkMethod
from Users.users_method import UserMethod
import os

app = Flask(__name__)


@app.route('/alwaysRight/reg', methods=["POST"])  # need put in
def register():
    getData = request.get_json()
    phone = getData.get('phone')

    session['phone']=phone
    return jsonify(msg="user Phone Put in !")


@app.route('/alwaysRight/setInfoByUserId', methods=["POST"])  # need put in
def setInfoByUserId():
    ingore = 1
    getData = request.get_json()
    nickName = getData.get("nickName")
    country = getData.get("country")
    province = getData.get("province")
    city = getData.get("city")
    gender = getData.get("gender")
    language = getData.get("language")
    if nickName:
        ingore = 1
    if country:
        ingore = 1
    if province:
        ingore = 1
    if city:
        ingore = 1
    if gender:
        ingore = 1
    if language:
        ingore = 1


    return jsonify(msg="User Info put in !")

@app.route('/alwaysRight/logIn', methods=["POST"])
def login():
    getData = request.get_json()
    phone = getData.get("phone")
    session['phone'] = phone
    return jsonify(msg="session login ! ")


@app.route('/alwaysRight/logOut', methods=["POST"])
def logOut():
    session.clear()
    return jsonify(msg="session erase ! ")


@app.route('/alwaysRight/checkLogin', methods=["POST"])
def checkLogin():
    message = 1
    phone = session['phone']
    if not phone:
        message = 0

    return jsonify(msg=message)


@app.route('/alwaysRight/getRandomWork', methods=["POST"])
def getRandomWork():
    getWork = WorksMethod.get_random_work()  # get random TotalWork
    return jsonify(randomWork=getWork)


@app.route('/alwaysRight/getRandomAudio', methods=["POST"])  # need put in
def getRandomAudio():
    getWork = 1  # get random TotalWork
    return jsonify(randomWork=getWork)


@app.route('/alwaysRight/getUserHistory', methods=["POST"])
def getUserHistory():
    getData = request.get_json()
    id = getData.get("id")
    userData = UserMethod.view_history(id)
    return jsonify(history=userData)


@app.route('/alwaysRight/getUserLikeById', methods=["POST"])
def getUserLikeById():
    id = session.get('phone')
    userData = UserMethod.view_mark(id)
    print(userData)
    return jsonify(Like=userData)


@app.route('/alwaysRight/saveUserIcon')  # need put in
def saveUserIcon():
    Icon = request.files.get('Icon')
    id = session.get('phone')
    path = ".\\static\\Icon\\"
    IconName = Icon.filename
    filePath = path + IconName
    Icon.save(filePath)
    return jsonify(msg='save !')


@app.route('/alwaysRight/getSomethingByUrl')  # need test
def getSomethingByUrl():
    getData = request.get_json()
    url = getData.get("url")

    return send_from_directory('js',url)



@app.route('/alwaysRight/uploadAudio4Score', methods=["POST"])
def upload4Score():
    audio = request.files.get('audio')
    path = ".\\static\\audio\\"
    audioName = audio.filename
    filePath = path + audioName
    userId = session.get('phone')
    audio.save(filePath)
    thisAudioId = WorksMethod.publish_public_work(audioName, filePath, userId)
    thisAudioId2Score = WorksMethod.make_comment(str(thisAudioId))
    data = {
        'id': thisAudioId,
        'score': thisAudioId2Score
    }
    return jsonify(data)


@app.route('/alwaysRight/uploadAudio4text', methods=["POST"])
def upload4text():
    audio = request.files.get('audio')
    path = ".\\static\\audio\\"
    audioName = audio.filename
    filePath = path + audioName
    userId = session.get('phone')
    audio.save(filePath)
    thisAudioId = WorksMethod.publish_public_work(audioName, filePath, userId)  # save id
    thisAudioId2Text = AudioWorkMethod.translate_work(filePath)  # save score
    # WorkMethod.make_score(id)
    data = {
        'id': thisAudioId,
        'text': thisAudioId2Text
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
