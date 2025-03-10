import cv2
import numpy as np
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from flirpy.camera.lepton import Lepton

class CameraApp(App):
   
        def build(self):
            self.layout = BoxLayout(orientation='vertical')
        
            self.image = Image()
            self.layout.add_widget(self.image)
        
            self.button = Button(text='Start Camera', size_hint=(1, 0.2))
            self.button.bind(on_press=self.toggle_camera)
            self.layout.add_widget(self.button)
        
            self.capture = None
            self.is_running = False
        
            return self.layout
    
        def toggle_camera(self, instance):
            with Lepton() as camera:
     
                if self.is_running:
                    self.is_running = False
                    self.button.text = 'Start Camera'
                    Clock.unschedule(self.update)
                else:
                    #camera.setup_video()
                    self.is_running = True
                    self.button.text = 'Stop Camera'
                    Clock.schedule_interval(self.update, 1.0 / 30.0)
    
        def update(self, dt):
            with Lepton() as camera:
                camera.setup_video()
                frame = camera.grab().astype(np.float32)
                frame = cv2.flip(frame, 0)
                buffer = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                buffer = buffer.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
                self.image.texture = texture
                cv2.imshow('image',frame)

if __name__ == '__main__':
    with Lepton() as camera:
        camera.setup_video()
        CameraApp().run()
