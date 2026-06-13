import json, os, math
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.text import LabelBase

# Android TTS + GPS
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from plyer import gps
    from jnius import autoclass
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

STATIONS = []

def load_stations():
    global STATIONS
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'stations.json')
    with open(path, 'r', encoding='utf-8') as f:
        STATIONS = json.load(f)

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_nearest(lat, lon):
    best = None
    best_d = float('inf')
    for s in STATIONS:
        d = haversine_m(lat, lon, s['la'], s['lo'])
        if d < best_d:
            best_d = d
            best = s
    return best, best_d


class TMVEApp(App):
    def build(self):
        load_stations()
        self.active = False
        self.current_station = ''
        self.log_lines = []
        self.tts = None
        self.lat = None
        self.lon = None

        if platform == 'android':
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])
            ctx = PythonActivity.mActivity
            self.tts = TextToSpeech(ctx, None)
            self.tts.setLanguage(Locale('es', 'ES', ''))

        root = BoxLayout(orientation='vertical', padding=12, spacing=8)

        # Title
        root.add_widget(Label(
            text='📡 TMVE Station Tracker',
            font_size='20sp', bold=True, color=(0.1,0.4,0.8,1),
            size_hint_y=None, height=40))

        self.lbl_status = Label(
            text=f'✅ {len(STATIONS)} estaciones cargadas',
            font_size='14sp', size_hint_y=None, height=30)
        root.add_widget(self.lbl_status)

        self.lbl_gps = Label(
            text='📍 GPS: esperando...',
            font_size='13sp', size_hint_y=None, height=28)
        root.add_widget(self.lbl_gps)

        self.lbl_station = Label(
            text='🔵 Estación: ---',
            font_size='18sp', bold=True, color=(0.05,0.5,0.1,1),
            size_hint_y=None, height=44)
        root.add_widget(self.lbl_station)

        self.lbl_dist = Label(
            text='📏 Distancia: ---',
            font_size='14sp', size_hint_y=None, height=28)
        root.add_widget(self.lbl_dist)

        self.lbl_info = Label(
            text='ℹ️ Region: ---  |  Tipo: ---',
            font_size='13sp', size_hint_y=None, height=28)
        root.add_widget(self.lbl_info)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.btn_start = Button(text='▶ Iniciar', background_color=(0.1,0.4,0.8,1))
        self.btn_start.bind(on_press=self.start_tracking)
        self.btn_stop = Button(text='⏹ Detener', background_color=(0.7,0.1,0.1,1), disabled=True)
        self.btn_stop.bind(on_press=self.stop_tracking)
        btn_row.add_widget(self.btn_start)
        btn_row.add_widget(self.btn_stop)
        root.add_widget(btn_row)

        # Log
        root.add_widget(Label(text='📋 Historial de ruta:',
            font_size='14sp', bold=True, size_hint_y=None, height=28))

        scroll = ScrollView()
        self.lbl_log = Label(
            text='', font_size='12sp',
            size_hint_y=None, halign='left', valign='top')
        self.lbl_log.bind(texture_size=self.lbl_log.setter('size'))
        scroll.add_widget(self.lbl_log)
        root.add_widget(scroll)

        btn_export = Button(text='💾 Exportar log',
            size_hint_y=None, height=44)
        btn_export.bind(on_press=self.export_log)
        root.add_widget(btn_export)

        return root

    def start_tracking(self, *a):
        self.active = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.lbl_status.text = '🟢 Rastreo activo...'
        if platform == 'android':
            gps.configure(on_location=self.on_gps)
            gps.start(minTime=5000, minDistance=20)
        else:
            # Desktop simulation
            Clock.schedule_interval(self.simulate_gps, 5)

    def stop_tracking(self, *a):
        self.active = False
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        self.lbl_status.text = '🔴 Rastreo detenido'
        if platform == 'android':
            gps.stop()

    def on_gps(self, **kwargs):
        self.lat = kwargs.get('lat')
        self.lon = kwargs.get('lon')
        if self.lat and self.lon and self.active:
            Clock.schedule_once(lambda dt: self.update_station(self.lat, self.lon))

    def simulate_gps(self, dt):
        # Demo: Caracas center
        import random
        self.update_station(10.4806 + random.uniform(-0.05,0.05),
                           -66.9036 + random.uniform(-0.05,0.05))

    def update_station(self, lat, lon):
        self.lbl_gps.text = f'📍 {lat:.5f}, {lon:.5f}'
        st, dist = find_nearest(lat, lon)
        if not st:
            return
        nombre = st['n']
        region = st['r']
        tipo = st['t']
        dist_km = dist / 1000

        self.lbl_station.text = f'🔵 {nombre}'
        if dist < 1000:
            self.lbl_dist.text = f'📏 {dist:.0f} m'
        else:
            self.lbl_dist.text = f'📏 {dist_km:.2f} km'
        self.lbl_info.text = f'ℹ️ {region}  |  {tipo}'

        if nombre != self.current_station:
            self.current_station = nombre
            hora = datetime.now().strftime('%H:%M:%S')
            self.log_lines.append(f'{hora} → {nombre}')
            self.lbl_log.text = '\n'.join(self.log_lines[-50:])
            self.speak(f'Estación: {nombre}')

    def speak(self, text):
        if self.tts:
            try:
                self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, None)
            except:
                pass

    def export_log(self, *a):
        if platform == 'android':
            path = '/sdcard/tmve_ruta.txt'
        else:
            path = os.path.join(os.path.expanduser('~'), 'tmve_ruta.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.log_lines))
        self.lbl_status.text = f'💾 Guardado: {path}'


if __name__ == '__main__':
    TMVEApp().run()
