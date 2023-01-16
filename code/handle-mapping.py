# Insert 增大摇杆WS灵敏度，	Home 开关打字，			PageUp 开关轴。			NumPad/ 摇杆居中		NumPad* 开关鼠标平滑		NumPad-+减增不平滑度
# Delete 减小摇杆WS灵敏度，	End 隐藏鼠标到左下角，	PageDown 开关键鼠						
# -= 减小增大摇杆AD灵敏度，	KL 减小增大Shift灵敏度，	<>减小增大Space灵敏度
# 鼠标中键 居中鼠标和转向

from ctypes import *
user32 = windll.user32 # 调用鼠标锁定功能所需库


if starting:

	# 映射vJoy设备号
	v = vJoy[0]
	# vjoy最大轴行程，勿改！
	a_max = 4 + v.axisMax
	a_min = -4 - v.axisMax
	
	jo = joystick[0]

	
	
	#控制器开关/控制
	Val_centAxis_x = 0	# 居中杆量 （后面会映射到目前杆量)
	Val_centAxis_xR = 0
	Val_centAxis_y = 0
	Val_centAxis_yR = 0
	Val_centAxis_z = 0
	Val_centAxis_zR = 0
		
	
	reProjectSensAD = 18 # 灵敏度
	reProjectSensWS = 24
	reProjectSensShift = 5
	reProjectSensShiftCurve = 1
	reProjectSensSpace = 4
	reProjectSensSpaceCurve = 1
	
	reProjectWS = 0 # 重映射杆量
	reProjectAD = 0
	reProjectShift = 0
	reProjectSpace = 0
	
	typEnable = False # 启用打字
	axiEnable = True  # 启用轴
	
	toTypVal = 10000 # 打字所需的vjoy杆量
	
	intervalWS = 25	# 打字间隔
	intervalAD = 25
	intervalSpace = 25
	
	# 键鼠开关
	keyMouseAxis = True # 启用键鼠
	mouselock = False # 光标锁定隐藏
	centerMouse = False # 居中鼠标，归零转向
	
	# 键鼠控制
	pitch_plus = 0 # 键盘辅助俯仰量 (玩无人机模拟器时小一点≈6000，玩战地战雷时 = a_max)
	yaw_plus = 0 # 侧键辅助偏航量 (无人机≈3000)  Liftoff里设置侧键为 重启游戏R 和 更改模式Z 时设为0 					^^^^^^^^^^^^OPTIONAL^^^^^^^^^^^^^^
	yaw_plus_start = 0
	pitch_plus_start = 0
	m_sens = 20 # 鼠标灵敏度，数值越大转向越快
	pitch_axis = 0
	yaw_axis = 0 
	
	mouseSmooth = False
	mouseSmoothSpeed = 5 # 鼠标不平滑度，数值越低越平滑
	mouseSmoothedValX = 0
	mouseSmoothedValY = 0
	mSpeedDifX = 0
	
	# WS AD
	WS_start = 0
	WS_axis = 0
	AD_start = 0
	AD_axis = 0

	"""# 手柄死区（一般不需要，游戏里可以设置）
	var_deadzone = 0.01
	
	var_left_stick_X = filters.deadband(xbox360[0].leftStickX, var_deadzone)
	var_left_stick_Y = filters.deadband(xbox360[0].leftStickY, var_deadzone)
	var_right_stick_X = filters.deadband(xbox360[0].rightStickX, var_deadzone)
	var_right_stick_Y = filters.deadband(xbox360[0].rightStickY, var_deadzone)"""
	
	# 函数
	def limitMinMax(axisVal2):	# 限制最大最小函数
		if axisVal2 > a_max: # 限值写法1
			axisVal2 = a_max
		elif axisVal2 < a_min:
			axisVal2 = a_min
			
	def limitMinMax2(axisVal):	# 限制最大最小函数2
		return (a_max * (axisVal > a_max)) + (a_min * (axisVal < a_min)) # 限值写法2
		

	def reProject(axi, centVal, sens):	# 重映射函数
		reVal = (axi - centVal) * sens
		reVal = a_max  if reVal > a_max  else reVal # 限值写法3
		reVal = a_min  if reVal < a_min  else reVal	# 有需要可增大范围, 如 if reVal > a_max + 2000  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^OPTIONAL^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		return reVal
		
	def reProjectExpo(axi2, centVal2, sens2):	# 曲线映射Shift Space
		reVal2 = abs((axi2 - centVal2) * sens2)** 1.5
		reVal2 = a_max  if reVal2 > a_max  else reVal2 
		reVal2 = a_min  if reVal2 < a_min  else reVal2	
		return reVal2

	def SmoothMouseConstSpeed(moSmVal,moDel,moSmSp):
		if moSmVal < moDel :
			moSmVal += moSmSp
			if moSmVal >= moDel:
				moSmVal = moDel
		if moSmVal > moDel :
			moSmVal -= moSmSp
			if moSmVal <= moDel:
				moSmVal = moDel	
		fiVal = moSmVal
		return fiVal

	def SmoothMouse(moSmVal,moDel,moSmSp):
		if moSmVal < moDel :
			moSmVal += moSmSp * (moDel-moSmVal) * 0.05
			if moSmVal >= moDel:
				moSmVal = moDel
		if moSmVal > moDel :
			moSmVal += moSmSp * (moDel-moSmVal) * 0.05
			if moSmVal <= moDel:
				moSmVal = moDel	
		fiVal = moSmVal
		return fiVal

