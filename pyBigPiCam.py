#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from picamera import PiCamera
import tkinter
import os
import _thread
import traceback

window = tkinter.Tk()
window.geometry("400x100+0+50")
window.title('Big PiCam')

status=tkinter.StringVar(window)
status.set('init')

storage_limit=28
video_base='/media/pi/U'
video_path=video_base+'/Video/'

camera=PiCamera(framerate=42,resolution=(1296,972),sensor_mode=4)
#camera.resolution=(1296,972)
#camera.framerate=41
#camera.framerate_range=(1,42)
#camera.framerate_delta=(1,42)
camera_preview=0
def chang_preview():
	global camera_preview
	global status

	if camera_preview==2:
		camera_preview=0
		camera.stop_preview()
		status.set('stop preview')
	elif camera_preview==1:
		camera_preview=2
		camera.stop_preview()
		camera.start_preview(fullscreen=True)
	else:
		camera_preview=1
		camera.start_preview(fullscreen=False,window=(0,0,240,480))
		status.set('start preview')

chang_preview()

def checksize():
	global video_path
	global storage_limit
	global status

	size=0
	for dirpath, dirname, filename in os.walk(video_path):
		for f in filename:
			size += os.path.getsize(os.path.join(dirpath,f))
	size=size/1048576
	print("Info: files size total: "+str(size))
	start=0
	while (storage_limit*1024<size):
		dir_list = os.listdir(video_path)
		dir_len=len(dir_list)
		if dir_len>1:
			dir_list = sorted(dir_list,  key=lambda x: os.path.getmtime(os.path.join(video_path, x)))
			file_to_delete=video_path+'/'+dir_list[start]
			print("Info: try delete: "+file_to_delete)
			try:
				deletesize=os.path.getsize(os.path.join(file_to_delete))
				os.remove(file_to_delete)
				deletesize=deletesize/1048576
				size=size-deletesize
				print("Info: files deleted, now size total: "+str(size))
				status.set('delete '+file_to_delete)
			except:
				print("Error: delete "+file_to_delete)
				start=start+1
				if start>=dir_len:
					break

recording=0
def cam_loop():
	global recording
	global video_base
	global video_path
	global storage_limit
	global status

	path=video_path
	while True:
		recording=recording+1
		if os.path.exists(path)==False:
			status.set('waiting for mount '+str(recording))
			if recording<10:
				path=video_base+str(recording)+'/Video/'
			else:
				recording=0
				path=video_path
			continue
		video_path=path
		video_file=video_path+'/'+str(recording)+'.h264'
		if os.path.isfile(video_file):
			continue
		print("Info: Record Video to: "+video_file)
		status.set('recording '+video_file)
		camera.start_recording(output=video_file,format='h264',quality=10,level='4.2')
		video_path=path
		checksize()
		camera.wait_recording(60)
		camera.stop_recording()

try:
	_thread.start_new_thread(cam_loop,())
except Exception as e:
	print("Error: unable to start thread")
	print('str(Exception):\t', str(Exception))
	print('str(e):\t\t', str(e))
	print('repr(e):\t', repr(e))
	print('traceback.print_exc():')
	traceback.print_exc()
	print('traceback.format_exc():\n%s' % traceback.format_exc())

b_chang_preview=tkinter.Button(window, text='Preview', command=chang_preview)
b_chang_preview.pack()

l_status=tkinter.Label(window, textvariable=status)
l_status.pack()

window.mainloop()
