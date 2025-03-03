import kivy 

from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.app import App
from kivy.uix.image import Widget
from kivy.uix.button import Button 
from kivy.uix.stacklayout import StackLayout
from kivy.config import Config
from kivy.graphics import *
from kivy.uix.label import Label
from kivy.core.window import Window 

Window.size = (1120,630)

Config.set('graphics', 'resizable', True)

class HomeScreen(App):
	def build(self):
		
		SL = StackLayout(orientation='tb-lr')
		
		btn_setup = Button(text='Set Up/Begin Sensing', font_size = 15, size_hint = (1, .25))
		btn_connection = Button(text='Check Sensor Connection', font_size = 15, size_hint = (1, .25))
		btn_crash = Button(text='Override: Crash', font_size = 15, size_hint = (1, .25))
		btn_no_crash = Button(text='Override: No Crash', font_size = 15, size_hint = (1, .25))
		
		btn_setup.bind(on_press = self.callback)
		
		SL.add_widget(btn_setup)
		SL.add_widget(btn_connection)
		SL.add_widget(btn_crash)
		SL.add_widget(btn_no_crash)
		
		return SL
		
		def callback(self,event):
			print("Set Up/Begin Sensing Pressed")
		
if __name__ == '__main__':
	HomeScreen().run()