#======== 键位映射 ========#
# 开关
toggle_keyMouseAxis = keyboard.getPressed(Key.PageDown) # 开关键鼠映射
centerMouse = mouse.getButton(2) #转向回中，鼠标中键(自由视角绑定鼠标，飞行控制绑定vjoy，在战雷自由视角时，鼠标移动不控制飞机,玩战地时请关掉因为自由视角用的不多而JET第三人称后视多)
toggle_mouselock = keyboard.getPressed(Key.End) # 鼠标锁定（隐藏）
toggle_mouseSmooth = keyboard.getPressed(Key.NumberPadStar)# 开关鼠标平滑，用于航拍

# 控制
key_yaw_L = mouse.getButton(4) # 侧键 辅助偏航
key_yaw_R = mouse.getButton(3)
key_Shift = keyboard.getKeyDown(Key.LeftShift) # Shift 辅助俯
key_Space = keyboard.getKeyDown(Key.Space)# 空格 辅助仰

key_W = keyboard.getKeyDown(Key.W) # 油门
key_S = keyboard.getKeyDown(Key.S) # 油门减
key_A = keyboard.getKeyDown(Key.A) # 左翻滚
key_D = keyboard.getKeyDown(Key.D) # 右翻滚


#======== 开关 ========#
if toggle_keyMouseAxis:
	keyMouseAxis = not keyMouseAxis
if toggle_mouselock:
	mouselock = not mouselock
if toggle_mouseSmooth:
	mouseSmooth = not mouseSmooth

