import os
import json
import time

from collections import OrderedDict


def json_userData_update(userName_code_match):
    ## 슬랙 봇 최초 실행하거나, 새로운 유저가 들어왔을 때 돌아간다.
    exitence = os.path.isfile("data.json")  ## 파일 있는지 체크
    if exitence == False:  ## 파일이 없다면.
        file_data = OrderedDict()
        file_data["userName_code_match"] = userName_code_match  ## 현재 슬랙에 참여하고 있는 사람들 정보 json에 저장한다.

        with open('data.json', 'w', encoding="utf-8") as make_file:  ## json 파일 작성.
            json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
    else:  ## 파일이 있다면 현재 있는 사람들 데이터만 업데이트.
        ## 파일 데이터 불러온다.
        with open('data.json', encoding="utf-8") as data_file:
            file_data = json.load(data_file, object_pairs_hook=OrderedDict)
            ## 파일 데이터의 userName_code_match만 새로 쓴다 -> 업데이트
            file_data["userName_code_match"] = userName_code_match
        ## json 파일 쓰기.
        with open('data.json', 'w', encoding="utf-8") as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent="\t")


def command_User_Event(command_Number, eventJson):
    userCode = eventJson["user"]
    nowDate = time.strftime('%Y%m%d')
    nowTime = time.strftime('%H%M')
    print(nowDate)

    with open('data.json', encoding="utf-8") as data_file:
        jsonData = json.load(data_file, object_pairs_hook=OrderedDict)

    DM_str = "준비중입니다."
    if command_Number == 0:
        ## 사용자별 오브젝트가 만들어졌는지? 안만들어져있으면 만들어라.
        json_file_user_insert(jsonData, userCode)
        ## 사용자 안에서 오늘날짜 만들어졌는지? 안만들어져있으면 만들자.
        json_file_date_insert(jsonData, userCode, nowDate)

        ## 시작 시간 배열에 넣기.
        insert_juge = json_file_startTime_insert(jsonData, userCode, nowDate, nowTime)
        if insert_juge:
            userName = jsonData["userName_code_match"][userCode]
            strTime = time.strftime("%Y년 %m월 %d일 %H시 %M분")
            DM_str = userName + "님이 " + strTime + "부터 일하는 시간을 체크합니다."
            return DM_str
        else:
            DM_str = "이미 일을 하고 있습니다."
            return DM_str
    elif command_Number == 1:
        insert_juge, exceptionDM = json_file_reststart_insert(jsonData, userCode, nowDate, nowTime)
        if insert_juge:
            userName = jsonData["userName_code_match"][userCode]
            strTime = time.strftime("%Y년 %m월 %d일 %H시 %M분")
            DM_str = userName + "님이 " + strTime + "부터 쉬기 시작했습니다."
            return DM_str
        else:
            DM_str = exceptionDM
            return DM_str
    elif command_Number == 2:
        ## 휴식 정지
        insert_juge, exceptionDM = json_file_restend_insert(jsonData, userCode, nowDate, nowTime)
        if insert_juge:
            userName = jsonData["userName_code_match"][userCode]
            strTime = time.strftime("%Y년 %m월 %d일 %H시 %M분")
            DM_str = userName + "님이 " + strTime + "부터 다시 일하기 시작했습니다."
            return DM_str
        else:
            DM_str = exceptionDM
            return DM_str
    elif command_Number == 3:
        insert_juge, exceptionDM = json_file_workingend_insert(jsonData, userCode, nowDate, nowTime)
        if insert_juge:
            userName = jsonData["userName_code_match"][userCode]
            strTime = time.strftime("%Y년 %m월 %d일 %H시 %M분")
            DM_str = userName + "님이 " + strTime + "에 일하기를 종료했습니다."
            return DM_str
        else:
            DM_str = exceptionDM
            return DM_str
    elif command_Number == 4:
        working_check_DM()
        return DM_str
        pass
    elif command_Number == 5:
        return DM_str
        pass
    elif command_Number == 6:
        return DM_str
    else:
        return DM_str


def json_file_workingend_insert(jsonData, userCode, nowDate, nowTime):
    size = len(jsonData["workingTimeData"][userCode][nowDate])
    if size > 0:
        state = list(jsonData["workingTimeData"][userCode][nowDate][size - 1].keys())[0]
        if state != "workingEndTime":
            workingEndInsert = {"workingEndTime": nowTime}
            jsonData["workingTimeData"][userCode][nowDate].append(workingEndInsert)
            write_json_data(jsonData)
            return True, None
        else:
            return False, "이미 일하는 것을 종료했습니다."
    else:
        return False, "일을 시작 하지 않았습니다."


