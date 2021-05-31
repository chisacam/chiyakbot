import chatbotmodel
import re
import random
import marketPrice
import checkPickup
import json
import boto3
from inko import Inko

# 전역변수
calc_p = re.compile('^=[0-9+\-*/%!^( )]+')
available_modeltype = ['ipad_pro', 'ipad_air',
                       'ipad_mini', 'ipad_10_2', 'iphone_12',
                       'iphone_12_pro', 'iphone_se', 'iphone_xr',
                       'iphone_11']
myInko = Inko()
comprehend = boto3.client(service_name='comprehend', region_name='ap-northeast-2',
                          aws_access_key_id='AKIA2475NDPROSZBLDGE',
                          aws_secret_access_key='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')
helpText = """/를 붙여서 사용해야하는 기능들

/about 자기소개
/pick 구분자(, | . 등등)과 함께 입력하면 하나를 골라주는 기능

/cp [modelcode?] [modeltype?] 모델코드 입력하면 애플스토어 구매/픽업 가능여부 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델
modeltype이 없으면 기본값은 ipad_pro, 가능한 모델타입은 아래와 같음
{0}

/cpr [modelcode] 모델코드 입력하면 애플스토어 픽업 가능할때 해당 채팅방에 알려주는 기능
modelcode가 없으면 기본값은 5세대 12.9 128 셀룰러 스페이스그레이 모델

/cpd [modelcode] 모델코드 입력하면 픽업 감시 취소
modelcode가 없으면 5세대 12.9 128 셀룰러 스페이스 그레이 예약한것 취소

'='다음에 수식을 쓰면 계산해주는 계산기
ex) =1+1 or =2*2

'확률은?'을 뒤에 붙이면 랜덤확률을 말해주는 기능
ex) 오늘 일론머스크가 또 헛소리할 확률은?

'마법의 소라고둥님'으로 시작하면 그래, 아니중 하나로 대답해주는 소라고둥님
ex) 마법의 소라고둥님 오늘 도지가 화성에 갈까요?
""".format(available_modeltype)

# 유저 chat_id 가져오기


def check_id(update, context):
    try:
        id = update.message.chat.id
        # print(id)
        return id
    except:
        id = update.channel_post.chat.id
        return id

# 유저 닉네임 가져오기


def check_nickname(update, context):
    try:
        nickname = update.message.from_user.first_name
        # print(nickname)
        return nickname
    except:
        nickname = update.channel_post.from_user.first_name
        return nickname

# 도움말 기능


def help_command(update, context):
    id = check_id(update, context)
    chiyak.sendMessage(id, "안녕하세요, " + check_nickname(update,
                       context) + "님. 저는 아래 목록에 있는 일을 할 수 있어요!")
    chiyak.sendMessage(id, helpText)

# 자기소개 기능


def about_command(update, context):
    chiyak.sendMessage(check_id(update, context), "저는 다기능 대화형 봇인 치약봇이에요.")

# 정지 기능


def stop_command(update, context):
    if update.message.from_user.id == 46674072:
        chiyak.sendMessage(check_id(update, context), "안녕히주무세요!")
        chiyak.stop()

# 선택장애 치료 기능


def pick_command(update, context):
    is_correct = update.message.text.split(' ', 1)
    if len(is_correct) <= 1:
        update.message.reply_text(
            '구분자(공백, 콤마 등)를 포함해 /pick 뒤에 써주세요!\nex) /pick 1,2,3,4 or /pick 1 2 3 4')
    else:
        text = is_correct[1]
        text = text.strip()
        if ',' in text:
            picklist = text.split(',')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

        elif ' ' in text:
            picklist = text.split(' ')
            pick = random.choice(picklist)
            update.message.reply_text(pick)

# 채팅방 퇴장 기능


def exit_command(update, context):
    if update.message.from_user.id == 46674072:
        update.message.reply_text("안녕히 계세요!")
        chiyak.core.leave_chat(update.message.chat.id)

# 메세지 삭제 기능


def delMessage_command(update, context):
    if update.message.from_user.id == 46674072:
        target_id = update.message.reply_to_message.message_id
        target_group = update.message.reply_to_message.chat.id
        chiyak.core.deleteMessage(target_group, target_id)

# 메세지 한영변환


def enko_command(update, context):
    if update.message.reply_to_message is not None:
        update.message.reply_text(myInko.en2ko(
            update.message.reply_to_message.text))
    else:
        text = update.message.text.split(' ', 1)
        if len(text) <= 1:
            update.message.reply_text(
                '변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/enko dksl')
        else:
            update.message.reply_text(myInko.en2ko(text[1]))


def koen_command(update, context):
    if update.message.reply_to_message is not None:
        update.message.reply_text(myInko.ko2en(
            update.message.reply_to_message.text))
    else:
        text = update.message.text.split(' ', 1)
        if len(text) <= 1:
            update.message.reply_text(
                '변환하고자 하는 메세지에 답장을 달거나, 명령어 뒤에 변환하고자 하는 문자열을 써주세요!\n ex)/koen ㅗ디ㅣㅐ')
        else:
            update.message.reply_text(myInko.ko2en(text[1]))


def detectSentiment_command(update, context):
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            result = comprehend.detect_sentiment(
                Text=update.message.reply_to_message.text, LanguageCode='ko')
            chiyak.core.sendMessage(
                chat_id=update.message.chat_id,
                text='나빠요' if result['SentimentScore']['Positive'] < result['SentimentScore']['Negative'] else '괜찮아요',
                reply_to_message_id=update.message.reply_to_message.message_id)
        else:
            update.message.reply_text('텍스트에만 사용 해주세요!')
    else:
        update.message.reply_text('원하는 텍스트에 답장을 걸고 사용해주세요!')

# 메세지 감지가 필요한 기능들


def messagedetecter(update, context):
    try:
        # 채팅창 계산기 기능
        is_calc = calc_p.match(update.message.text)
        if is_calc:
            result = eval(update.message.text[1:])
            update.message.reply_text(result)
        else:
            # 확률대답 기능
            if '확률은?' in update.message.text:
                n = random.randint(0, 100)
                update.message.reply_text("{}퍼센트".format(n))

            # 소라고둥님
            if '마법의 소라고둥님' in update.message.text:
                update.message.reply_text(random.choice(['그래.', '아니.']))
    except Exception as e:
        print(e)


chiyak = chatbotmodel.chiyakbot()
chiyak.add_cmdhandler('ds', detectSentiment_command)
chiyak.add_cmdhandler('koen', koen_command)
chiyak.add_cmdhandler('enko', enko_command)
chiyak.add_cmdhandler('cmp', marketPrice.checkMarketPrice_command)
chiyak.add_cmdhandler('cp', checkPickup.checkPickup_command)
chiyak.add_cmdhandler('cpl', checkPickup.checkPickupLoop)
chiyak.add_cmdhandler('cpr', checkPickup.checkPickupRegister)
chiyak.add_cmdhandler('cpd', checkPickup.checkPickupDelete)
chiyak.add_cmdhandler('help', help_command)
chiyak.add_cmdhandler('about', about_command)
chiyak.add_cmdhandler('stop', stop_command)
chiyak.add_cmdhandler('pick', pick_command)
chiyak.add_cmdhandler('exit', exit_command)
chiyak.add_cmdhandler('del', delMessage_command)
chiyak.add_messagehandler(messagedetecter)

chiyak.start()
