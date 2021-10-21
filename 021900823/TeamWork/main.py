import re

from flask import Flask, redirect, request, jsonify
import pymysql
import random
import numpy as np
import gamePolicy

conn = pymysql.connect(host="gz-cynosdbmysql-grp-56sj4bjz.sql.tencentcdb.com", user='root', password='Lcx010327',
                       database="software", port=25438)
conn.select_db("software")
cursor = conn.cursor()

app = Flask(__name__)
OpenState = "S1 S2 S3 S4 S5 S6 S7 S8 S9 S10 SJ SQ SK SA S2 " \
            "H1 H2 H3 H4 H5 H6 H7 H8 H9 H10 HJ HQ HK HA H2 " \
            "C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 CJ CQ CK CA C2 " \
            "D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 DJ DQ DK DA D2 "
p = gamePolicy.gamePolicy()


@app.route('/KongoApi', methods=["POST"])
def frame_step():
    getData = request.get_json()
    frame = int(getData.get("frame"))
    print(frame)
    if frame == 0:
        print("抽牌")
    else:
        card = getData.get("place")
        print(card)
    if all([frame]):
        return jsonify(msg="您没有选择是否私密")
    else:
        return jsonify(msg="ok")


@app.route('/KongoApi/StartGame', methods=["POST"])
def startGame():
    getData = request.get_json()
    sql = "insert into TOKEN2ID(ROMTOKEN) values(%s)"
    roomToken = getData.get("roomToken")
    p1ID = getData.get("p1")
    p2ID = getData.get("p2")

    cursor.execute(sql, roomToken)
    rID = rToken2rId(roomToken)
    sql = "insert into room(roomID,drawer,player1Info,player2Info) values (%s,%s,%s,%s)"
    cursor.execute(sql, [rID, OpenState, p1ID, p2ID])

    conn.commit()
    return jsonify(msg="ok")


@app.route('/KongoApi/kongoREG', methods=["POST"])
def kongoREG():
    getData = request.get_json()
    Username = getData.get("Username")
    Password = getData.get("Password")
    NickName = getData.get("NickName")
    sql = "insert into user(userID,Username,Password,Nickname) values (%s,%s,%s,%s)"
    cursor.execute(sql, [1, Username, Password, NickName])
    conn.commit()


@app.route('/KongoApi/frameStep', methods=["POST"])
def frameStep():
    getData = request.get_json()
    op = getData.get("last_code")
    p = getData.get("player")
    rID = getData.get("roomID")
    sql = "select * from room where roomID = %s"
    cursor.execute(sql, rID)
    data = cursor.fetchone()
    drawer = data[5].split(" ")
    player1 = data[6].split(" ")
    player2 = data[7].split(" ")
    room = data[0]
    discard = data[8].split(" ")
    top = data[9]
    if op == 0:
        card = random.choice(drawer)
        drawer.remove(card)
        discard.append(card)
        print(card)
        if top != '' and top[0] == card[0]:
            if p == 1:
                player1.extend(discard)
            else:
                player2.extend(discard)
            discard = ""
            top = ""
        top = card
    else:
        card = getData.get("card")
        discard.append(card)
        if top != '' and top[0] == card[0]:
            if p == 1:
                player1.extend(discard)
                player1.remove(card)
            else:
                player2.extend(discard)
                player2.remove(card)
            discard = ""
            top = ""

        sql = "update room set drawer = %s,player1Card = %s,player2Card = %s,discard = %s,top = %s where roomID = %s"

        drawer = " ".join(str(i) for i in drawer)
        player1 = " ".join(str(i) for i in player1)
        player2 = " ".join(str(i) for i in player2)
        discard = " ".join(str(i) for i in discard)

        print(drawer)
        print(player1, "--", player2, "--", discard, "--", top, "--", room)
        cursor.execute(sql, [drawer, player1, player2, discard, top, room])
        conn.commit()

    return jsonify(msg="ok")


def rToken2rId(roomToken):
    sql = "select * from TOKEN2ID where ROMTOKEN = %s"
    cursor.execute(sql, roomToken)
    res = cursor.fetchone()[0]
    print("进行了转换 ", res)
    return res


def getPolicy(romId, pcSite, lastCard):
    sql = "select * from room where roomID = %s"

    cursor.execute(sql, romId)
    data = cursor.fetchone()
    print(data)  # 五行四列 玩家1 玩家2 棋局牌库 棋牌牌库 弃牌堆顶和次堆顶  pcSite 如果为1 代表电脑是玩家1 为2代表电脑是玩家2
    drawer = data[5].replace(" ", "")
    drawer = re.findall(r'\w{2}', drawer)
    player1 = data[6].replace(" ", "")
    player1 = re.findall(r'\w{2}', player1)
    player2 = data[7].replace(" ", "")
    player2 = re.findall(r'\w{2}', player2)
    room = data[0]
    discard = data[8].replace(" ", "")
    discard = re.findall(r'\w{2}', discard)
    top = data[9]
    rotax = np.zeros((5, 4))
    for i in player1:
        if i[0] == 'S':
            rotax[0][1] += 1
            continue
        if i[0] == 'H':
            rotax[0][0] += 1
            continue
        if i[0] == 'C':
            rotax[0][3] += 1
            continue
        if i[0] == 'D':
            rotax[0][2] += 1
            continue
    for i in player2:
        if i[0] == 'S':
            rotax[1][1] += 1
            continue
        if i[0] == 'H':
            rotax[1][0] += 1
            continue
        if i[0] == 'C':
            rotax[1][3] += 1
            continue
        if i[0] == 'D':
            rotax[1][2] += 1
            continue
    for i in drawer:
        if i[0] == 'S':
            rotax[2][1] += 1
            continue
        if i[0] == 'H':
            rotax[2][0] += 1
            continue
        if i[0] == 'C':
            rotax[2][3] += 1
            continue
        if i[0] == 'D':
            rotax[2][2] += 1
    for i in discard:
        if i[0] == 'S':
            rotax[3][1] += 1
            continue
        if i[0] == 'H':
            rotax[3][0] += 1
            continue
        if i[0] == 'C':
            rotax[3][3] += 1
            continue
        if i[0] == 'D':
            rotax[3][2] += 1
    if top != '':
        if top[0] == 'S':
            rotax[4][0] = 2
        if top[0] == 'H':
            rotax[4][0] = 1
        if top[0] == 'C':
            rotax[4][0] = 4
        if top[0] == 'D':
            rotax[4][0] = 3
    if lastCard[0] == 'S':
        rotax[4][1] = 2
    if lastCard[0] == 'H':
        rotax[4][1] = 1
    if lastCard[0] == 'C':
        rotax[4][1] = 4
    if lastCard[0] == 'D':
        rotax[4][1] = 3
    if pcSite == 2:
        rotax[[0, 1], :] = rotax[[1, 0], :]
    print(rotax)

    ans = p.getRes(rotax)
    print(ans)
    print(np.argmax(ans[0]))


if __name__ == '__main__':
    # app.run(host="0.0.0.0")
    getPolicy(140, 1, "H5")
    cursor.close()
    conn.commit()
    conn.close()
