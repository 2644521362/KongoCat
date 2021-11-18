import pymysql
import json

class Type:

    # 获取全部种类
    def getTypeInfo():
        conn = pymysql.connect(
            host="gz-cynosdbmysql-grp-56sj4bjz.sql.tencentcdb.com",
            user="root",
            port=25438,
            password="Lcx010327",
            database="Hokkien");

        # 创建游标
        cursor = conn.cursor();
        sql = "SELECT * FROM Type"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            jsonData = []
            for row in results:
                result = {}
                result['typeId'] = row[0]
                result['typeName'] = row[1]
                print
                u'转换为列表字典的原始数据：', jsonData
                jsonData.append(result)
            return jsonData
        except:
            print("Error: unable to fetchall TypeInfo")
        else:
            jsondatar = json.dumps(jsonData, ensure_ascii=False)
            return jsondatar[1:len(jsondatar) - 1]

    # 获取类别名
    def getTypeName(typeId):
        conn = pymysql.connect(
            host="gz-cynosdbmysql-grp-56sj4bjz.sql.tencentcdb.com",
            user="root",
            port=25438,
            password="Lcx010327",
            database="Hokkien");

        # 创建游标
        cursor = conn.cursor();
        sql = "SELECT typeName FROM Type WHERE typeId = \""+typeId+"\";";
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            typeName = results[0]
            typeName = typeName[0]
            jsonData = []
            result = {}
            result['typeId'] = typeId
            result['typeName'] = typeName
            jsonData.append(result)
            return jsonData
        except:
            print("Error: unable to fetchall userPrefer")
        else:
            jsondatar = json.dumps(jsonData, ensure_ascii=False)
            return jsondatar[1:len(jsondatar) - 1]

    # 添加类别
    def insertType(typeId, typeName):
        conn = pymysql.connect(
            host="gz-cynosdbmysql-grp-56sj4bjz.sql.tencentcdb.com",
            user="root",
            port=25438,
            password="Lcx010327",
            database="Hokkien");

        # 创建游标
        cursor = conn.cursor();
        sql = "INSERT INTO Type(typeId,typeName) VALUES(\""+typeId+"\",\""+typeName+"\");"
        try:
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            results = Type.getTypeInfo()
            return results
        except:
            print("Error: unable to fetchall userPrefer")
        else:
            jsondatar = json.dumps(jsonData, ensure_ascii=False)
            return jsondatar[1:len(jsondatar) - 1]

    # 删除类别
    def deleteType(typeId):
        conn = pymysql.connect(
            host="gz-cynosdbmysql-grp-56sj4bjz.sql.tencentcdb.com",
            user="root",
            port=25438,
            password="Lcx010327",
            database="Hokkien");

        # 创建游标
        cursor = conn.cursor();
        sql = "DELETE FROM Type WHERE typeId = \""+typeId+"\"";
        try:
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            results = Type.getTypeInfo()
            return results
        except Exception as e:
            print(e)
            print("Error: unable to fetchall userPrefer")


if __name__ == "__main__":
    # Type.insertType("15", "测试")
    print(Type.deleteType("15"))