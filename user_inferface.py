from kivy.app import App
from kivy.lang import Builder 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import (ScreenManager, Screen, NoTransition) 
import cv2
import numpy as np
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from flirpy.camera.lepton import Lepton
from kivy.core.window import Window
from threading import Thread
import threading

from Sensing import SensingApp

global camera
camera = Lepton()
camera.setup_video()
global SApp
SApp = SensingApp()
SApp.get_camera(camera)

class CameraApp(App):
   
        def build(self):
            self.camera = camera
            self.layout = BoxLayout(orientation='vertical')
            self.image = Image()
            self.layout.add_widget(self.image)
            self.button = Button(text='Back to Home Page', size_hint=(1, 0.2))
            self.layout.add_widget(self.button)
            self.capture = None
            self.is_running = False
            return self.layout
        
        def on_start(self):
           self.toggle_camera()
    
        def toggle_camera(self):
            if self.is_running:
                self.is_running = False
                Clock.unschedule(self.update)
            else:
                self.is_running = True
                self.button.bind(on_press=self.back_to_home)
                Clock.schedule_interval(self.update, 1.0 / 30.0)
    
        def back_to_home(self, instance):
            App.get_running_app().stop()
            HomeApp().run()
            
        def update(self, dt):
            x_size = self.image.size[0]
            y_size = self.image.size[1]
            y_size = int(y_size)
            frame = self.camera.grab().astype(np.float32)
            img = 255*(frame - frame.min())/(frame.max()-frame.min())
            img2 = img.astype(np.uint8)
            img3 = cv2.flip(img2, 0)
            img4 = cv2.flip(img3, 1)
            frame_resize = cv2.resize(img4, (x_size, y_size))
            frame2 = cv2.applyColorMap(frame_resize.astype(np.uint8), cv2.COLORMAP_JET)
            buffer = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            buffer = buffer.tobytes()
            texture = Texture.create(size=(frame_resize.shape[1], frame_resize.shape[0]), colorfmt='rgb')
            texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture


Builder.load_string("""

<HomeScreen>:
	#id: main_win 
    #orientation: "vertical"
    #spacing: 10
    #space_x: self.size[0]/3
  
    canvas.before: 
        Color: 
            rgba: (125, 14, 20, 0.74) 
        Rectangle: 
            source:'sts.png'
            size: root.width, root.height 
            pos: self.pos 

    BoxLayout:
        Button:
            text: 'Set Up/Begin Sensing'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'setup'
        Button:
            text: 'FLIR Live Stream'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'stream'
        Button:
            text: 'Check Sensor Connection'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'connection'
        Button:
            text: 'Override: Crash'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'crash'
        Button:
            text: 'Override: No Crash'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'nocrash'
        Button:
            text: 'Stop Sensing'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_release: root.stop_thread()

<SetUpScreen>:
    BoxLayout:
        Button:
            text: 'ROI Selection'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
            on_release: root.roi_setup()
        Button:
            text: 'Back to home screen'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'home'
<ConnectionScreen>:
    BoxLayout:
        Button:
            text: 'My sensor connection button'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
        Button:
            text: 'Back to home screen'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'home'
<CrashScreen>:
    BoxLayout:
        Button:
            text: 'My override crash button'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
        Button:
            text: 'Back to home screen'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'home'
<NoCrashScreen>:
    BoxLayout:
        Button:
            text: 'My override: no crash button'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
        Button:
            text: 'Back to home screen'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
            on_release: root.manager.current = 'home'
""")


class HomeScreen(Screen):
	def stop_thread(self):
		global sensingthread
		if sensingthread.is_alive():
			stop_sensing_event.set()
			sensingthread = None
			print('stopped thread')

class SetUpScreen(Screen):
	def on_enter(self):
		global sensingthread
		sensingthread = Thread(target=threadSensingTarget)
		
	def roi_setup(self):
		global sensingthread
		# if sensingthread is None:
			# sensingthread = Thread(target=threadSensingTarget)
		#if not stop_sensing_event.is_set():
		print('setting up roi')
		#SApp.build()
		if not sensingthread.is_alive():
			SApp.build()
			stop_sensing_event.clear()
			sensingthread.start()
		else:
			if sensingthread is not None and sensingthread.is_alive():
				HomeScreen.stop_thread(self)
				stop_sensing_event.clear()
			SApp.build()
			sensingthread = Thread(target=threadSensingTarget)
			sensingthread.start()
			print('started thread')
			
	
class ConnectionScreen(Screen):
	pass
		
class CrashScreen(Screen):
    pass

class NoCrashScreen(Screen):
    pass
    
class StreamScreen(Screen):
	def on_enter(self):
		CameraApp().run()
		
stop_sensing_event = threading.Event()

def threadSensingTarget():
	print('thread')
	print(stop_sensing_event.is_set())
	while not stop_sensing_event.is_set():
		SApp.update()

class HomeApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager(transition = NoTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SetUpScreen(name='setup'))
        sm.add_widget(ConnectionScreen(name='connection'))
        sm.add_widget(CrashScreen(name='crash'))
        sm.add_widget(NoCrashScreen(name='nocrash'))
        sm.add_widget(StreamScreen(name='stream'))

        return sm


if __name__ == '__main__':
    HomeApp().run()