#======== 键鼠控制 ========#
if (keyMouseAxis):

	"""if key_yaw_L:	# liftoff里鼠标用侧键 重启比赛 和 切模式 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^OPTIONAL^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		keyboard.setPressed(Key.R)
	if key_yaw_R:
		keyboard.setPressed(Key.Z)"""
	
	if keyboard.getPressed(Key.NumberPadMinus):
		mouseSmoothSpeed -= 1
	if keyboard.getPressed(Key.NumberPadPlus):
		mouseSmoothSpeed += 1
	
	# 鼠标转向X	
	if not mouseSmooth:
		# 直接读取，用于 Race 和 Gunplay
		yaw_axis = (mouse.deltaX * m_sens * 5)	
	else:
		# 平滑模式，用于 航拍
		mouseSmoothedValX = SmoothMouse(mouseSmoothedValX, mouse.deltaX, mouseSmoothSpeed)
		yaw_axis = (mouseSmoothedValX * m_sens * 5)



	#□□□□□□□□□□□□□□□□□□□□□□□□□侧键辅助□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□		我是笨蛋，其实只要 定义两个值 yaw_left 和 yaw_right 就很好写了，我很懒不改了
	#阻尼 线性衰减
	if 	not(key_yaw_R ^ key_yaw_L) and yaw_plus != 0:
		posOrNeg = abs(yaw_plus)/yaw_plus
		yaw_plus = (abs(yaw_plus) - 350)*posOrNeg
		if yaw_plus != 0:
			posOrNeg2 = abs(yaw_plus)/yaw_plus
			if posOrNeg != posOrNeg2:
				yaw_plus = 0	
	#由于条件过于复杂，所以我分两次写好了
	if 	(key_yaw_R and not key_yaw_L and yaw_plus < 0) or (not key_yaw_R and key_yaw_L and yaw_plus > 0):
		posOrNeg = abs(yaw_plus)/yaw_plus
		yaw_plus = (abs(yaw_plus) - 350)*posOrNeg
		if yaw_plus != 0:
			posOrNeg2 = abs(yaw_plus)/yaw_plus
			if posOrNeg != posOrNeg2:
				yaw_plus = 0	
	
	
	"""if not key_yaw_R and not key_yaw_L:	#嫌起步太慢就开启这个
		yaw_plus_start = 300
	if  key_yaw_R and  key_yaw_L:
		yaw_plus_start = 300"""
	
	if key_yaw_R and not key_yaw_L:	# 侧键辅助
		yaw_plus += 600 + yaw_plus_start
		yaw_plus_start = 0
		if yaw_plus >= 6000:
			yaw_plus = 6000
	elif key_yaw_L and not key_yaw_R:
		yaw_plus -= 600 - yaw_plus_start
		yaw_plus_start = 0
		if yaw_plus <= -6000:
			yaw_plus = -6000
	#□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□


	
	
	

	mSpeedDifX = mouse.deltaX - mouseSmoothedValX #监测用

	# 鼠标转向Y
	if not mouseSmooth:
		pitch_axis = (-mouse.deltaY * m_sens * 5)
	else:	
		mouseSmoothedValY = SmoothMouse(mouseSmoothedValY, mouse.deltaY, mouseSmoothSpeed)
		pitch_axis = (mouseSmoothedValY * m_sens * -5)	



	#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■Shift Space 辅助■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
	#阻尼 线性衰减
	if 	not(key_Space ^ key_Shift) and pitch_plus != 0:
		posOrNeg = abs(pitch_plus)/pitch_plus
		pitch_plus = (abs(pitch_plus) - 350)*posOrNeg
		if pitch_plus != 0:
			posOrNeg2 = abs(pitch_plus)/pitch_plus
			if posOrNeg != posOrNeg2:
				pitch_plus = 0	
	#由于条件过于复杂，所以我分两次写好了
	if 	(key_Space and not key_Shift and pitch_plus < 0) or (not key_Space and key_Shift and pitch_plus > 0):
		posOrNeg = abs(pitch_plus)/pitch_plus
		pitch_plus = (abs(pitch_plus) - 350)*posOrNeg
		if pitch_plus != 0:
			posOrNeg2 = abs(pitch_plus)/pitch_plus
			if posOrNeg != posOrNeg2:
				pitch_plus = 0	
	
	
	"""if not key_Space and not key_Shift:	#嫌起步太慢就开启这个
		pitch_plus_start = 300
	if  key_Space and  key_Shift:
		pitch_plus_start = 300"""
	
	if key_Space and not key_Shift:	# 侧键辅助
		pitch_plus += 600 + pitch_plus_start
		pitch_plus_start = 0
		if pitch_plus >= 8000:
			pitch_plus = 8000
	elif key_Shift and not key_Space:
		pitch_plus -= 600 - pitch_plus_start
		pitch_plus_start = 0
		if pitch_plus <= -8000:
			pitch_plus = -8000
	#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

	
	
	


	#óóóóóóóóóóóóóóóóóó极坐标óóóóóóóóóóóóóóóóóóóó     保证右上30°快速移动鼠标时，XY不会同时最大导致右上45°移动视角
	# 只有此摇杆同时控制 Pitch 和 Yaw时才需要，且Pitch Yaw有最大值（非步兵FPS），摇杆值又会超过AxisMax。
	# 如果同时控制Pitch 和 Roll, 或 Throttle 和 Roll, 或 Throttle 和 Yaw 等这些不相关的属性，不要启用这些代码。
	"""if abs(yaw_axis) > a_max and abs(yaw_axis) > abs(pitch_axis):
		pitch_axis = pitch_axis * a_max / abs(yaw_axis)
		yaw_axis = a_max*yaw_axis/abs(yaw_axis)
	elif abs(pitch_axis) > a_max and abs(pitch_axis) > abs(yaw_axis):
		yaw_axis = yaw_axis * a_max / abs(pitch_axis)
		pitch_axis = a_max*pitch_axis/abs(pitch_axis)"""

	yaw_axis += yaw_plus*0.6

	pitch_axis += pitch_plus*0.5


	#======== 鼠标居中 ========#
	if (centerMouse):
		user32.SetCursorPos(1280 , 720) # 鼠标在屏幕上的像素坐标(x, y)，居中鼠标，归零转向，适用2560X1440屏幕	
		pitch_axis = 0
		yaw_axis = 0		
	#======== 鼠标锁定 ========#
	if (mouselock):
		user32.SetCursorPos(100 , 5000) # 鼠标在屏幕上的像素坐标(x, y)

	# WS
	#阻尼
	if 	not(key_W ^ key_S) and WS_axis != 0:
		posOrNeg = abs(WS_axis)/WS_axis
		WS_axis = (abs(WS_axis) - 1500)*posOrNeg
		if WS_axis != 0:
			posOrNeg2 = abs(WS_axis)/WS_axis
			if posOrNeg != posOrNeg2:
				WS_axis = 0
	#由于条件过于复杂，所以我分两次写好了
	if 	(key_W and not key_S and WS_axis < 0) or (not key_W and key_S and WS_axis > 0):
		posOrNeg = abs(WS_axis)/WS_axis
		WS_axis = (abs(WS_axis) - 1500)*posOrNeg
		if WS_axis != 0:
			posOrNeg2 = abs(WS_axis)/WS_axis
			if posOrNeg != posOrNeg2:
				WS_axis = 0


	if not key_W and not key_S:	#嫌起步太慢就开启这个
		WS_start = 1500
	if  key_W and  key_S:
		WS_start = 1500

	if key_W and not key_S:
	    WS_axis += 4000 + WS_start
	    WS_start = 0
	elif key_S and not key_W:
	    WS_axis -= 4000 - WS_start
	    WS_start = 0

	if WS_axis > a_max : # 玩无人机模拟器时限制油门
	    WS_axis = a_max 
	elif WS_axis < a_min :
	    WS_axis = a_min 
	    
	# AD
	#阻尼
	if 	not(key_A ^ key_D) and AD_axis != 0:
		posOrNeg = abs(AD_axis)/AD_axis
		AD_axis = (abs(AD_axis) - 800)*posOrNeg
		if AD_axis != 0:
			posOrNeg2 = abs(AD_axis)/AD_axis
			if posOrNeg != posOrNeg2:
				AD_axis = 0
	#由于条件过于复杂，所以我分两次写好了
	if 	(key_A and not key_D and AD_axis < 0) or (not key_A and key_D and AD_axis > 0):
		posOrNeg = abs(AD_axis)/AD_axis
		AD_axis = (abs(AD_axis) - 800)*posOrNeg
		if AD_axis != 0:
			posOrNeg2 = abs(AD_axis)/AD_axis
			if posOrNeg != posOrNeg2:
				AD_axis = 0

	if not key_A and not key_D:	#嫌起步太慢就开启这个
		AD_start = 800
	if  key_A and  key_D:
		AD_start = 800

	if key_A and not key_D:
	    AD_axis += 1200 + AD_start
	    AD_start = 0
	elif key_D and not key_A:
	    AD_axis -= 1200 - AD_start
	    AD_start = 0

	if AD_axis > a_max - 7000: # 限制滚转
	    AD_axis = a_max - 7000
	elif AD_axis < a_min + 7000:
	    AD_axis = a_min + 7000