def json_file_restend_insert(jsonData, userCode, nowDate, nowTime):
    size = len(jsonData["workingTimeData"][userCode][nowDate])
    if size > 0:
        state = list(jsonData["workingTimeData"][userCode][nowDate][size - 1].keys())[0]
        if state == "restStartTime":
            restEndInsert = {"restEndTime": nowTime}
            jsonData["workingTimeData"][userCode][nowDate].append(restEndInsert)
            write_json_data(jsonData)
            return True, None
        else:
            return False, "휴식중이 아닙니다."
    else:
        return False, "일을 시작 하지 않았습니다."


def json_file_reststart_insert(jsonData, userCode, nowDate, nowTime):
    ## 마지막에 일시작, 휴식끝, 워킹체크가 있어야지 쓸수있음.
    ## 휴식시작, 일종료 있거나 일시작이 없으면 쓸수 없음.
    size = len(jsonData["workingTimeData"][userCode][nowDate])
    if size > 0:
        state = list(jsonData["workingTimeData"][userCode][nowDate][size - 1].keys())[0]
        if state == "workingStartTime" or state == "restEndTime" or state == "workingCheckTime":
            restStartInsert = {"restStartTime": nowTime}
            jsonData["workingTimeData"][userCode][nowDate].append(restStartInsert)
            write_json_data(jsonData)
            return True, None
        elif state == "restStartTime":
            exceptionDM = "이미 쉬고 있습니다."
        elif state == "nonResponseTime":
            exceptionDM = "응답이 없어 시간 체크되지 않았습니다.\n 응, yes, y 중에서 입력해주세요."
        elif state == "workingEndTime":
            exceptionDM = "일을 시작하지 않았습니다."
        else:
            exceptionDM = "exceptionDM"

        return False, exceptionDM
    else:
        exceptionDM = "일을 시작하지 않았습니다."
        return False, exceptionDM


def json_file_startTime_insert(jsonData, userCode, nowDate, nowTime):
    ## 일 시작 json 파일 작성.
    size = len(jsonData["workingTimeData"][userCode][nowDate])
    if size == 0:
        startInsert = {"workingStartTime": nowTime}
        jsonData["workingTimeData"][userCode][nowDate].append(startInsert)
        write_json_data(jsonData)
        return True
    else:
        state = list(jsonData["workingTimeData"][userCode][nowDate][size - 1].keys())[0]
        if state == "workingEndTime":
            startInsert = {"workingStartTime": nowTime}
            jsonData["workingTimeData"][userCode][nowDate].append(startInsert)
            write_json_data(jsonData)
            return True
        else:
            return False


def json_file_date_insert(jsonData, userCode, nowDate):
    # 오늘 날짜가 저장되었는지 확인한다.
    if nowDate in jsonData["workingTimeData"][userCode]:
        pass
    else:
        jsonData["workingTimeData"][userCode][nowDate] = []
        ## 추가 하고 파일 데이터 쓰기.
        write_json_data(jsonData)


def json_file_user_insert(jsonData, userCode):
    ## 유저가 저장되었는지 확인한다.
    if userCode in jsonData["workingTimeData"]:
        pass
    else:  ## 유저 데이터가 없을 때.
        jsonData["workingTimeData"][userCode] = {}
        ## 추가 하고 파일 데이터 쓰기.
        write_json_data(jsonData)


def write_json_data(jsonData):
    ## 파일 쓰기.
    with open('data.json', 'w', encoding="utf-8") as make_file:
        json.dump(jsonData, make_file, ensure_ascii=False, indent="\t")


workingCheckList = {}


def working_check_DM():
    ## 마지막 상태에 따라서 DM 날릴지 확인하는 로직.
    nowDate = time.strftime('%Y%m%d')
    with open('data.json', encoding="utf-8") as data_file:
        jsonData = json.load(data_file, object_pairs_hook=OrderedDict)

    for userCode, objectValue in jsonData["workingTimeData"].items():
        print(userCode)
        arrayValue = list(objectValue[nowDate])
        size = len(arrayValue)
        userLastState = list(arrayValue[size - 1].keys())[0]
        userLastTime = list(arrayValue[size - 1].values())[0]
        ## 일시작, 휴식끝, 30분 DM 체크.
        if userLastState == "workingStartTime" or userLastState == "restEndTime" or userLastState == "workingCheckTime":
            workingCheckList[userCode] = userLastTime

    # print(workingCheckList)


def working_time_calculation():
    ## 시간 산출 프로그래밍
    nowDate = time.strftime('%Y%m%d')
    with open('data.json', encoding="utf-8") as data_file:
        jsonData = json.load(data_file, object_pairs_hook=OrderedDict)

    for userCode, objectValue in jsonData["workingTimeData"].items():
        for arrayValue in objectValue[nowDate]:
            print(arrayValue)


