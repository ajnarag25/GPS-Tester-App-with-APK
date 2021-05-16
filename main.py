from kivy.lang import Builder
from plyer import gps
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

kv = '''
BoxLayout:
    orientation: 'vertical'
    MDToolbar:
        title: "GPS Tester App"
        left_action_items: [["server", lambda x:x]]
        
    MDLabel:
        text: "Welcome User here you can now test your GPS sensor using this app!"
        halign: "center"
    
    MDLabel:
        text: "DISPLAY:"
        halign: "center"
        
    MDLabel:
        text: app.gps_location
        halign: "center"

    MDLabel:
        text: app.gps_status
        halign: "center"

    ToggleButton:
        text: 'Start' if self.state == 'normal' else 'Stop'
        size_hint_x: 0.5
        pos_hint: {'center_x': 0.5,'center_y': 0.5}
        on_state:
            app.start(1000, 0) if self.state == 'down' else \
            app.stop()

    MDBottomNavigation:
        MDBottomNavigationItem:
            name: 'screen 1'
            text: 'Home'
            icon: 'home'
        MDBottomNavigationItem:
            name: 'screen 2'
            text: 'Exit'
            icon: 'exit-to-app'
            on_tab_release: app.exit() 


'''
class GpsTest(MDApp):

    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.

        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_string(kv)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

    def exit(self):
        self.dialog = MDDialog(text="Do you want to exit now?", size_hint=(0.7, 1),
                               buttons=[
                                   MDFlatButton(
                                       text="Yes", on_release=self.eeexit
                                   ), MDFlatButton(
                                       text="No", on_release=self.close
                                   )])

        self.dialog.open()

    def close(self, obj):
        self.dialog.dismiss()

    def eeexit(self, obj):
        exit()


if __name__ == "__main__":
    GpsTest().run()