#———————摇杆居中———————#

if keyboard.getPressed(Key.NumberPadSlash):
	Val_centAxis_x = jo.x
	Val_centAxis_xR = jo.xRotation
	Val_centAxis_y = jo.y
	Val_centAxis_yR = jo.yRotation
	Val_centAxis_z = jo.z
	Val_centAxis_zR = jo.zRotation
	
	
#=======杆量重映射========#

axiEnable = not axiEnable if keyboard.getPressed(Key.PageUp) else axiEnable

reProjectSensWS += 1 if keyboard.getPressed(Key.Insert) else 0
reProjectSensWS -= 1 if keyboard.getPressed(Key.Delete) else 0
reProjectSensAD += 1 if keyboard.getPressed(Key.Equals) else 0
reProjectSensAD -= 1 if keyboard.getPressed(Key.Minus) else 0
reProjectSensShift += 1 if keyboard.getPressed(Key.L) else 0
reProjectSensShift -= 1 if keyboard.getPressed(Key.K) else 0
reProjectSensSpace += 1 if keyboard.getPressed(Key.Period) else 0
reProjectSensSpace -= 1 if keyboard.getPressed(Key.Comma) else 0
	
if axiEnable:
	reProjectWS = reProject(jo.y, Val_centAxis_y, reProjectSensWS)
	reProjectAD = reProject(jo.x, Val_centAxis_x, reProjectSensAD) * -1
	"""if reProjectWS < 0 :	#降低无人机3D模式反桨速度       	^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^OPTIONAL^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		reProjectWS = reProjectWS * 0.62"""
		
	# 因为Pitch由鼠标控制，游戏中为线性，因此为Space键应用曲线	
	reProjectSensShiftCurve = reProjectSensShift * 0.08	
	reProjectShift = reProjectExpo(jo.xRotation, Val_centAxis_xR, reProjectSensShiftCurve)
	reProjectSensSpaceCurve = reProjectSensSpace * 0.06
	reProjectSpace = reProjectExpo(jo.yRotation, Val_centAxis_yR, reProjectSensSpaceCurve)
	
