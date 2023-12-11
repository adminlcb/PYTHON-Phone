# -*- coding: UTF-8 -*-
# 导入模块
import log
import utime
import ujson
import audio
import _thread
import checkNet
import voiceCall
from machine import Pin
from machine import Timer

# 官网
# https://python.quectel.com/doc/Getting_started/zh/evb/ec600x-evb.html


# 在执行用户代码前，会先打印这两个变量的值。
PROJECT_NAME = "Grey_Test"
PROJECT_VERSION = "1.0.3"
checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)

# | Parameter | parameter | description               | type     |
# | --------- | --------- | ------------------------- | -------- |
# | CRITICAL  | constant  | value of logging level 50 | critical |
# | ERROR     | constant  | value of logging level 40 | error    |
# | WARNING   | constant  | value of logging level 30 | warning  |
# | INFO      | constant  | value of logging level 20 | info     |
# | DEBUG     | constant  | value of logging level 10 | debug    |
# | NOTSET    | constant  | value of logging level 0  | notset   |

# | 参数      | 参数类型 | 说明                | 类型      |
# | -------- | ------- | ------------------ | -------- |
# | CRITICAL | 常量     | 日志记录级别的数值 50 | critical |
# | ERROR    | 常量     | 日志记录级别的数值 40 | error    |
# | WARNING  | 常量     | 日志记录级别的数值 30 | warning  |
# | INFO     | 常量     | 日志记录级别的数值 20 | info     |
# | DEBUG    | 常量     | 日志记录级别的数值 10 | debug    |
# | NOTSET   | 常量     | 日志记录级别的数值 0  | notset   |
log.basicConfig(level=log.NOTSET)   # 设置日志输出级别
Grey_log = log.getLogger("Grey")

key = Pin(Pin.GPIO12, Pin.IN, Pin.PULL_PD , 1)
key_call = Pin(Pin.GPIO13, Pin.IN, Pin.PULL_PD , 1)
# key_ok = Pin(Pin.GPIO23, Pin.IN, Pin.PULL_PD , 1)
t0Count = 0
	
tts = None
people = 2
str1 = "用户: "
str2 = "来电, 请接听!"
name = ["卢长宝","王蕾","中国移动"]
name_phone = ["17864292401","17806283605","10086"]
# 记录电话簿当前位置
NAME_NUM = 0  
# 记录通话状态 0 待机 1 拨号中 2 来电 3通话中
call_status = 0


# 按键相关定时器 未使用
def timer0_test(t):
	global t0Count
	t0Count = t0Count>=20 and t0Count or t0Count + 1
	print('timer0_test', t0Count)

t0 = Timer(Timer.Timer0)


# # 接听按键回调函数
# def keyok_people():
# 	global tts
# 	print("anxia")
# 	while key_ok.read() == 0:
# 		True   

# 拨号按键回调函数
def call_people(who):
	global tts , call_status
	# 打电话
	if call_status == 0:
		print("打电话"+ name_phone[who])
		# 拨打指定电话
		voiceCall.callStart(name_phone[who])
		tts.stopAll()
		tts.play(4, 0, 2, "正在呼叫"+name[who])
		call_status=1
	# 接电话 
	elif call_status==2:
		voiceCall.callAnswer()
		tts.stopAll()
		call_status=3
	# 已接通 挂电话 
	elif call_status==3:
		print("挂电话")
		tts.stopAll()
		tts.play(4, 0, 2, "已挂断")
		voiceCall.callEnd()
	# 拨号中 挂电话 
	elif call_status==1:
		print("挂电话")
		tts.stopAll()
		tts.play(4, 0, 2, "已挂断")
		voiceCall.callEnd()
		call_status=0
	while key_call.read() == 0:
		True   

# 选择按键回调函数
def key_callback():
	global NAME_NUM,tts
	NAME_NUM+=1
	if NAME_NUM > 2:
		NAME_NUM = 0
	print(name[NAME_NUM])
	tts.play(4, 0, 2, name[NAME_NUM])
	while key.read() == 0:
		True   

# 按键线程
def thread_KEY():
	global NAME_NUM
	while True:
		utime.sleep_ms(20)
		if key.read() ==0 :
			utime.sleep_ms(20)
			if key.read() ==0 :
				key_callback()
		elif key_call.read() ==0 :
			utime.sleep_ms(20)
			if key_call.read() ==0 :
				call_people(NAME_NUM)


