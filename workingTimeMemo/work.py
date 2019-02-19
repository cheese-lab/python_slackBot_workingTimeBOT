import os
import re
import time

import json
from collections import OrderedDict
from pprint import pprint
from dataHandling import *

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
            call_juge, command = bot_call_command(event)

            if call_juge:
                ## 정해진 호출을 하고 text 입력했으면 명령어가 유효한지 검사.
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


def bot_call_command(messageJson):
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
    matches = re.search(MENTION_REGEX, messageJson["text"])
    callUserCode = matches.group(1)
    command = matches.group(2)
    userCode = messageJson["user"]
    ## 봇을 호출했는지 검사.
    if starterbot_id == callUserCode:
        return True, command
    else:
        return False, None


##
def define_command_func(command, event):
    ##정해진 명령어로 들어왔는지 검사한다.

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
                     ["5", "오늘피드백", "feedbacktoday", "fbto"],
                     ["6", "전체피드백", "feedbackfull", "fbful"]]
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
        yesDefineCommand = ""
        for cmd in defineCommand[int(command_Number)]:
            yesDefineCommand += (cmd + ", ")

        # select_channel_DM(channel, yesDefineCommand)

        DM_str = command_User_Event(int(command_Number), event)
        select_channel_DM(channel, DM_str)

    elif command == "help":
        ## 없는 명령어 쳤을때 => help 명령어를 쳤을때만나오게..
        notDefineCommand = "다음 중 알맞은 명령 입력하세요\n"
        for cmd in defineCommand:
            for i in cmd:
                notDefineCommand += (i + ", ")
            notDefineCommand += "\n"

        select_channel_DM(channel, notDefineCommand)


def select_channel_DM(channel, massage):
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=massage
    )


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

        json_userData_update(userName_code_match)  ##json 파일이 없으면 생성, 있으면 추가된 유저 입력.

        # print(userName_code_match)

        ## 슬랙봇 시작.
        while True:
            sleck_event_sensing(slack_client.rtm_read())
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")