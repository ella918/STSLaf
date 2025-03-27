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


#from MultObjTracking.py import FLIRFunc

class CameraApp(App):
   
        def build(self):
            self.camera = Lepton()
            self.camera.setup_video()
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
            FLIRApp().run()
            
            
        def update(self, dt):
            frame = self.camera.grab().astype(np.float32)
            img = 255*(frame - frame.min())/(frame.max()-frame.min())
            img2 = img.astype(np.uint8)
            img3 = cv2.flip(img2, 0)
            frame_resize = cv2.resize(img3, (320,240))
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
            on_release: root.manager.current = 'stop'

<SetUpScreen>:
    BoxLayout:
        Button:
            text: 'my set up button'
            ont_size: 30
            size_hint: (1, .5)
            background_color: (0.1, .36, .4, .75)
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
<StopScreen>:
    BoxLayout:
        Button:
            text: 'My stop sensing button'
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




# Declare both screens

class HomeScreen(Screen):
    pass

class SetUpScreen(Screen):
	pass

class ConnectionScreen(Screen):
    pass

class CrashScreen(Screen):
    pass

class NoCrashScreen(Screen):
    pass

class StopScreen(Screen):
    pass
    
class StreamScreen(Screen):
	def on_enter(self):
		CameraApp().run()


class FLIRApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager(transition = NoTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SetUpScreen(name='setup'))
        sm.add_widget(ConnectionScreen(name='connection'))
        sm.add_widget(CrashScreen(name='crash'))
        sm.add_widget(NoCrashScreen(name='nocrash'))
        sm.add_widget(StopScreen(name='stop'))
        sm.add_widget(StreamScreen(name='stream'))

        return sm


if __name__ == '__main__':
    FLIRApp().run()