else:
	reProjectWS=0
	reProjectAD=0
	reProjectShift = 0
	reProjectShift = 0
	
	
#======= 杆量触发 按键/打字 =======#

if keyboard.getPressed(Key.Home):
	typEnable = not typEnable
if typEnable:
	# 重置间隔
	if toTypVal >= reProjectWS >= -toTypVal:
		intervalWS = 25
	if toTypVal >= reProjectAD >= -toTypVal:
		intervalAD = 25
	# 触发按键规则	
	if reProjectWS < -toTypVal:
		keyboard.setPressed(Key.S, intervalWS == 25)
		intervalWS -= 1
		if intervalWS < 1:
			keyboard.setKeyDown(Key.S)
			keyboard.setKeyUp(Key.S)
			intervalWS = 2	
	if reProjectWS > toTypVal:
		keyboard.setPressed(Key.W, intervalWS == 25)
		intervalWS -= 1
		if intervalWS < 1:
			keyboard.setKeyDown(Key.W)
			keyboard.setKeyUp(Key.W)
			intervalWS = 2	

	if reProjectAD < -toTypVal:
		keyboard.setPressed(Key.A, intervalAD == 25)
		intervalAD -= 1
		if intervalAD < 1:
			keyboard.setKeyDown(Key.A)
			keyboard.setKeyUp(Key.A)
			intervalAD = 2	
	if reProjectAD > toTypVal:
		keyboard.setPressed(Key.D, intervalAD == 25) # setPressed 简洁写法 （ 按键，条件 ）
		intervalAD -= 1
		if intervalAD < 1:
			keyboard.setKeyDown(Key.D)
			keyboard.setKeyUp(Key.D)
			intervalAD = 2	
	
	if reProjectShift < toTypVal:
		keyboard.setKeyDown(Key.LeftShift)
		keyboard.setKeyUp(Key.LeftShift)

	if reProjectSpace > toTypVal:
		keyboard.setPressed(Key.Space, intervalWS == 25)
		intervalSpace -= 1
		if intervalSpace < 1:
			keyboard.setKeyDown(Key.Space)
			keyboard.setKeyUp(Key.Space)
			intervalSpace = 2	

