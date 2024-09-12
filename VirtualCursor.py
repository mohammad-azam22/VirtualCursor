import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import time
import numpy as np
import pyautogui as pag

screen_w, screen_h = pag.size()

detector = HandDetector(detectionCon=0.9, maxHands=1)

source = 0
cap = cv2.VideoCapture(source)
cam_w, cam_h = screen_w//2, screen_h//2

cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
cap.set(cv2.CAP_PROP_FPS, 30)

text = ""

actions = [0, 0, 0, 0, 0, 0]
threshold = 30

while True:
	success, img = cap.read()
	img = cv2.flip(img, 1)

	x1 = pag.center((0, 0, screen_w, screen_h))[0]//3 - (pag.center((0, 0, screen_w, screen_h))[0]//4)
	y1 = pag.center((0, 0, screen_w, screen_h))[1]//3 - (pag.center((0, 0, screen_w, screen_h))[1]//4)
	x2 = pag.center((0, 0, screen_w, screen_h))[0]//3 + (pag.center((0, 0, screen_w, screen_h))[0]//4)
	y2 = pag.center((0, 0, screen_w, screen_h))[1]//4 + (pag.center((0, 0, screen_w, screen_h))[1]//4)

	hands, img = detector.findHands(img, flipType=False)
	cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)	

	if hands:
		lmList = hands[0]["lmList"]
		tmb_x, tmb_y = lmList[4][0], lmList[4][1]
		ind_x, ind_y = lmList[8][0], lmList[8][1]
		mid_x, mid_y = lmList[12][0], lmList[12][1]

		fingers = detector.fingersUp(hands[0])
		handThumb = not fingers[0]
		handIndex = fingers[1]
		handMiddle = fingers[2]
		handRing = fingers[3]
		handPinky = fingers[4]

		# to move mouse
		if handThumb == 0 and handIndex == 1 and handMiddle == 0 and handRing == 0 and handPinky == 0:
			actions = [actions[0], 0, 0, 0, 0, 0]
			if actions[0] > threshold:
				conv_x = int(np.interp(ind_x, (x1, x2), (0, screen_w + 100)))
				conv_y = int(np.interp(ind_y, (y1, y2), (0, screen_h + 100)))
				mouse.move(conv_x, conv_y)
				text = "Move Mouse"
			else:
				actions[0] += 1

		# for left click
		elif handThumb == 1 and handIndex == 1 and handMiddle == 0 and handRing == 0 and handPinky == 0:
			actions = [0, actions[1], 0, 0, 0, 0]
			if actions[1] > threshold:
				mouse.click(button="left")
				mouse.release(button="left")
				text = "Left Click"
				time.sleep(0.5)
			else:
				actions[1] += 1

		# for right click
		elif handThumb == 0 and handIndex == 1 and handMiddle == 1 and handRing == 0 and handPinky == 0:    
			actions = [0, 0, actions[2], 0, 0, 0]
			if actions[2] > threshold:
				mouse.click(button="right")
				mouse.release(button="right")
				text = "Right Click"
				time.sleep(0.5)
			else:
				actions[2] += 1

		elif handThumb == 1 and handIndex == 1 and handMiddle == 1 and handRing == 0 and handPinky == 0:  
			# for scroll up
			if abs(tmb_x - ind_x) <= 30 and abs(ind_x - mid_x) <= 30:
				actions = [0, 0, 0, actions[3], 0, 0]
				if actions[3] > threshold:
					mouse.wheel(delta=1)
					text = "Scroll Up"
				else:
					actions[3] += 1
			
			# for scroll down
			elif abs(tmb_x - ind_x) > 30 and abs(ind_x - mid_x) > 30:
				actions = [0, 0, 0, 0, actions[4], 0]
				if actions[4] > threshold:
					mouse.wheel(delta=-1)
					text = "Scroll Down"
				else:
					actions[4] += 1
		
		# for double left click
		elif handThumb == 0 and handIndex == 1 and handMiddle == 0 and handRing == 0 and handPinky == 1:
			actions = [0, 0, 0, 0, 0, actions[5]]
			if actions[5] > threshold:
				mouse.double_click(button="left")
				mouse.release(button="left")
				text = "Double Left Click"
				time.sleep(0.5)
			else:
				actions[5] += 1
			
		cv2.putText(img, text, (10, 30), 0, 1, (0, 0, 255), 2, 0)
		
	cv2.imshow("Camera Feed", img)
	
	q = cv2.waitKey(1)
	if q==ord("q"):    # press Q to quit
		break

cv2.destroyAllWindows()
cap.release()
