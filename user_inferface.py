from kivy.app import App
from kivy.lang import Builder 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import (ScreenManager, Screen, NoTransition) 

from MultObjTracking.py import FLIRFunc

Builder.load_string("""

<HomeScreen>:
	id: main_win 
    orientation: "vertical"
    spacing: 10
    space_x: self.size[0]/3
  
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
            on_press: root.manager.current = 'setup'
        Button:
            text: 'Check Sensor Connection'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_press: root.manager.current = 'connection'
        Button:
            text: 'Override: Crash'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_press: root.manager.current = 'crash'
        Button:
            text: 'Override: No Crash'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_press: root.manager.current = 'nocrash'
        Button:
            text: 'Stop Sensing'
            font_size: 30
            size_hint: (1, .2)
            background_color: (0.1, .36, .4, .75)
            on_press: root.manager.current = 'stop'

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
            on_press: root.manager.current = 'home'
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
            on_press: root.manager.current = 'home'
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
            on_press: root.manager.current = 'home'
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
            on_press: root.manager.current = 'home'
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
            on_press: root.manager.current = 'home'
""")

# Declare both screens

class HomeScreen(Screen):
    pass

class SetUpScreen(Screen):
    def on_enter(self):
    	print('woooo')
    	FlirFunc()

class ConnectionScreen(Screen):
    pass

class CrashScreen(Screen):
    pass

class NoCrashScreen(Screen):
    pass

class StopScreen(Screen):
    pass


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

        return sm


if __name__ == '__main__':
    FLIRApp().run()
