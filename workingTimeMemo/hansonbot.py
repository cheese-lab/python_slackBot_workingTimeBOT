import os
import re
import time

import json
from collections import OrderedDict
from pprint import pprint

from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None  # @botname 으로 호출때문에 필요함.
user_list = None  # 사용자 리스트
userName_code_match = {}  # 사용자 고유 코드와 슬랙대화방에서 사용하는 유저 닉네임 연결.

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "work start"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def sleck_event_sensing(slack_events):
    ## 슬랙에서 발생하는 이벤트 캐치
    for event in slack_events:
        ## bot이 DM 보낸것에는 반능하지 않는다.
        if event["type"] == "message" and (not ("subtype" in event)):
            print("===================================================")
            print(event)  ## 이벤트 json
            ## self_call_command 함수에서 자기 자신 호출했는가?
            self_my_yes, command = self_call_command(event)

            if self_my_yes:
                ## 자기 자신 호출 하고 text 입력했으면 명령어가 유효한지 검사.
                define_command_func(command, event)


def self_call_command(messageJson):
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
    matches = re.search(MENTION_REGEX, messageJson["text"])
    callUserCode = matches.group(1)
    command = matches.group(2)
    userCode = messageJson["user"]
    ## 자기 자신 호출했는지 검사.
    if userCode == callUserCode:
        return True, command
    else:
        return False, None


def define_command_func(command, event):
    ## 커멘드에서 모든 공백 제거
    command = command.replace(" ", "")
    ## 채널 코드
    channel = event["channel"]

    allFeedBackCode = "ssh9492"
    ## 명령어 인정 범위 집합.
    defineCommand = [["0", "일시작", "workstart", "ws"],
                     ["1", "휴식시작", "reststart", "rs"],
                     ["2", "휴식끝", "restend", "re"],
                     ["3", "일종료", "workend", "we"],
                     ["4", "응", "yes", "y"],
                     ["5", "오늘피드백", "todayfeedback", "tofb"],
                     ["6", "전체피드백", "fullfeedback", "fulfb"]]
    command_juge = False
    command_Number = None

    for cmd in defineCommand:
        if command in cmd:
            print(cmd[0])
            command_Number = cmd[0]
            command_juge = True
            break

    if command_juge:
        ## 기능 있을 때.
        print(defineCommand[int(command_Number)])
    else:
        ## 없는 명령어 쳤을때
        notDefineCommand = "다음 중 알맞은 명령 입력하세요\n"
        for cmd in defineCommand:
            for i in cmd:
                notDefineCommand += (i + ", ")
            notDefineCommand += "\n"

        select_channel_DM(channel, notDefineCommand)

        print(defineCommand)


def select_channel_DM(channel, massage):
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=massage
    )


def json_userData_update():
    exitence = os.path.isfile("data.json")
    if exitence == False:
        file_data = OrderedDict()
        file_data["userName_code_match"] = userName_code_match

        with open('data.json', 'w', encoding="utf-8") as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
    else:
        with open('data.json', encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        data["userName_code_match"] = userName_code_match

        with open('data.json', 'w', encoding="utf-8") as make_file:
            json.dump(data, make_file, ensure_ascii=False, indent="\t")


if __name__ == "__main__":

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        ## 슬랙 채널 정보, 봇 아이디, 유저 정보
        channel_list = slack_client.api_call("channels.list")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        user_list = slack_client.api_call("users.list")

        ## 유저 코드와 유저 리얼 이름과 매칭
        for user in user_list["members"]:
            userName_code_match[user["id"]] = user["profile"]["real_name_normalized"]

        json_userData_update()  ##json 파일이 없으면 생성, 있으면 추가된 유저 입력.

        print(userName_code_match)

        while True:
            sleck_event_sensing(slack_client.rtm_read())
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")