# SIM卡电话相关
def dtmf_cb(args):
    print(args)

# 电话回调函数
def voice_callback(args):
	global tts, str1, str2, call_status
	print(args)
	if args[0] == 10:
		print('voicecall incoming call, PhoneNO.: ', args[6])
		str3 = "[n1]"+ args[6][2:-1]
		# 来电
		call_status = 2
		tts.stopAll()
		tts.play(4, 0, 2, str1+str3+str2)
	elif args[0] == 11:
		print('voicecall connected, PhoneNO.: ', args[6])
		# voiceCall.startDtmf("1234567890*#", 1000)   # 设置DTMF音
		#                                             # 参数一: DTMF字符串。最大字符数：32个。有效字符数有：0、1、…、9、A、B、C、D、*、#
		#                                             # 参数二: 持续时间。范围：100-1000；单位：毫秒。
	elif args[0] == 12:
		# 断开
		call_status = 0
		print('voicecall disconnect')
	elif args[0] == 13:
		print('voicecall is waiting, PhoneNO.: ', args[6])
	elif args[0] == 3:
		print('voicecall is waiting, PhoneNO.: ', args[6])
	elif args[0] == 14:
		print('voicecall dialing, PhoneNO.: ', args[6])
	elif args[0] == 15:
		print('voicecall alerting, PhoneNO.: ', args[6])
	elif args[0] == 16:
		print('voicecall holding, PhoneNO.: ', args[6])


if __name__ == "__main__":
	# 手动运行本例程时, 可以去掉该延时, 如果将例程文件名改为main.py, 希望开机自动运行时, 需要加上该延时.
	# utime.sleep(5)
	# CDC口打印poweron_print_once()信息, 注释则无法从CDC口看到下面的poweron_print_once()中打印的信息.
	checknet.poweron_print_once()

	# 如果用户程序包含网络相关代码必须执行wait_network_connected()等待网络就绪(拨号成功).
	# 如果是网络无关代码, 可以屏蔽 wait_network_connected().
	# 注: 未插入SIM卡时函数不会阻塞.
	# stagecode, subcode = checknet.wait_network_connected(120)
	
	stagecode = 3
	subcode = 1
	Grey_log.debug('stagecode: {}   subcode: {}'.format(stagecode, subcode))
	# 网络已就绪: stagecode = 3, subcode = 1
	# 没插sim卡: stagecode = 1, subcode = 0
	# sim卡被锁: stagecode = 1, subcode = 2
	# 超时未注网: stagecode = 2, subcode = 0
	if stagecode != 3 or subcode != 1:
		Grey_log.warning('【Look Out】 Network Not Available\r\n')
	else:
		Grey_log.error('【Look Out】 Network Ready\r\n')

	Grey_log.info('User Code Start\r\n\r\n')

	record = audio.Record()
	record.gain(4, 12)

	tts = audio.TTS(0)
	tts.play(4, 0, 2,"已开机")
	voiceCall.setCallback(voice_callback)  # 注册监听回调函数
	voiceCall.dtmfSetCb(dtmf_cb)  # 设置DTMF识别回调
	voiceCall.dtmfDetEnable(1)  # 使能DTMF音
	# voiceCall.setFw(3, 1, "xxx-xxxx-xxxx")  # 设置控制呼叫转移
	# voiceCall.setChannel(0)  # 切换音频通道
	voiceCall.setVolume(6)  # 设置音量大小, 最大11 
	# voiceCall.getVolume()  # 获取音量大小
	# voiceCall.setAutoRecord(1, 1, 2, "U:/test.amr")  # 自动录音
	# voiceCall.startRecord(0, 2, "U:/test.amr")  # 开启录音
	# oiceCall.stopRecord()  # 结束录音
	voiceCall.setAutoAnswer(30)  # 设置自动应答时间, 单位: S 

	# voiceCall.callStart("10086")  # Grey


	# voiceCall.callAnswer()  # 接听电话
	# voiceCall.callEnd()  # 挂断电话
	# 启动脚本
	Grey_log.info('User Code End\r\n\r\n')
	# 创建按键线程
	_thread.start_new_thread(thread_KEY, ())


