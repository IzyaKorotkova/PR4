from flask import Flask, request, jsonify
import subprocess
app = Flask(__name__)

class ReportElement():
    def __init__(self, deminsion, report):
        self.deminsion = deminsion
        self.report = report
    def addToReport(self, Pid, currStats):
        pass

class ParentElement(ReportElement):
    def addToReport(self, Pid, currStats):
        myStat = currStats[self.deminsion]
        for i in self.report:
            if self.deminsion in i.keys() and i[self.deminsion] == myStat:
                i["Count"] += 1
                return i["Id"]
        else:
            newElement = {"Id": len(self.report),"Pid": None,"URL": None,"SourceIP": None,"TimeInterval": None,"Count": 1}
            newElement[self.deminsion] = myStat
            self.report.append(newElement)
            return newElement["Id"]


class ChildrenElement(ReportElement):
    def addToReport(self, Pid, currStats):
        myStat = currStats[self.deminsion]
        for i in self.report:
            if self.deminsion in i.keys() and i[self.deminsion] == myStat and i["Pid"] == Pid:
                i["Count"] += 1
                return i["Id"]
        else:
            newElement = {"Id": len(self.report),"Pid": Pid,"URL": None,"SourceIP": None,"TimeInterval": None,"Count": 1}
            newElement[self.deminsion] = myStat
            self.report.append(newElement)
            return newElement["Id"]

class ReportsCreater():
    def createReport(self):
        pass

class CreatorForJSON(ReportsCreater):
    def __init__(self, deminsions):
        self.report = list()
        self.report.append(dict())
        self.deminsions = deminsions
    def createReport(self):
        count = int(askDB('HGET', "2", "counter", ""))
        elements = list()
        for j in range(len(self.deminsions)):
            if j == 0:
                elements.append(ParentElement(self.deminsions[j], self.report))
            else:
                elements.append(ChildrenElement(self.deminsions[j], self.report))
        print(count)
        for i in range(count):
            data = askDB('HGET',"2", str(i), '').split(';')
            stats = {"URL": data[0], "SourceIP": data[1], "TimeInterval": data[2]}
            Pid = -1
            for element in elements:
                Pid = element.addToReport(Pid, stats)
        return jsonify(self.report)





def askDB(command, name,arg1, arg2):  #функция для запроса к базе данных
    answer = subprocess.Popen(['go','run','C:\\My\\GO\\Client2\\client.go', command, name, arg1, arg2], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    otvet=str(answer.communicate(str.encode("utf-8"))[0].strip())[2:-1]
    return otvet

@app.route("/", methods=['POST'])
def getStatistic():
    URL = request.form.get("URL")
    SourceIP = request.form.get("SourceIP")
    TimeInterval = request.form.get("TimeInterval")
    coun=askDB('HGET','2','counter','')
    if coun == "Nope":
        askDB('HSET', '2', '0', URL + ';' + SourceIP + ';' + TimeInterval + '\n')
        askDB('HSET','2','counter','1')
    else:
        askDB('HSET', '2', coun, URL + ';' + SourceIP + ';' + TimeInterval + '\n')
        askDB('HSET','2','counter',str(int(coun)+1))
    return "Ok"

@app.route("/report", methods=['POST'])
def backStatistic():
    data = request.get_json()

    creator = CreatorForJSON(data["Dimensions"])
    report = creator.createReport()

    return report

if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = 81)