#======== vjoy 轴与按钮映射（勿随便修改） ========#
	# 按照rifle aim键位，即反日本手，StickPad主板 x为Roll, zR为油门，xR为Yaw, yR为Pitch
	# 因此为了方便辨认，vjoy同名轴映射StickPad主板同名轴

v.x = int(round(-AD_axis - reProjectAD))
limitMinMax(v.x)
v.y = int(round(-WS_axis + reProjectWS))
limitMinMax(v.rz)

v.rx = int(round(yaw_axis))
v.ry = int(round(pitch_axis + reProjectSpace))
###v.ry = int(round(pitch_axis - reProjectShift + reProjectSpace))
limitMinMax(v.ry)




	#======== 调试 ========#
# 不调试时请注释掉，不然CPU使用率增加50%-80% 
diagnostics.watch(jo.x)
diagnostics.watch(jo.y)
diagnostics.watch(jo.z)
diagnostics.watch(jo.xRotation)
diagnostics.watch(jo.yRotation)
diagnostics.watch(jo.zRotation)


diagnostics.watch(centerMouse) 
diagnostics.watch(keyMouseAxis) # 开关键鼠映射

diagnostics.watch(axiEnable) # 启用轴
diagnostics.watch(typEnable) # 启用打字
diagnostics.watch(intervalWS) # 打字间隔
diagnostics.watch(intervalAD)

diagnostics.watch(m_sens)
diagnostics.watch(mouseSmooth)
diagnostics.watch(mouseSmoothSpeed)

diagnostics.watch(reProjectSensAD)
diagnostics.watch(reProjectSensWS)
diagnostics.watch(reProjectSensShift)
diagnostics.watch(reProjectSensShiftCurve)
diagnostics.watch(reProjectSensSpace)
diagnostics.watch(reProjectSensSpaceCurve)
# 读取航模摇杆和键鼠
diagnostics.watch(AD_axis)

diagnostics.watch(reProjectAD)
diagnostics.watch(v.x)

diagnostics.watch(WS_axis)

diagnostics.watch(reProjectWS)
diagnostics.watch(v.rz)

diagnostics.watch(mouse.deltaX)
diagnostics.watch(mouseSmoothedValX)
diagnostics.watch(mSpeedDifX)

diagnostics.watch(yaw_axis)
diagnostics.watch(v.rx)

diagnostics.watch(mouse.deltaY)
diagnostics.watch(pitch_axis)

diagnostics.watch(reProjectShift)

diagnostics.watch(reProjectSpace)
diagnostics.watch(v.ry)


diagnostics.watch(v.axisMax) # vjoy axis max range



	
	
	
	
	
	
	
	
	
	
	
	
	
	
	