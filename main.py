import json
import os
import calendar
from datetime import date, datetime
import os
os.environ["KIVY_WINDOW"] = "sdl2"

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.axes import XValueAxis, YCategoryAxis
from reportlab.graphics import renderPDF

from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label



# ==========================================
# 🎨 SISTEMA DE DISEÑO (TEMA CENTRALIZADO)
# ==========================================
THEME = {
    "bg_app": (0.07, 0.09, 0.15, 1),       # Fondo general de pantalla (#121726)
    "bg_card": (0.13, 0.17, 0.26, 1),      # Fondo de tarjetas (#212B42)
    "bg_input": (0.18, 0.23, 0.34, 1),     # Fondo para campos de texto
    "primary": (0.06, 0.72, 0.51, 1),      # Verde esmeralda (#10B981)
    "accent": (0.31, 0.82, 0.77, 1),
    "text_main": (0.95, 0.96, 0.98, 1),    # Blanco suave (#F2F5FA)
    "text_muted": (0.60, 0.66, 0.76, 1),   # Gris secundario
    "danger": (0.93, 0.27, 0.27, 1),       # Rojo para devoluciones
    "radius": [dp(12)]                     # Radio de bordes redondeados
}

# ==========================================
# 🧩 COMPONENTE BASE: TARJETA REDONDEADA
# ==========================================
class CardWidget(BoxLayout):
    """Contenedor elegante que sustituye a los BoxLayout planos."""
    def __init__(self, bg_color=THEME["bg_card"], radius=THEME["radius"], **kwargs):
        super().__init__(**kwargs)
        self.padding = [dp(14), dp(14)]
        self.spacing = dp(8)
        
        with self.canvas.before:
            self.canvas_color = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size



class KPICard(CardWidget):
    """Tarjeta KPI rediseñada, adaptada a la estética moderna y 100% compatible."""

    def __init__(
        self,
        titulo,
        valor,
        color_bg=THEME["bg_card"],
        color_texto=THEME["text_main"],
        **kwargs,
    ):
        # Hereda de CardWidget respetando el color de fondo personalizado si se recibe
        super().__init__(bg_color=color_bg, orientation="vertical", **kwargs)
        
        self.padding = [dp(14), dp(6)]
        self.spacing = dp(4)

        # 1. Título (Alineado a la izquierda para un look más moderno y limpio)
        self.lbl_titulo = Label(
            text=str(titulo).upper(),
            font_size=sp(12),
            bold=True,
            color=THEME["text_muted"],
            size_hint_y=0.30,
            halign="left",
            valign="middle",
        )
        self.lbl_titulo.bind(size=self.lbl_titulo.setter("text_size"))

        # 2. Valor Principal (Tipografía proporcional sp)
        self.lbl_valor = Label(
            text=str(valor),
            font_size=sp(30),
            bold=True,
            color=color_texto,
            size_hint_y=0.70,
            halign="right",
            valign="middle",
        )
        self.lbl_valor.bind(size=self.lbl_valor.setter("text_size"))

        self.add_widget(self.lbl_titulo)
        self.add_widget(self.lbl_valor)

    def actualizar(self, valor, color_texto=None):
        """Permite actualizar el contenido desde la lógica sin rehacer el widget."""
        self.lbl_valor.text = str(valor)
        if color_texto:
            self.lbl_valor.color = color_texto



class GraficaVentas(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ventas = [0] * 31
        self.color_barras = (1, 0.85, 0.2, 1)
        self.bind(pos=self.redibujar, size=self.redibujar)

    def redibujar(self, *args):
        self.canvas.clear()
        ancho_columna = self.width / 31

        if hasattr(self, "objetivo_ticket"):
            maximo = max(max(self.ventas), self.objetivo_ticket)
        else:
            maximo = max(self.ventas)

        if maximo <= 0:
            maximo = 1

        if hasattr(self, "objetivo_ticket"):
            altura_objetivo = (self.objetivo_ticket / maximo) * (self.height * 0.90)
        else:
            altura_objetivo = None

        with self.canvas:
            # Marco
            Color(0.75, 0.75, 0.75, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

            # Rejilla
            Color(0.88, 0.88, 0.88, 1)
            for i in range(1, 5):
                y = self.y + (self.height * i / 5)
                Line(points=[self.x, y, self.x + self.width, y], width=1)

            for dia in (5, 10, 15, 20, 25, 30):
                x = self.x + (dia * ancho_columna)
                Line(points=[x, self.y, x, self.y + self.height], width=1)

            if altura_objetivo is not None:
                Color(0.2, 0.6, 1, 1)
                Line(
                    points=[
                        self.x,
                        self.y + altura_objetivo,
                        self.x + self.width,
                        self.y + altura_objetivo,
                    ],
                    width=2,
                )

            # Barras
            ancho_barra = ancho_columna * 0.60
            for i, venta in enumerate(self.ventas):
                if hasattr(self, "objetivo_ticket"):
                    if venta >= self.objetivo_ticket:
                        Color(0.2, 0.8, 0.3, 1)
                    elif venta >= (self.objetivo_ticket * 0.8):
                        Color(1, 0.8, 0, 1)
                    else:
                        Color(1, 0.2, 0.2, 1)
                else:
                    Color(*self.color_barras)

                altura = (venta / maximo) * (self.height * 0.90)
                x = self.x + i * ancho_columna + (ancho_columna - ancho_barra) / 2
                Rectangle(pos=(x, self.y), size=(ancho_barra, altura))

            # Etiquetas inferiores
            Color(1, 1, 1, 1)
            for dia in (1, 5, 10, 15, 20, 25, 31):
                etiqueta = CoreLabel(text=str(dia), font_size=11)
                etiqueta.refresh()
                textura = etiqueta.texture
                x = self.x + (dia - 0.5) * ancho_columna - textura.width / 2
                Rectangle(texture=textura, pos=(x, self.y - 18), size=textura.size)


class GraficaTicketMedio(GraficaVentas):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_barras = (0.2, 0.8, 0.3, 1)
        self.objetivo_ticket = 75


class GraficaEquipo(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombres = []
        self.ventas = []
        self.bind(pos=self.redibujar, size=self.redibujar)

    def redibujar(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.75, 0.75, 0.75, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

            Color(0.88, 0.88, 0.88, 1)
            for i in range(1, 5):
                y = self.y + (self.height * i / 5)
                Line(points=[self.x, y, self.x + self.width, y], width=1)

            if len(self.ventas) == 0:
                return

            maximo = max(self.ventas)
            if maximo <= 0:
                maximo = 1

            ancho_columna = self.width / len(self.ventas)
            ancho_barra = ancho_columna * 0.60

            Color(0.2, 0.6, 1, 1)
            for i, venta in enumerate(self.ventas):
                altura = (venta / maximo) * (self.height * 0.90)
                x = self.x + i * ancho_columna + (ancho_columna - ancho_barra) / 2
                Rectangle(pos=(x, self.y), size=(ancho_barra, altura))

            Color(1, 1, 1, 1)
            for i, nombre in enumerate(self.nombres):
                etiqueta = CoreLabel(text=str(nombre), font_size=18)
                etiqueta.refresh()
                textura = etiqueta.texture
                x = self.x + (i + 0.5) * ancho_columna - textura.width / 2
                Rectangle(texture=textura, pos=(x, self.y - 18), size=textura.size)


class GraficaObjetivo(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objetivo = 0
        self.venta = 0
        self.cumplimiento = 0
        self.bind(pos=self.redibujar, size=self.redibujar)

    def redibujar(self, *args):
        self.canvas.clear()
        maximo = max(self.objetivo, self.venta, 1)

        with self.canvas:
            ancho_maximo = self.width - 80

            Color(0.20, 0.45, 0.90, 1)
            Rectangle(pos=(self.x + 40, self.y + 150), size=(ancho_maximo, 25))

            ancho = ancho_maximo * self.venta / maximo
            Color(1, 0.85, 0.20, 1)
            Rectangle(pos=(self.x + 40, self.y), size=(ancho, 25))

            titulo = CoreLabel(text="VENTA", font_size=28)
            titulo.refresh()
            Rectangle(
                texture=titulo.texture,
                pos=(self.x + 35, self.y + 35),
                size=titulo.texture.size,
            )

            importe = CoreLabel(text=f"{self.venta:.2f} €", font_size=24)
            importe.refresh()
            Rectangle(
                texture=importe.texture,
                pos=(self.x + 40, self.y - 35),
                size=importe.texture.size,
            )

            titulo = CoreLabel(text="OBJETIVO", font_size=28)
            titulo.refresh()
            Rectangle(
                texture=titulo.texture,
                pos=(self.x + 40, self.y + 180),
                size=titulo.texture.size,
            )

            importe = CoreLabel(text=f"{self.objetivo:.2f} €", font_size=24)
            importe.refresh()
            Rectangle(
                texture=importe.texture,
                pos=(self.x + 40, self.y + 115),
                size=importe.texture.size,
            )

            texto = CoreLabel(
                text=f"Cumplimiento diario: {self.cumplimiento:.2f} %", font_size=26
            )
            texto.refresh()
            Rectangle(
                texture=texto.texture,
                pos=(self.x + 40, self.y - 100),
                size=texto.texture.size,
            )

class ViyuvaApp(App):
    ventas = []

    def abrir_nuevo_dia(self):
        # Layout principal con espaciados proporcionales y padding
        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))

        # Estilo reutilizable para las etiquetas
        def crear_label_campo(texto):
            lbl = Label(
                text=texto,
                font_size=sp(11),
                bold=True,
                color=THEME["text_muted"],
                size_hint_y=None,
                height=dp(20),
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter('text_size'))
            return lbl

        # Estilo reutilizable para los inputs de una línea
        def crear_input_linea(multiline=False, text="", hint_text=""):
            return TextInput(
                text=text,
                hint_text=hint_text,
                multiline=multiline,
                font_size=sp(14),
                size_hint_y=None,
                height=dp(42) if not multiline else dp(70),
                background_normal='',
                background_color=THEME["bg_input"],
                foreground_color=THEME["text_main"],
                hint_text_color=THEME["text_muted"],
                cursor_color=THEME["primary"],
                padding=[dp(10), dp(10)]
            )

        # 1. FECHA
        layout.add_widget(crear_label_campo("FECHA"))
        fecha_inicial = str(date.today())
        self.entry_fecha = crear_input_linea(
                text=fecha_inicial
        )

        self.entry_fecha.bind(
                focus=self.actualizar_fecha_popup
        )

        self.entry_fecha.bind(
                on_text_validate=lambda x: setattr(
                        self.entry_clientes,
                        "focus",
                        True,
                )
        )
        layout.add_widget(self.entry_fecha)

        # 2. CLIENTES
        layout.add_widget(crear_label_campo("CLIENTES"))
        self.entry_clientes = crear_input_linea()
        self.entry_clientes.bind(
            on_text_validate=lambda x: setattr(self.entry_objetivo, "focus", True)
        )
        layout.add_widget(self.entry_clientes)

        # 3. OBJETIVO MES
        layout.add_widget(crear_label_campo("OBJETIVO MES"))
        self.entry_objetivo = crear_input_linea()
        self.entry_objetivo.bind(
            on_text_validate=lambda x: setattr(self.combo_clima, "focus", True)
        )
        layout.add_widget(self.entry_objetivo)

        # 4. CLIMA
        layout.add_widget(crear_label_campo("CLIMA"))
        self.combo_clima = crear_input_linea(hint_text="Clima o incidencia del día")
        self.combo_clima.bind(
            on_text_validate=lambda x: setattr(self.entry_observaciones, "focus", True)
        )
        layout.add_widget(self.combo_clima)

        # 5. OBSERVACIONES
        layout.add_widget(crear_label_campo("OBSERVACIONES"))
        self.entry_observaciones = crear_input_linea(multiline=True)
        layout.add_widget(self.entry_observaciones)

        # BOTONES
        botones = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(10)
        )
        
        btn_volver = Button(
            text="CERRAR",
            background_normal='',
            background_color=THEME["bg_card"],
            color=THEME["text_muted"],
            bold=True,
            font_size=sp(14)
        )
        btn_volver.bind(on_press=self.cerrar_popup_nuevo_dia)

        btn_guardar = Button(
            text="GUARDAR",
            background_normal='',
            background_color=THEME["primary"],
            color=THEME["text_main"],
            bold=True,
            font_size=sp(14)
        )
        btn_guardar.bind(on_press=self.guardar_config)

        botones.add_widget(btn_volver)
        botones.add_widget(btn_guardar)
        layout.add_widget(botones)

        # Cargar Objetivo por defecto
        objetivo = (
            self.obtener_objetivo_mes(self.entry_fecha.text)
            if hasattr(self, "obtener_objetivo_mes")
            else 0.0
        )

        if objetivo > 0:
            self.entry_objetivo.text = str(objetivo)

        # --- MOSTRAR DATOS SI EL DÍA YA EXISTE EN JSON ---
        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias_existentes = json.load(f)
            for d in dias_existentes:
                if d.get("fecha") == fecha_inicial:
                    
                    if d.get("clientes", 0) > 0:
                        self.entry_clientes.text = str(d["clientes"])
                    if d.get("objetivo_mes", 0) > 0:
                        self.entry_objetivo.text = str(d["objetivo_mes"])
                    self.combo_clima.text = str(d.get("clima", ""))
                    self.entry_observaciones.text = str(d.get("observaciones", ""))
                    break
        except Exception:
            pass

        self.popup_nuevo_dia = Popup(
            title="Nuevo Día", content=layout, size_hint=(0.95, 0.95), auto_dismiss=False
        )
        self.popup_nuevo_dia.open()

    def guardar_config(self, instance):
        fecha_ingresada = self.entry_fecha.text.strip()
        self.fecha_actual = fecha_ingresada

        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias = json.load(f)
        except Exception:
            dias = []

        dia_existente = None
        for d in dias:
            if d.get("fecha") == fecha_ingresada:
                dia_existente = d
                break

        txt_clts = self.entry_clientes.text.strip()
        if txt_clts.isdigit() and int(txt_clts) > 0:
            clientes_val = int(txt_clts)
        elif dia_existente and "clientes" in dia_existente:
            clientes_val = dia_existente["clientes"]
        else:
            clientes_val = 0

        txt_obj = self.entry_objetivo.text.strip()
        if txt_obj:
            try:
                objetivo_val = float(txt_obj)
            except ValueError:
                objetivo_val = (
                    dia_existente.get("objetivo_mes", 0.0) if dia_existente else 0.0
                )
        else:
            objetivo_val = (
                dia_existente.get("objetivo_mes", 0.0) if dia_existente else 0.0
            )

        datos = {
            "fecha": fecha_ingresada,
            "clientes": clientes_val,
            "objetivo_mes": objetivo_val,
            "clima": self.combo_clima.text,
            "observaciones": self.entry_observaciones.text,
        }

        if dia_existente:
            dia_existente.update(datos)
        else:
            dias.append(datos)
            if txt_obj:

                for d in dias:

                        try:

                                fecha_d = datetime.strptime(
                                        d["fecha"],
                                        "%Y-%m-%d"
                                )

                                fecha_actual = datetime.strptime(
                                        fecha_ingresada,
                                        "%Y-%m-%d"
                                )

                                if (
                                        fecha_d.month == fecha_actual.month
                                        and
                                        fecha_d.year == fecha_actual.year
                                ):

                                        d["objetivo_mes"] = objetivo_val

                        except Exception:

                                pass
            

        with open("dias.json", "w", encoding="utf-8") as f:
            json.dump(dias, f, indent=4, ensure_ascii=False)

        self.popup_nuevo_dia.dismiss()

    def cerrar_popup_nuevo_dia(self, instance):
        self.popup_nuevo_dia.dismiss()
    def actualizar_fecha_popup(
            self,
            instancia,
            tiene_foco,
    ):

        if tiene_foco:
            return

        fecha = self.entry_fecha.text.strip()

        self.entry_clientes.text = ""
        self.entry_objetivo.text = ""
        self.combo_clima.text = ""
        self.entry_observaciones.text = ""

        objetivo = self.obtener_objetivo_mes(fecha)

        if objetivo > 0:

                self.entry_objetivo.text = str(objetivo)

        try:

                with open(
                        "dias.json",
                        "r",
                        encoding="utf-8",
                ) as f:

                        dias = json.load(f)

                for d in dias:

                        if d.get("fecha") == fecha:

                                if d.get("clientes", 0) > 0:
                                        self.entry_clientes.text = str(
                                                d["clientes"]
                                        )

                                if float(
                                        d.get("objetivo_mes", 0)
                                ) > 0:

                                        self.entry_objetivo.text = str(
                                                d["objetivo_mes"]
                                        )

                                self.combo_clima.text = str(
                                        d.get("clima", "")
                                )

                                self.entry_observaciones.text = str(
                                        d.get(
                                                "observaciones",
                                                "",
                                        )
                                )

                                break

        except Exception:

                pass

    def obtener_objetivo_mes(self, fecha):
        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias = json.load(f)
        except Exception:
            return 0.0

        try:
            # Asegurar formato estándar YYYY-MM-DD
            fecha_str = str(fecha).split(" ")[0].split("T")[0]
            fecha_busqueda = datetime.strptime(fecha_str, "%Y-%m-%d")
        except Exception:
            return 0.0

        # 1º INTENTO: Buscar la fecha exacta consultada con un objetivo mayor a 0
        for dia in dias:
            if dia.get("fecha") == fecha_str and float(dia.get("objetivo_mes", 0.0)) > 0:
                return float(dia["objetivo_mes"])

        # 2º INTENTO: Buscar cualquier día del MISMO MES Y AÑO que tenga un objetivo guardado
        for dia in dias:
            try:
                f_dia_str = str(dia.get("fecha", "")).split(" ")[0].split("T")[0]
                fecha_dia = datetime.strptime(f_dia_str, "%Y-%m-%d")
                if (
                    fecha_dia.month == fecha_busqueda.month
                    and fecha_dia.year == fecha_busqueda.year
                ):
                    obj = float(dia.get("objetivo_mes", 0.0))
                    if obj > 0:
                        return obj
            except Exception:
                continue

        return 0.0
        


        for dia in dias:
            try:
                fecha_dia = datetime.strptime(dia["fecha"], "%Y-%m-%d")
                if (
                    fecha_dia.month == fecha_busqueda.month
                    and fecha_dia.year == fecha_busqueda.year
                ):
                    return float(dia["objetivo_mes"])
            except Exception:
                continue

        return 0.0
    
    def crear_tarjeta(self, titulo, valor, color=None):
        if color is None:
            color_texto = THEME["primary"]
        else:
            color_texto = color

        tarjeta = CardWidget(orientation="vertical", size_hint_y=None, height=dp(130))
        
        titulo_label = Label(
            text=str(titulo).upper(),
            font_size=sp(12),
            bold=True,
            color=THEME["text_muted"],
            halign="center",
            valign="middle",
        )
        titulo_label.bind(
            size=lambda instance, value: setattr(instance, "text_size", value)
        )

        valor_label = Label(
            text=str(valor),
            font_size=sp(28),
            bold=True,
            color=THEME["text_main"],
            halign="center",
            valign="middle",
        )
        valor_label.bind(
            size=lambda instance, value: setattr(instance, "text_size", value)
        )

        tarjeta.add_widget(titulo_label)
        tarjeta.add_widget(valor_label)
        return tarjeta

    def crear_titulo(self, texto, color=None):
        return Label(
            text=str(texto).upper(),
            font_size=sp(18),
            bold=True,
            color=THEME["text_main"],
            size_hint_y=None,
            height=dp(50),
            halign="center",
            valign="middle",
        )

        
    def abrir_dashboard(self, instance):
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except Exception:
            ventas = []

        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias = json.load(f)
        except Exception:
            dias = []

        fecha_act = getattr(self, "fecha_actual", str(date.today()))
        try:
            fecha_act_dt = datetime.strptime(fecha_act, "%Y-%m-%d")
        except Exception:
            fecha_act_dt = datetime.now()

        venta_neta = 0.0
        articulos_totales = 0
        tickets = 0
        ventas_dependiente = {}
        tickets_dependiente = {}
        articulos_dependiente = {}
        clientes = 0

        for venta in ventas:
            if not isinstance(venta, dict):
                continue

            fecha_v_str = venta.get("fecha", "")
            try:
                f_v = datetime.strptime(fecha_v_str, "%Y-%m-%d")
            except Exception:
                continue

            if f_v.year != fecha_act_dt.year or f_v.month != fecha_act_dt.month:
                continue
            if f_v > fecha_act_dt:
                continue

            vendedor = venta.get("vendedor", "Sin Nombre")

            # LECTURA A PRUEBA DE ERRORES DE IMPORTE Y ARTÍCULOS
            try:
                importe = float(
                    str(venta.get("importe", 0)).replace(",", ".").strip()
                )
            except (ValueError, TypeError):
                importe = 0.0

            try:
                articulos = int(
                    float(
                        str(venta.get("articulos", 0)).replace(",", ".").strip()
                    )
                )
            except (ValueError, TypeError):
                articulos = 0

            venta_neta += importe
            articulos_totales += articulos
            tickets += 1

            if vendedor not in ventas_dependiente:
                ventas_dependiente[vendedor] = 0.0
                tickets_dependiente[vendedor] = 0
                articulos_dependiente[vendedor] = 0

            ventas_dependiente[vendedor] += importe
            tickets_dependiente[vendedor] += 1
            articulos_dependiente[vendedor] += articulos


        ticket_medio = (venta_neta / tickets) if tickets > 0 else 0.0
        upt = (articulos_totales / tickets) if tickets > 0 else 0.0

        for dia in dias:
            if dia.get("fecha") == fecha_act:
                clientes = int(dia.get("clientes", 0) or 0)
                break

        # Aseguramos que fecha_act esté limpia (solo YYYY-MM-DD)
        fecha_act_limpia = str(fecha_act).split(" ")[0].split("T")[0]
        
        # Obtenemos el objetivo del mes consultado
        objetivo = self.obtener_objetivo_mes(fecha_act_limpia)
        
        restante_objetivo = max(0.0, objetivo - venta_neta)
        cumplimiento = ((venta_neta / objetivo) * 100) if objetivo > 0 else 0.0


        popup = Popup(
            title=f"DASHBOARD A36 MADRID - ({fecha_act})",
            size_hint=(1, 1),
            auto_dismiss=False,
        )

        layout_principal = BoxLayout(orientation="vertical", padding=12, spacing=10)

        grid_kpis = GridLayout(cols=3, spacing=10, size_hint_y=None, height=240)
        grid_kpis.add_widget(
            KPICard(
                "Venta Neta",
                f"{venta_neta:.2f} EUR",
                color_bg=[0.15, 0.25, 0.4, 1],
            )
        )
        grid_kpis.add_widget(
            KPICard(
                "T. Medio",
                f"{ticket_medio:.2f} EUR",
                color_bg=[0.2, 0.2, 0.25, 1],
            )
        )
        grid_kpis.add_widget(
            KPICard("UPT Global", f"{upt:.2f}", color_bg=[0.12, 0.3, 0.18, 1])
        )

        grid_kpis.add_widget(
            KPICard(
                "Tickets / Arts",
                f"{tickets} / {articulos_totales}",
                color_bg=[0.2, 0.2, 0.25, 1],
            )
        )
        grid_kpis.add_widget(
            KPICard(
                "Restante Obj.",
                f"{restante_objetivo:.2f} EUR",
                color_bg=[0.35, 0.25, 0.1, 1],
            )
        )
        grid_kpis.add_widget(
            KPICard(
                "Cumplimiento",
                f"{cumplimiento:.1f} %",
                color_bg=[0.28, 0.15, 0.35, 1],
            )
        )

        layout_principal.add_widget(grid_kpis)

        lbl_seccion_desglose = Label(
            text="DESGLOSE POR DEPENDIENTE",
            font_size="14sp",
            bold=True,
            color=[0.9, 0.9, 0.9, 1],
            size_hint_y=None,
            height=35,
            padding=[0, 10, 0, 5],
            halign="left",
        )
        lbl_seccion_desglose.bind(size=lbl_seccion_desglose.setter("text_size"))
        layout_principal.add_widget(lbl_seccion_desglose)

        scroll = ScrollView(size_hint=(1, 1))
        tabla_layout = GridLayout(
            cols=5, spacing=6, size_hint_y=None, padding=[4, 4]
        )
        tabla_layout.bind(minimum_height=tabla_layout.setter("height"))

        columnas_config = [
            ("Vendedor", "left"),
            ("Ventas", "right"),
            ("Tkts", "center"),
            ("Tm", "right"),
            ("UPT", "right"),
        ]

        for titulo, alin in columnas_config:
            lbl_h = Label(
                text=f"[b]{titulo}[/b]",
                markup=True,
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=[0.7, 0.8, 0.95, 1],
                halign=alin,
                valign="middle",
            )
            lbl_h.bind(size=lbl_h.setter("text_size"))
            tabla_layout.add_widget(lbl_h)

        ranking = sorted(ventas_dependiente.items(), key=lambda x: x[1], reverse=True)

        for vendedor, imp in ranking:
            v_tkts = tickets_dependiente.get(vendedor, 0)
            v_arts = articulos_dependiente.get(vendedor, 0)
            v_tm = (imp / v_tkts) if v_tkts > 0 else 0.0
            v_upt = (v_arts / v_tkts) if v_tkts > 0 else 0.0

            lbl_nom = Label(
                text=str(vendedor),
                font_size="12sp",
                size_hint_y=None,
                height=28,
                color=[1, 1, 1, 1],
                halign="left",
                valign="middle",
            )
            lbl_nom.bind(size=lbl_nom.setter("text_size"))
            tabla_layout.add_widget(lbl_nom)

            lbl_vta = Label(
                text=f"{imp:.2f} EUR",
                font_size="12sp",
                size_hint_y=None,
                height=28,
                color=[1, 1, 1, 1],
                halign="right",
                valign="middle",
            )
            lbl_vta.bind(size=lbl_vta.setter("text_size"))
            tabla_layout.add_widget(lbl_vta)

            lbl_tkts = Label(
                text=str(v_tkts),
                font_size="12sp",
                size_hint_y=None,
                height=28,
                color=[1, 1, 1, 1],
                halign="center",
                valign="middle",
            )
            lbl_tkts.bind(size=lbl_tkts.setter("text_size"))
            tabla_layout.add_widget(lbl_tkts)

            lbl_tm = Label(
                text=f"{v_tm:.2f} EUR",
                font_size="12sp",
                size_hint_y=None,
                height=28,
                color=[1, 1, 1, 1],
                halign="right",
                valign="middle",
            )
            lbl_tm.bind(size=lbl_tm.setter("text_size"))
            tabla_layout.add_widget(lbl_tm)

            lbl_upt = Label(
                text=f"{v_upt:.2f}",
                font_size="12sp",
                bold=True,
                size_hint_y=None,
                height=28,
                color=[0.3, 0.9, 0.4, 1],
                halign="right",
                valign="middle",
            )
            lbl_upt.bind(size=lbl_upt.setter("text_size"))
            tabla_layout.add_widget(lbl_upt)

        scroll.add_widget(tabla_layout)
        layout_principal.add_widget(scroll)

        btn_cerrar = Button(
            text="CERRAR",
            size_hint=(None, None),
            size=(140, 40),
            pos_hint={"center_x": 0.5},
        )
        btn_cerrar.bind(on_press=lambda x: popup.dismiss())
        layout_principal.add_widget(btn_cerrar)

        popup.content = layout_principal
        popup.open()
   
    def abrir_informe_diario(self, instance):
        venta_neta = 0
        tickets = 0
        articulos_totales = 0
        ticket_medio = 0
        upt = 0
        conversion = 0
        clientes = 0
        objetivo = 0
        cumplimiento = 0
        diferencia = 0
        ventas_dependiente = {}
        tickets_dependiente = {}
        articulos_dependiente = {}
        ventas_mes_dependiente = {}

        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except Exception:
            ventas = []

        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias = json.load(f)
        except Exception:
            dias = []

        fecha_busqueda = getattr(self, "fecha_actual", str(date.today()))
        try:
            fecha_informe = datetime.strptime(fecha_busqueda, "%Y-%m-%d")
        except Exception:
            fecha_informe = datetime.now()

        for venta in ventas:
            if venta.get("fecha", "")[:7] == fecha_busqueda[:7]:
                vendedor = venta.get("vendedor", "Sin Nombre")
                if vendedor not in ventas_mes_dependiente:
                    ventas_mes_dependiente[vendedor] = 0
                ventas_mes_dependiente[vendedor] += float(venta.get("importe", 0))

            if venta.get("fecha") != fecha_busqueda:
                continue

            tickets += 1
            venta_neta += float(venta.get("importe", 0))
            articulos_totales += int(venta.get("articulos", 0))
            vendedor = venta.get("vendedor", "Sin Nombre")

            if vendedor not in tickets_dependiente:
                tickets_dependiente[vendedor] = 0
            if vendedor not in articulos_dependiente:
                articulos_dependiente[vendedor] = 0

            tickets_dependiente[vendedor] += 1
            articulos_dependiente[vendedor] += int(venta.get("articulos", 0))

            if vendedor not in ventas_dependiente:
                ventas_dependiente[vendedor] = 0
            ventas_dependiente[vendedor] += float(venta.get("importe", 0))

        if tickets > 0:
            ticket_medio = venta_neta / tickets
            upt = articulos_totales / tickets
        else:
            ticket_medio = 0
            upt = 0

        # Limpiamos la fecha de búsqueda para la consulta
        fecha_busqueda_limpia = str(fecha_busqueda).split(" ")[0].split("T")[0]

        for dia in dias:
            if dia.get("fecha") == fecha_busqueda_limpia:
                clientes = int(dia.get("clientes", 0))
                break

        # Forzar la obtención del objetivo del mes consultado
        objetivo = self.obtener_objetivo_mes(fecha_busqueda_limpia)

        if clientes > 0:
            conversion = (tickets / clientes) * 100
        else:
            conversion = 0

        if objetivo > 0:
            cumplimiento = (venta_neta / objetivo) * 100
        else:
            cumplimiento = 0

        diferencia = objetivo - venta_neta

        texto_dependientes = ""
        texto_ticket_medio = ""
        texto_upt = ""

        ranking = sorted(
            ventas_dependiente.items(), key=lambda x: x[1], reverse=True
        )
        ranking_mes = sorted(
            ventas_mes_dependiente.items(), key=lambda x: x[1], reverse=True
        )

        nombres_dia, ventas_dia = [], []
        nombres_mes, ventas_mes = [], []

        for vendedor, importe in ranking:
            nombres_dia.append(vendedor)
            ventas_dia.append(importe)
            texto_dependientes += f"{vendedor} ............ {importe:.2f} €\n"

            t_dep_count = tickets_dependiente.get(vendedor, 1)
            ticket_dep = importe / t_dep_count if t_dep_count > 0 else 0
            upt_dep = articulos_dependiente.get(vendedor, 0) / t_dep_count if t_dep_count > 0 else 0

            texto_ticket_medio += f"{vendedor} ............ {ticket_dep:.2f} €\n"
            texto_upt += f"{vendedor} ............ {upt_dep:.2f}\n"

        for vendedor, importe in ranking_mes:
            nombres_mes.append(vendedor)
            ventas_mes.append(importe)

        # --- INICIO BLOQUE DEVOLUCIONES ---
        devoluciones_por_dia = {d: 0.0 for d in range(1, 32)}

        for venta in ventas:
            try:
                # Soporta formatos con o sin hora "YYYY-MM-DD" o "YYYY-MM-DD HH:MM"
                f_raw = str(venta.get("fecha", "")).split(" ")[0].split("T")[0]
                fecha = datetime.strptime(f_raw, "%Y-%m-%d")
                if (
                    fecha.month == fecha_informe.month
                    and fecha.year == fecha_informe.year
                ):
                    imp = float(venta.get("importe", 0))
                    if venta.get("tipo") == "devolucion" or imp < 0:
                        devoluciones_por_dia[fecha.day] += abs(imp)
            except Exception:
                continue

        # Crear la gráfica de devoluciones
        # Crear la gráfica de devoluciones
        self.grafica_devoluciones = GraficaVentas(size_hint=(1, 1))
        self.grafica_devoluciones.color_barras = THEME["danger"]
        self.grafica_devoluciones.ventas = [
            devoluciones_por_dia[d] for d in range(1, 32)
        ]
        
        self.zona_devoluciones = BoxLayout(orientation="horizontal", spacing=dp(5))
        eje_y_dev = BoxLayout(orientation="vertical", size_hint=(None, 1), width=dp(35))
        
        maximo_dev = max(self.grafica_devoluciones.ventas) if max(self.grafica_devoluciones.ventas) > 0 else 50
        paso_dev = ((int(maximo_dev / 50) + 1) * 50) / 5

        for i in range(5, -1, -1):
            eje_y_dev.add_widget(
                Label(
                    text=str(int(paso_dev * i)),
                    font_size=sp(10),
                    color=THEME["text_muted"]
                )
            )

        self.zona_devoluciones.add_widget(eje_y_dev)
        self.zona_devoluciones.add_widget(self.grafica_devoluciones)
        self.grafica_devoluciones.redibujar()
        # --- FIN BLOQUE DEVOLUCIONES ---

        popup = Popup(
            title="Informe Diario", size_hint=(1, 1), auto_dismiss=False
        )

        layout = BoxLayout(orientation="horizontal", padding=dp(10), spacing=dp(10))
        columna_izquierda = BoxLayout(orientation="vertical", size_hint=(0.55, 1), spacing=dp(10))

        # --- FILA SUPERIOR KPI CON CARDS TEMA ---
        fila_kpi = GridLayout(cols=4, size_hint_y=None, height=dp(110), spacing=dp(8))
        
        def crear_kpi_tarjeta(titulo, valor):
            tarjeta = CardWidget(orientation="vertical", padding=dp(8))
            
            lbl_title = Label(
                text=titulo.upper(),
                font_size=sp(11),
                bold=True,
                color=THEME["text_muted"],
                halign="center",
                valign="middle"
            )
            lbl_title.bind(size=lambda i, v: setattr(i, "text_size", v))

            lbl_val = Label(
                text=valor,
                font_size=sp(22),
                bold=True,
                color=THEME["text_main"],
                halign="center",
                valign="middle"
            )
            lbl_val.bind(size=lambda i, v: setattr(i, "text_size", v))

            tarjeta.add_widget(lbl_title)
            tarjeta.add_widget(lbl_val)
            return tarjeta

        fila_kpi.add_widget(crear_kpi_tarjeta("VENTA", f"{venta_neta:.0f} €"))
        fila_kpi.add_widget(crear_kpi_tarjeta("TICKETS", str(tickets)))
        fila_kpi.add_widget(crear_kpi_tarjeta("ARTÍCULOS", str(articulos_totales)))
        fila_kpi.add_widget(crear_kpi_tarjeta("T. MEDIO", f"{ticket_medio:.2f} €"))

        columna_izquierda.add_widget(fila_kpi)

        # --- COLUMNA DERECHA (GRÁFICAS Y CONTROLES) ---
        columna_derecha = BoxLayout(orientation="vertical", size_hint=(0.45, 1), spacing=dp(6))
        
        titulo_graficas = Label(
            text="GRÁFICAS DE CONTROL",
            font_size=sp(16),
            bold=True,
            color=THEME["text_main"],
            size_hint_y=None,
            height=dp(35),
            halign="center",
            valign="middle"
        )
        columna_derecha.add_widget(titulo_graficas)

        # 1. Barra superior de botones
        botones_graficas = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(38), spacing=dp(4)
        )

        btn_ventas = Button(
            text="VENTAS", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["bg_card"], color=THEME["text_main"]
        )
        btn_objetivo = Button(
            text="OBJETIVO", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["bg_card"], color=THEME["text_main"]
        )
        btn_rendim = Button(
            text="RENDIM.", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["bg_card"], color=THEME["text_main"]
        )
        btn_equipo = Button(
            text="EQUIPO", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["bg_card"], color=THEME["text_main"]
        )
        btn_pdf = Button(
            text="PDF", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["primary"], color=THEME["text_main"]
        )
        btn_devol = Button(
            text="DEVOL.", font_size=sp(11), bold=True, background_normal="",
            background_color=THEME["bg_card"], color=THEME["text_main"]
        )

        # Eventos para cambiar de gráfica dinámicamente
        btn_ventas.bind(on_release=lambda x: self.cambiar_grafica_control("ventas"))
        btn_objetivo.bind(on_release=lambda x: self.cambiar_grafica_control("objetivo"))
        btn_rendim.bind(on_release=lambda x: self.cambiar_grafica_control("rendim"))
        btn_equipo.bind(on_release=lambda x: self.cambiar_grafica_control("equipo"))
        btn_pdf.bind(on_release=lambda x: self.generar_informe_direccion())
        btn_devol.bind(on_release=lambda x: self.cambiar_grafica_control("devoluciones"))

        botones_graficas.add_widget(btn_ventas)
        botones_graficas.add_widget(btn_objetivo)
        botones_graficas.add_widget(btn_rendim)
        botones_graficas.add_widget(btn_equipo)
        botones_graficas.add_widget(btn_pdf)
        botones_graficas.add_widget(btn_devol)

        columna_derecha.add_widget(botones_graficas)

        # 2. Subtítulo dinámico
        self.titulo_mes = Label(
            text="VENTAS DEL MES",
            font_size=sp(14),
            bold=True,
            color=THEME["accent"],
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle"
        )
        columna_derecha.add_widget(self.titulo_mes)

        # 3. Panel de la gráfica asignado a self.contenedor_grafica y self.zona_graficas
        panel_mes = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(450),
            padding=dp(10),
            spacing=dp(10),
        )
        columna_derecha.add_widget(panel_mes)

        self.zona_graficas = BoxLayout(orientation="vertical")
        self.contenedor_grafica = self.zona_graficas  # <-- Vincular ambas variables al mismo lugar
        self.zona_ventas = BoxLayout(orientation="horizontal", spacing=dp(5))

        self.zona_graficas.add_widget(self.zona_ventas)
        panel_mes.add_widget(self.zona_graficas)

        eje_y = BoxLayout(orientation="vertical", size_hint=(None, 1), width=dp(35))
        self.zona_ventas.add_widget(eje_y)


        ventas_por_dia = {d: 0.0 for d in range(1, 32)}
        tickets_por_dia = {d: 0 for d in range(1, 32)}
        articulos_por_dia = {d: 0 for d in range(1, 32)}
        
        for venta in ventas:
            try:
                fecha = datetime.strptime(venta["fecha"], "%Y-%m-%d")
                if (
                    fecha.month == fecha_informe.month
                    and fecha.year == fecha_informe.year
                ):
                    ventas_por_dia[fecha.day] += float(venta.get("importe", 0))
                    tickets_por_dia[fecha.day] += 1
                    articulos_por_dia[fecha.day] += int(venta.get("articulos", 0))
            except Exception:
                continue

        grafica = GraficaVentas(size_hint=(1, 1))
        grafica.ventas = [ventas_por_dia[d] for d in range(1, 32)]
        venta_mes = sum(ventas_por_dia.values())

        ticket_medio_por_dia = [
            (ventas_por_dia[d] / tickets_por_dia[d]) if tickets_por_dia[d] > 0 else 0
            for d in range(1, 32)
        ]
        upt_por_dia = [
            (articulos_por_dia[d] / tickets_por_dia[d]) if tickets_por_dia[d] > 0 else 0
            for d in range(1, 32)
        ]

        maximo_eje = max(grafica.ventas) if max(grafica.ventas) > 0 else 100
        paso = ((int(maximo_eje / 100) + 1) * 100) / 5

        for i in range(5, -1, -1):
            eje_y.add_widget(
                Label(
                    text=str(int(paso * i)),
                    font_size=sp(10),
                    color=THEME["text_muted"]
                )
            )

        self.zona_ventas.add_widget(grafica)
        grafica.redibujar()

        # --- CONFIGURACIÓN DE PANELES SECUNDARIOS ---
        self.zona_objetivo = BoxLayout(
            orientation="vertical", spacing=dp(15), padding=dp(10)
        )
        self.grafica_objetivo = GraficaObjetivo(size_hint=(1, None), height=dp(220))

        dias_mes = calendar.monthrange(fecha_informe.year, fecha_informe.month)[1]
        dias_restantes = max(1, dias_mes - fecha_informe.day)
        objetivo_restante = max(0, objetivo - venta_mes)
        objetivo_diario = objetivo_restante / dias_restantes

        self.grafica_objetivo.objetivo = objetivo_diario
        self.grafica_objetivo.venta = venta_neta
        self.grafica_objetivo.cumplimiento = (
            (venta_neta / objetivo_diario) * 100 if objetivo_diario > 0 else 0
        )

        self.zona_objetivo.add_widget(self.grafica_objetivo)
        self.grafica_objetivo.redibujar()

        diferencia = objetivo - venta_mes
        cumplimiento_mes = (venta_mes / objetivo) * 100 if objetivo > 0 else 0

        if diferencia > 0:
            texto_objetivo = (
                f"Te faltan {diferencia:.2f} € para alcanzar el objetivo mensual.\n"
                f"Cumplimiento mensual: {cumplimiento_mes:.2f} %"
            )
        elif diferencia == 0:
            texto_objetivo = (
                f"🎉 ¡Objetivo mensual alcanzado!\n"
                f"Cumplimiento mensual: {cumplimiento_mes:.2f} %"
            )
        else:
            texto_objetivo = (
                f"🎉 ¡Objetivo mensual superado en {-diferencia:.2f} €!\n\n"
                f"Cumplimiento mensual: {cumplimiento_mes:.2f} %"
            )

                # Reemplazo del Label inferior con espacio dinámico para que no pise las barras:
        self.label_objetivo = Label(
            text=texto_objetivo,
            font_size=sp(13),
            bold=True,
            color=THEME["text_main"],
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(70),  # Aumentamos la altura para que quepan las 2 líneas cómodamente
        )
        self.label_objetivo.bind(
            size=lambda i, v: setattr(i, "text_size", (v[0], None))
        )

        # Añadimos un pequeño espacio transparente ANTES del texto para empujarlo hacia abajo
        self.zona_objetivo.add_widget(Widget(size_hint_y=None, height=dp(20)))
        self.zona_objetivo.add_widget(self.label_objetivo)


        self.zona_rendimiento = BoxLayout(
            orientation="vertical", spacing=dp(10), padding=dp(10)
        )
        titulo_ticket = Label(
            text="TICKET MEDIO DIARIO",
            font_size=sp(13),
            bold=True,
            color=THEME["text_muted"],
            size_hint_y=None,
            height=dp(25),
        )
        self.zona_rendimiento.add_widget(titulo_ticket)

        zona_ticket = BoxLayout(orientation="horizontal", spacing=dp(5))
        eje_y_ticket = BoxLayout(
            orientation="vertical", size_hint=(None, 1), width=dp(35)
        )
        zona_ticket.add_widget(eje_y_ticket)

        self.grafica_rendimiento = GraficaTicketMedio(size_hint=(1, 1))
        self.grafica_rendimiento.ventas = ticket_medio_por_dia
        self.grafica_rendimiento.objetivo_ticket = 80

        maximo_ticket = max(max(ticket_medio_por_dia), 80)
        paso = ((int(maximo_ticket / 10) + 1) * 10) / 5

        for i in range(5, -1, -1):
            eje_y_ticket.add_widget(
                Label(
                    text=str(int(paso * i)),
                    font_size=sp(10),
                    color=THEME["text_muted"]
                )
            )

        zona_ticket.add_widget(self.grafica_rendimiento)
        self.zona_rendimiento.add_widget(zona_ticket)
        self.grafica_rendimiento.redibujar()

        titulo_upt = Label(
            text="UPT DIARIO",
            font_size=sp(13),
            bold=True,
            color=THEME["text_muted"],
            size_hint_y=None,
            height=dp(25),
        )
        self.zona_rendimiento.add_widget(titulo_upt)

        zona_upt = BoxLayout(orientation="horizontal", spacing=dp(5))
        eje_y_upt = BoxLayout(orientation="vertical", size_hint=(None, 1), width=dp(35))
        zona_upt.add_widget(eje_y_upt)

        self.grafica_upt = GraficaTicketMedio(size_hint=(1, 1))
        self.grafica_upt.ventas = upt_por_dia
        self.grafica_upt.objetivo_ticket = 1.2
        
        maximo_upt = max(max(upt_por_dia), 1.2)
        paso = maximo_upt / 5

        for i in range(5, -1, -1):
            eje_y_upt.add_widget(
                Label(
                    text=f"{paso * i:.1f}",
                    font_size=sp(10),
                    color=THEME["text_muted"]
                )
            )

        zona_upt.add_widget(self.grafica_upt)
        self.zona_rendimiento.add_widget(zona_upt)
        self.grafica_upt.redibujar()

        self.zona_equipo = BoxLayout(
            orientation="vertical", spacing=dp(10), padding=dp(10)
        )
        lista_equipo = BoxLayout(orientation="vertical", spacing=dp(8))

        grafica_dia = GraficaEquipo(size_hint=(1, 1.4))
        grafica_dia.nombres = nombres_dia
        grafica_dia.ventas = ventas_dia
        lista_equipo.add_widget(grafica_dia)
        grafica_dia.redibujar()

        lista_equipo.add_widget(Widget(size_hint_y=None, height=dp(15)))

        titulo_mes = Label(
            text="RANKING DEL MES",
            font_size=sp(13),
            bold=True,
            color=THEME["text_muted"],
            size_hint_y=None,
            height=dp(20),
        )
        lista_equipo.add_widget(titulo_mes)
        lista_equipo.add_widget(Widget(size_hint_y=None, height=dp(15)))

        grafica_mes = GraficaEquipo(size_hint=(1, 1))
        grafica_mes.nombres = nombres_mes
        grafica_mes.ventas = ventas_mes
        lista_equipo.add_widget(grafica_mes)
        grafica_mes.redibujar()

        titulo_equipo = Label(
            text="RANKING DE DEPENDIENTES",
            font_size=sp(14),
            bold=True,
            color=THEME["text_main"],
            size_hint_y=None,
            height=dp(25),
        )
        self.zona_equipo.add_widget(titulo_equipo)
        self.zona_equipo.add_widget(lista_equipo)

        columna_derecha.add_widget(Widget(size_hint_y=1))

        # --- COLUMNA IZQUIERDA: TARJETA DE RESUMEN EN TEXTO ---
        contenido = BoxLayout(
            orientation="vertical", spacing=dp(10), size_hint_y=None
        )
        contenido.bind(minimum_height=contenido.setter("height"))
        scroll = ScrollView(size_hint=(1, 1))

        hex_accent = "4FD1C5"

        informe = Label(
            text=(
            # ✅ AHORA (Muestra la fecha filtrada formateada en DD/MM/YYYY):
                f"[b]Fecha:[/b] {datetime.strptime(fecha_busqueda_limpia, '%Y-%m-%d').strftime('%d/%m/%Y')}\n\n"

                f"[b]UPT ........................[/b] {upt:.2f}\n\n"
                f"[b]CONVERSIÓN .................[/b] {conversion:.2f} %\n\n"
                f"[b]OBJETIVO ...................[/b] {objetivo:.2f} €\n\n"
                f"[b]CUMPLIMIENTO ...............[/b] {cumplimiento:.2f} %\n\n"
                f"[b]DIFERENCIA .................[/b] {diferencia:.2f} €\n\n"
                f"[color={hex_accent}][b]VENTA POR DEPENDIENTE[/b][/color]\n\n"
                f"{texto_dependientes}\n\n"
                f"[color={hex_accent}][b]TICKET MEDIO POR DEPENDIENTE[/b][/color]\n\n"
                f"{texto_ticket_medio}\n\n"
                f"[color={hex_accent}][b]UPT POR DEPENDIENTE[/b][/color]\n\n"
                f"{texto_upt}"
            ),
            markup=True,
            font_size=sp(15),
            color=THEME["text_main"],
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        informe.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        informe.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))

        contenido_tarjeta = CardWidget(
            orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)
        )
        contenido_tarjeta.bind(
            minimum_height=contenido_tarjeta.setter("height")
        )
        contenido_tarjeta.add_widget(informe)
        scroll.add_widget(contenido_tarjeta)

        columna_izquierda.add_widget(scroll)

        btn_cerrar = Button(
            text="CERRAR",
            size_hint=(None, None),
            size=(dp(140), dp(40)),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=THEME["bg_card"],
            color=THEME["text_muted"],
            bold=True,
            font_size=sp(13)
        )
        btn_cerrar.bind(on_press=lambda x: popup.dismiss())

        columna_izquierda.add_widget(btn_cerrar)
        layout.add_widget(columna_izquierda)
        layout.add_widget(columna_derecha)

        popup.content = layout
        popup.open()

    def abrir_devoluciones(self, instance):
        popup = Popup(
            title="DEVOLUCIONES", size_hint=(0.80, 0.80), auto_dismiss=False
        )

        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                self.ventas = json.load(f)
        except Exception:
            self.ventas = []

        def crear_input_dev(hint, is_float=False):
            return TextInput(
                multiline=False,
                size_hint_y=None,
                height=dp(48),
                font_size=sp(16),
                hint_text=hint,
                padding=(dp(12), dp(12)),
                foreground_color=THEME["text_main"],
                hint_text_color=THEME["text_muted"],
                cursor_color=THEME["accent"],
                background_normal="",
                background_active="",
                background_color=THEME["bg_card"],
                input_filter="float" if is_float else "int",
            )

        self.dev_vendedor = crear_input_dev("Nombre del vendedor")
        self.dev_articulos = crear_input_dev("Número de artículos a devolver")
        self.dev_importe = crear_input_dev(
            "Importe de la devolución (€)",
            is_float=True
        )

        self.dev_vendedor.bind(
            on_text_validate=lambda x: setattr(
                self.dev_articulos,
                "focus",
                True
            )
        )

        self.dev_articulos.bind(
            on_text_validate=lambda x: setattr(
                self.dev_importe,
                "focus",
                True
            )
        )

        self.dev_importe.bind(
            on_text_validate=self.guardar_devolucion
        )

        layout.add_widget(
            Label(
                text="REGISTRO DE DEVOLUCIÓN",
                font_size=sp(16),
                bold=True,
                color=THEME["text_main"]
            )
        )

        layout.add_widget(self.dev_vendedor)
        layout.add_widget(self.dev_articulos)
        layout.add_widget(self.dev_importe)
        
        self.lista_devoluciones = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=10
        )
        self.lista_devoluciones.bind(
            minimum_height=self.lista_devoluciones.setter("height")
        )

        fecha_filtro = getattr(self, "fecha_actual", str(date.today()))

        for venta in self.ventas:

            if venta.get("tipo") != "devolucion":
                continue

            if venta.get("fecha") != fecha_filtro:
                continue

            texto = (
                f"Vendedor: {venta['vendedor']}   |   "
                f"Artículos: {abs(int(venta['articulos']))}   |   "
                f"Importe: {abs(float(venta['importe'])):.2f} €"
            )

            fila = Button(
                text=texto,
                size_hint_y=None,
                height=55,
                background_normal="",
                background_color=THEME["bg_card"],
                color=THEME["text_main"],
                bold=True,
            )

            self.lista_devoluciones.add_widget(fila)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.lista_devoluciones)

        layout.add_widget(scroll)

        btn_box = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(45))
        
        btn_guardar = Button(
            text="REGISTRAR DEVOLUCIÓN",
            background_normal="",
            background_color=THEME["primary"],
            color=THEME["text_main"],
            bold=True
        )
        btn_guardar.bind(on_press=self.guardar_devolucion)
        
        btn_cerrar = Button(
            text="CANCELAR",
            background_normal="",
            background_color=THEME["bg_card"],
            color=THEME["text_muted"],
            bold=True
        )
        btn_cerrar.bind(on_press=lambda x: popup.dismiss())

        btn_box.add_widget(btn_guardar)
        btn_box.add_widget(btn_cerrar)

        layout.add_widget(btn_box)
        popup.content = layout
        self.popup_devoluciones = popup
        popup.open()


    def abrir_ventas(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
        estilo_input = {
            "multiline": False,
            "size_hint_y": None,
            "height": 70,
            "font_size": 32,
            "padding_y": (16, 16),
            "foreground_color": (0.95, 0.95, 0.95, 1),
            "cursor_color": (0.2, 0.6, 0.9, 1),
            "background_normal": "",
            "background_active": "",
            "background_color": (0.18, 0.20, 0.24, 1),
        }

        self.entry_vendedor = TextInput(hint_text="Vendedor", **estilo_input)
        self.entry_vendedor.bind(on_text_validate=self.saltar_a_articulos)
        layout.add_widget(self.entry_vendedor)

        self.entry_articulos = TextInput(hint_text="Artículos", **estilo_input)
        self.entry_articulos.bind(on_text_validate=self.saltar_a_importe)
        layout.add_widget(self.entry_articulos)

        self.entry_importe = TextInput(hint_text="Importe (€)", **estilo_input)
        self.entry_importe.bind(on_text_validate=self.validar_guardado)
        layout.add_widget(self.entry_importe)

        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                self.ventas = json.load(f)
        except Exception:
            self.ventas = []

        fecha_filtro = getattr(self, "fecha_actual", str(date.today()))

        total_acumulado = sum(
            float(v.get("importe", 0))
            for v in self.ventas
            if v.get("fecha") == fecha_filtro
        )
        total_tickets = sum(
            1 for v in self.ventas if v.get("fecha") == fecha_filtro
        )

        barra_acumulado = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=65, padding=[15, 10]
        )

        with barra_acumulado.canvas.before:
            Color(0.18, 0.52, 0.35, 1)
            rect_bar = RoundedRectangle(
                pos=barra_acumulado.pos,
                size=barra_acumulado.size,
                radius=[8],
            )

        barra_acumulado.bind(
            pos=lambda inst, val: setattr(rect_bar, "pos", inst.pos),
            size=lambda inst, val: setattr(rect_bar, "size", inst.size),
        )

        lbl_acumulado = Label(
            text=f"[b]Ventas acumuladas del día:[/b] {total_acumulado:.2f} €   |   [b]Tickets:[/b] {total_tickets}",
            markup=True,
            font_size=24,
            color=(1, 1, 1, 1),
        )
        barra_acumulado.add_widget(lbl_acumulado)
        layout.add_widget(barra_acumulado)

        self.lista_ventas = GridLayout(cols=1, size_hint_y=None, spacing=10)

        for venta in self.ventas:
            if "fecha" not in venta or venta["fecha"] != fecha_filtro:
                continue

            texto = (
                f" Vendedor: {venta['vendedor']}   |   "
                f"Artículos: {venta['articulos']}   |   "
                f"Importe: {venta['importe']} €"
            )

            fila = Button(
                text=texto,
                size_hint_y=None,
                height=65,
                font_size=22,
                bold=True,
                background_normal="",
                background_color=(0.22, 0.25, 0.30, 1),
                color=(1, 1, 1, 1),
            )
            fila.id_venta = venta["id"]
            fila.bind(on_press=self.editar_venta)
            self.lista_ventas.add_widget(fila)

        self.lista_ventas.bind(minimum_height=self.lista_ventas.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.lista_ventas)
        layout.add_widget(scroll)

        botones = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=60, spacing=10
        )
        btn_cerrar = Button(
            text="CERRAR",
            size_hint=(None, None),
            size=(180, 50),
            font_size=20,
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=(0.3, 0.35, 0.4, 1),
            bold=True,
        )
        btn_cerrar.bind(on_press=self.cerrar_popup_ventas)
        botones.add_widget(btn_cerrar)
        layout.add_widget(botones)

        self.popup_ventas = Popup(
            title="Introducir Ventas",
            content=layout,
            size_hint=(1, 1),
            auto_dismiss=False,
            background="",
            background_color=(0.12, 0.12, 0.12, 1),
        )
        self.popup_ventas.open()
        
    def cerrar_popup_ventas(self, instance):
        self.popup_ventas.dismiss()
        
    def guardar_devolucion(self, instance):
        vendedor = self.dev_vendedor.text.strip()

        try:
            articulos = int(self.dev_articulos.text or 0)
        except Exception:
            articulos = 0

        try:
            importe = abs(float(self.dev_importe.text or 0))
        except Exception:
            importe = 0.0

        venta = {
            "id": len(self.ventas) + 1,
            "fecha": getattr(self, "fecha_actual", str(date.today())),
            "vendedor": vendedor,
            "articulos": -articulos,
            "importe": -importe,
            "tipo": "devolucion",
        }

        self.ventas.append(venta)
        texto = (
            f"Vendedor: {venta['vendedor']}   |   "
            f"Artículos: {abs(int(venta['articulos']))}   |   "
            f"Importe: {abs(float(venta['importe'])):.2f} €"
        )

        fila = Button(
            text=texto,
            size_hint_y=None,
            height=55,
            background_normal="",
            background_color=THEME["bg_card"],
            color=THEME["text_main"],
            bold=True,
        )

        self.lista_devoluciones.add_widget(fila)

        with open("ventas.json", "w", encoding="utf-8") as f:
            json.dump(self.ventas, f, indent=4, ensure_ascii=False)

        self.dev_vendedor.text = ""
        self.dev_articulos.text = ""
        self.dev_importe.text = ""

        self.dev_vendedor.focus = True

    def guardar_venta(self, instance):
        vendedor = self.entry_vendedor.text
        articulos = self.entry_articulos.text
        importe = float(self.entry_importe.text or 0)

        tipo = "devolucion" if importe < 0 else "venta"
        texto = f"{vendedor} | {articulos} | {importe} €"
        nuevo_id = len(self.ventas) + 1

        venta = {
            "id": nuevo_id,
            "fecha": getattr(self, "fecha_actual", str(date.today())),
            "vendedor": vendedor,
            "articulos": articulos,
            "importe": importe,
            "tipo": tipo,
        }

        self.ventas.append(venta)

        with open("ventas.json", "w", encoding="utf-8") as f:
            json.dump(self.ventas, f, indent=4, ensure_ascii=False)

        fila = Button(text=texto, size_hint_y=None, height=60)
        fila.id_venta = venta["id"]
        fila.bind(on_press=self.editar_venta)

        self.lista_ventas.add_widget(fila)

        self.entry_vendedor.text = ""
        self.entry_articulos.text = ""
        self.entry_importe.text = ""
        self.entry_vendedor.focus = True

    def validar_guardado(self, instance):
        if (
            self.entry_vendedor.text.strip() == ""
            or self.entry_articulos.text.strip() == ""
            or self.entry_importe.text.strip() == ""
        ):
            return
        self.guardar_venta(instance)

    def saltar_a_articulos(self, instance):
        self.entry_articulos.focus = True

    def saltar_a_importe(self, instance):
        self.entry_importe.focus = True

    def editar_venta(self, instance):
        popup = Popup(title="Venta", size_hint=(0.7, 0.4))
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        texto_venta = Label(text=instance.text)
        btn_modificar = Button(text="MODIFICAR")

        # Pasar 'popup' para cerrarlo antes de abrir el siguiente
        btn_modificar.bind(
            on_press=lambda x: self.modificar_venta(instance, popup)
        )

        btn_eliminar = Button(text="ELIMINAR")
        btn_eliminar.bind(
            on_press=lambda x: self.eliminar_venta(instance, popup)
        )

        btn_cerrar = Button(text="CERRAR")
        btn_cerrar.bind(on_press=popup.dismiss)

        layout.add_widget(texto_venta)
        layout.add_widget(btn_modificar)
        layout.add_widget(btn_eliminar)
        layout.add_widget(btn_cerrar)

        popup.content = layout
        popup.open()

    def eliminar_venta(self, boton_venta, popup):
        id_eliminar = getattr(boton_venta, "id_venta", None)

        if id_eliminar is not None:
            # 1. Borrar de la lista local en memoria
            self.ventas = [
                v for v in self.ventas if str(v.get("id")) != str(id_eliminar)
            ]

            # 2. Cargar TODO el JSON, eliminar la venta específica y reescribir
            try:
                with open("ventas.json", "r", encoding="utf-8") as f:
                    todas_las_ventas = json.load(f)

                # Filtramos en el archivo completo
                todas_las_ventas = [
                    v
                    for v in todas_las_ventas
                    if str(v.get("id")) != str(id_eliminar)
                ]

                with open("ventas.json", "w", encoding="utf-8") as f:
                    json.dump(todas_las_ventas, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error guardando borrado en ventas.json: {e}")

        # 3. Quitar el widget de la venta del layout visual
        if (
            hasattr(self, "lista_ventas")
            and boton_venta in self.lista_ventas.children
        ):
            self.lista_ventas.remove_widget(boton_venta)

        popup.dismiss()

    def modificar_venta(self, boton, popup_anterior):
        # Cierra el primer popup para evitar apilamientos/rebotes
        if popup_anterior:
            popup_anterior.dismiss()

        popup = Popup(title="Modificar Venta", size_hint=(0.8, 0.8))
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        datos = boton.text.split("|")
        self.id_venta_editando = getattr(boton, "id_venta", None)
        self.boton_editando = boton

        # Limpiamos el texto del vendedor
        vendedor = datos[0].strip() if len(datos) > 0 else ""
        vendedor = (
            vendedor.replace("Vendedor:", "")
            .replace("vendedor:", "")
            .replace("VENDEDOR:", "")
            .strip()
        )

        articulos = datos[1].strip() if len(datos) > 1 else ""
        importe = datos[2].replace("€", "").strip() if len(datos) > 2 else "0"

        layout.add_widget(Label(text="VENDEDOR"))
        entry_vendedor = TextInput(text=str(vendedor), multiline=False)
        layout.add_widget(entry_vendedor)

        layout.add_widget(Label(text="ARTICULOS"))
        entry_articulos = TextInput(text=str(articulos), multiline=False)
        layout.add_widget(entry_articulos)

        layout.add_widget(Label(text="IMPORTE"))
        entry_importe = TextInput(text=str(importe), multiline=False)
        layout.add_widget(entry_importe)

        btn_guardar = Button(text="GUARDAR CAMBIOS")
        btn_guardar.bind(
            on_press=lambda x: self.guardar_cambios_venta(
                popup, entry_vendedor, entry_articulos, entry_importe
            )
        )
        layout.add_widget(btn_guardar)

        btn_cerrar = Button(text="CERRAR")
        btn_cerrar.bind(on_press=popup.dismiss)
        layout.add_widget(btn_cerrar)

        popup.content = layout
        popup.open()

    def guardar_cambios_venta(
        self, popup, entry_vendedor, entry_articulos, entry_importe
    ):
        # Limpieza estricta del vendedor
        vendedor_raw = (
            entry_vendedor.text.replace("Vendedor:", "")
            .replace("vendedor:", "")
            .replace("VENDEDOR:", "")
            .strip()
        )

        # Mantener siempre el vendedor como texto
        # para evitar que "842" y 842 se consideren diferentes
        vendedor_limpio = vendedor_raw
        # Conversión segura de importe
        try:
            val_importe = float(entry_importe.text.replace(",", ".").strip())
        except ValueError:
            val_importe = 0.0

        # Conversión segura de artículos
        try:
            val_articulos = int(
                float(entry_articulos.text.replace(",", ".").strip())
            )
        except ValueError:
            val_articulos = 0

        # 1. Actualización en la lista en memoria local
        for venta in self.ventas:
            if str(venta.get("id")) == str(self.id_venta_editando):
                venta["vendedor"] = vendedor_limpio
                venta["articulos"] = val_articulos
                venta["importe"] = val_importe
                venta["tipo"] = (
                    "devolucion" if val_importe < 0 else "venta"
                )

                if hasattr(self, "boton_editando") and self.boton_editando:
                    self.boton_editando.text = (
                        f"{venta['vendedor']} | {venta['articulos']} |"
                        f" {venta['importe']:.2f} €"
                    )
                break

        # 2. Actualización segura en el JSON completo (preservando los demás días)
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                todas_las_ventas = json.load(f)

            # Normalizar todos los vendedores existentes como texto
            for venta in todas_las_ventas:
                if "vendedor" in venta:
                    venta["vendedor"] = str(
                        venta["vendedor"]
                    ).strip()

            # Buscar y actualizar la venta modificada
            for venta in todas_las_ventas:
                if str(venta.get("id")) == str(
                    self.id_venta_editando
                ):
                    venta["vendedor"] = vendedor_limpio
                    venta["articulos"] = val_articulos
                    venta["importe"] = val_importe
                    venta["tipo"] = (
                        "devolucion"
                        if val_importe < 0
                        else "venta"
                    )
                    break

            with open("ventas.json", "w", encoding="utf-8") as f:
                json.dump(
                    todas_las_ventas,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:
            print(
                f"Error actualizando ventas.json: {e}"
            )

        popup.dismiss()


    def armar_tabla(
        self,
        lista_data,
        style_body,
        col2_title="Importe Net.",
        es_fmt_num=True,
        color_val="#2B5C8F",
    ):
        """Genera la tabla con anchos perfectamente simétricos para alinearse con la gráfica"""
        col1_title = "Día" if "Peso" in col2_title else "Dep."
        filas = [
            [
                Paragraph(f"<b>{col1_title}</b>", style_body),
                Paragraph(f"<b>{col2_title}</b>", style_body),
            ]
        ]

        for dep, val in lista_data:
            if "%" in col2_title:
                txt_v = f"{val:.1f} %"
            elif es_fmt_num:
                txt_v = f"{val:.2f} €"
            else:
                txt_v = f"{val:.2f}"

            filas.append(
                [
                    Paragraph(str(dep), style_body),
                    Paragraph(
                        f"<font color='{color_val}'><b>{txt_v}</b></font>",
                        style_body,
                    ),
                ]
            )

        if len(filas) == 1:
            filas.append(
                [
                    Paragraph("Sin datos", style_body),
                    Paragraph("-", style_body),
                ]
            )

        # 4.7 cm + 4.7 cm = 9.4 cm de ancho total de tabla
        t = Table(filas, colWidths=[4.7 * cm, 4.7 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E1E4E8")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
                    ("TOPPADDING", (0, 0), (-1, -1), 0.8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return t

    def crear_grafica_horizontal(
        self, datos, etiquetas, color, alto_grafica=110
    ):
        """Genera la gráfica ajustando su altura proporcionalmente"""

        dibujo = Drawing(320, alto_grafica)

        graf = HorizontalBarChart()
        graf.x = 60
        graf.y = 12
        graf.width = 250
        graf.height = alto_grafica - 18

        graf.data = [list(reversed(datos))]
        graf.categoryAxis.categoryNames = list(reversed(etiquetas))

        graf.categoryAxis.labels.boxAnchor = "e"
        graf.categoryAxis.labels.dx = -6
        graf.categoryAxis.labels.fontName = "Helvetica"
        graf.categoryAxis.labels.fontSize = 8

        graf.valueAxis.valueMin = 0
        maximo = max(datos) if datos else 1
        if maximo <= 0:
            maximo = 1

        graf.valueAxis.valueMax = maximo * 1.10
        graf.valueAxis.valueStep = max(1, round(maximo / 4))

        graf.valueAxis.labels.fontName = "Helvetica"
        graf.valueAxis.labels.fontSize = 7

        graf.bars[0].fillColor = color
        graf.bars[0].strokeColor = colors.white
        graf.bars[0].strokeWidth = 0.5

        dibujo.add(graf)
        return dibujo

    def crear_bloque_tabla_grafica(
        self, datos, titulo_columna, color, style_body
    ):
        """Estructura en dos celdas de 9.7 cm cada una (Total: 19.4 cm de ancho útil)"""
        color_hex = color.hexval() if hasattr(color, "hexval") else str(color)
        es_porcentaje = "%" in titulo_columna or "UPT" in titulo_columna

        tabla = self.armar_tabla(
            datos,
            style_body,
            col2_title=titulo_columna,
            es_fmt_num=not es_porcentaje,
            color_val=color_hex,
        )

        if not datos:
            etiquetas = ["Sin datos"]
            valores = [0.0]
        else:
            etiquetas = [str(x[0]) for x in datos]
            if es_porcentaje:
                valores = [max(0.0, float(x[1])) for x in datos]
            else:
                valores = [abs(float(x[1])) for x in datos]

        # Altura dinámica: evita que ocupe espacio innecesario si hay pocas filas
        num_filas = max(len(datos), 1)
        alto_grafica = max(70, min(140, num_filas * 14 + 20))

        grafica = self.crear_grafica_horizontal(
            valores, etiquetas, color, alto_grafica=alto_grafica
        )

        bloque = Table([[tabla, grafica]], colWidths=[9.5 * cm, 9.9 * cm])
        bloque.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return bloque


    def generar_informe_direccion(self, instance=None):
        # 1. RECOGIDA Y LIMPIEZA DE FECHA CONSULTADA
        fecha_str = getattr(self, "fecha_actual", str(date.today()))
        fecha_str_corta = fecha_str.split(" ")[0].split("T")[0]
        fecha_dt = datetime.strptime(fecha_str_corta, "%Y-%m-%d")
        target_date = fecha_dt.date()
        target_int = int(target_date.strftime("%Y%m%d"))

        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas_data = json.load(f)
        except Exception:
            ventas_data = []

        try:
            with open("dias.json", "r", encoding="utf-8") as f:
                dias_data = json.load(f)
        except Exception:
            dias_data = []

        venta_dia, tickets_dia, articulos_dia = 0.0, 0, 0
        venta_sem, tickets_sem, articulos_sem = 0.0, 0, 0
        venta_acum_mes, tickets_mes, articulos_mes = 0.0, 0, 0
        clientes_dia, objetivo_mes = 0, 0.0
        devoluciones_totales_mes = 0.0

        ventas_acum_dependiente = {}
        devoluciones_acum_dependiente = {}
        dep_stats_upt_acum = {}
        # Devoluciones acumuladas por día del mes consultado
        devoluciones_por_dia_mes = {
            d: 0.0 for d in range(1, 32)
        }

        dias_semana_nombres = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        ventas_por_dia_semana = [0.0] * 7

        iso_ano_consultado, iso_semana_consultada, _ = target_date.isocalendar()

        # PROCESAR dias.json
        for d in dias_data:
            try:
                f_d_str = str(d.get("fecha", "")).split(" ")[0].split("T")[0]
                f_d = datetime.strptime(f_d_str, "%Y-%m-%d").date()
                d_int = int(f_d.strftime("%Y%m%d"))
            except Exception:
                continue

            if d_int > target_int:
                continue

            if f_d.year == target_date.year and f_d.month == target_date.month:
                if d_int == target_int:
                    clientes_dia = int(d.get("clientes", 0) or 0)

        # Forzar a obtener el objetivo del mes correspondiente a la fecha seleccionada
        objetivo_mes = self.obtener_objetivo_mes(fecha_str_corta)

        # PROCESAR ventas.json
        for v in ventas_data:
            try:
                raw_f = str(v.get("fecha", "")).split(" ")[0].split("T")[0]
                f_v = datetime.strptime(raw_f, "%Y-%m-%d").date()
                v_int = int(f_v.strftime("%Y%m%d"))
            except Exception:
                continue

            if v_int > target_int:
                continue

            imp = float(v.get("importe", 0) or 0)
            vendedor = str(v.get("vendedor", "Sin Nombre"))
            es_dev = v.get("tipo") == "devolucion" or imp < 0
            arts = int(v.get("articulos", 1) or 1)
            cant_prendas = -abs(arts) if es_dev else abs(arts)

            ventas_por_dia_semana[f_v.weekday()] += imp
            f_v_iso_ano, f_v_iso_sem, _ = f_v.isocalendar()

            # ACUMULADO MES
            if f_v.year == target_date.year and f_v.month == target_date.month:
                articulos_mes += cant_prendas
                tickets_mes += 1

                if vendedor not in dep_stats_upt_acum:
                    dep_stats_upt_acum[vendedor] = [0, 0]
                dep_stats_upt_acum[vendedor][0] += cant_prendas
                dep_stats_upt_acum[vendedor][1] += 1

                if es_dev:
                    cant_dev = abs(imp)

                    # Acumular la devolución en el día correspondiente
                    devoluciones_por_dia_mes[f_v.day] += cant_dev

                    venta_acum_mes -= cant_dev

                    devoluciones_acum_dependiente[vendedor] = (
                        devoluciones_acum_dependiente.get(
                            vendedor, 0.0
                        ) + cant_dev
                    )

                    ventas_acum_dependiente[vendedor] = (
                        ventas_acum_dependiente.get(
                            vendedor, 0.0
                        ) - cant_dev
                    )
                else:
                    venta_acum_mes += imp
                    ventas_acum_dependiente[vendedor] = (
                        ventas_acum_dependiente.get(
                            vendedor, 0.0
                        ) + imp
                    )

                # ACUMULADO SEMANA
                if (
                    f_v_iso_ano == iso_ano_consultado
                    and f_v_iso_sem == iso_semana_consultada
                ):
                    if es_dev:
                        venta_sem -= abs(imp)
                        articulos_sem += cant_prendas
                        tickets_sem += 1
                    else:
                        venta_sem += imp
                        tickets_sem += 1
                        articulos_sem += arts

            # SOLO EL DÍA EXACTO
            if v_int == target_int:
                if es_dev:
                    venta_dia -= abs(imp)
                    articulos_dia += cant_prendas
                    tickets_dia += 1
                else:
                    venta_dia += imp
                    tickets_dia += 1
                    articulos_dia += arts
        # Total de devoluciones acumuladas hasta el día consultado
        devoluciones_totales_mes = sum(
            importe
            for dia, importe in devoluciones_por_dia_mes.items()
            if dia <= target_date.day
        )

        # RATIOS Y PROMEDIOS

        # RATIOS Y PROMEDIOS
        ticket_medio_dia = (venta_dia / tickets_dia) if tickets_dia > 0 else 0.0
        upt_dia = (articulos_dia / tickets_dia) if tickets_dia > 0 else 0.0
        conversion_dia = (
            ((tickets_dia / clientes_dia) * 100) if clientes_dia > 0 else 0.0
        )

        ticket_medio_sem = (venta_sem / tickets_sem) if tickets_sem > 0 else 0.0
        upt_sem = (articulos_sem / tickets_sem) if tickets_sem > 0 else 0.0

        ticket_medio_mes = (venta_acum_mes / tickets_mes) if tickets_mes > 0 else 0.0
        upt_mes = (articulos_mes / tickets_mes) if tickets_mes > 0 else 0.0

        devs_filtradas = {
            k: v for k, v in devoluciones_acum_dependiente.items() if v > 0
        }
        ranking_ventas = sorted(
            ventas_acum_dependiente.items(), key=lambda x: x[1], reverse=True
        )
        ranking_devs = sorted(
            devs_filtradas.items(), key=lambda x: x[1], reverse=True
        )

        res_upt = []
        for dep, (arts_netos, tkts_netos) in dep_stats_upt_acum.items():
            u_val = (arts_netos / tkts_netos) if tkts_netos > 0 else 0.0
            res_upt.append((dep, max(0.0, u_val)))
        res_upt.sort(key=lambda x: x[1], reverse=True)

        tot_hist = sum(ventas_por_dia_semana)
        pesos_pct = [
            (v / tot_hist * 100) if tot_hist > 0 else 14.28
            for v in ventas_por_dia_semana
        ]

        falta_objetivo = max(0.0, objetivo_mes - venta_acum_mes)
        dias_totales_mes = calendar.monthrange(
            target_date.year, target_date.month
        )[1]
        dias_restantes = max(1, dias_totales_mes - target_date.day)
        media_diaria_necesaria = falta_objetivo / dias_restantes

        # 2. CONSTRUCCIÓN DEL PDF
        nombre_pdf = f"Informe_Direccion_{fecha_str_corta}.pdf"
        doc = SimpleDocTemplate(
            nombre_pdf,
            pagesize=A4,
            rightMargin=0.8 * cm,
            leftMargin=0.8 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.5 * cm,
        )

        styles = getSampleStyleSheet()
        style_title = ParagraphStyle(
            "T",
            parent=styles["Heading1"],
            fontSize=13,
            leading=13,
            textColor=colors.whitesmoke,
        )
        style_date = ParagraphStyle(
            "D",
            parent=styles["Normal"],
            fontSize=9,
            leading=10,
            textColor=colors.whitesmoke,
            alignment=2,
        )
        style_sec = ParagraphStyle(
            "S",
            parent=styles["Normal"],
            fontSize=10,
            leading=10,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#2B5C8F"),
        )
        style_body = ParagraphStyle(
            "B", parent=styles["Normal"], fontSize=7.5, leading=7.5
        )

        elements = []

        # CABECERA Y KPI SUPERIORES
        header_table = Table(
            [
                [
                    Paragraph(
                        "<b>INFORME DE DIRECCIÓN GENERAL</b>", style_title
                    ),
                    Paragraph(
                        f"Fecha Corte: <b>{target_date.strftime('%d/%m/%Y')}</b>",
                        style_date,
                    ),
                ]
            ],
            colWidths=[12.8 * cm, 6.6 * cm],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2B5C8F")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 2 * mm))

        html_izq = f"""
        <b>DÍA ({target_date.strftime('%d/%m')}): {venta_dia:.2f} €</b> | Tkts: <b>{tickets_dia}</b> | Unid: <b>{articulos_dia}</b> | Tm: <b>{ticket_medio_dia:.2f}€</b> | UPT: <b>{upt_dia:.2f}</b> | Conv: <b>{conversion_dia:.1f}%</b><br/>
        <b>SEMANA (Acum. al {target_date.strftime('%d/%m')}): {venta_sem:.2f} €</b> | Tkts: <b>{tickets_sem}</b> | Unid: <b>{articulos_sem}</b> | Tm: <b>{ticket_medio_sem:.2f}€</b> | UPT: <b>{upt_sem:.2f}</b><br/>
        <b>ACUM. MES (al {target_date.strftime('%d/%m')}): {venta_acum_mes:.2f} €</b> | Tkts: <b>{tickets_mes}</b> | Unid: <b>{articulos_mes}</b> | Tm: <b>{ticket_medio_mes:.2f}€</b> | UPT: <b>{upt_mes:.2f}</b>
        """

        html_der = f"""
        <b>OBJETIVO MES: {objetivo_mes:.2f} €</b> | Falta: <b>{falta_objetivo:.2f} €</b><br/>
        Med. Diaria Nec: <b>{media_diaria_necesaria:.2f} €</b> ({dias_restantes} d. rest.)<br/>
        <font color='#C0392B'><b>DEVOLUCIONES MES (al {target_date.strftime('%d/%m')}): {devoluciones_totales_mes:.2f} €</b></font>
        """

        t_sup = Table(
            [[Paragraph(html_izq, style_body), Paragraph(html_der, style_body)]],
            colWidths=[10.8 * cm, 8.6 * cm],
        )
        t_sup.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F7FA")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elements.append(t_sup)
        elements.append(Spacer(1, 3 * mm))

        # BLOQUE 1: VENTAS ACUMULADAS
        elements.append(
            Paragraph(
                f"VENTAS NETAS ACUMULADAS POR DEPENDIENTE (AL {target_date.strftime('%d/%m/%Y')})",
                style_sec,
            )
        )
        elements.append(Spacer(1, 2 * mm))
        elements.append(
            self.crear_bloque_tabla_grafica(
                ranking_ventas,
                "Importe Net.",
                colors.HexColor("#2B5C8F"),
                style_body,
            )
        )
        elements.append(Spacer(1, 3 * mm))

        # BLOQUE 2: DEVOLUCIONES ACUMULADAS
        style_sec_dev = ParagraphStyle(
            "SDEV", parent=style_sec, textColor=colors.HexColor("#C0392B")
        )
        elements.append(
            Paragraph(
                f"DEVOLUCIONES ACUMULADAS POR DEPENDIENTE (AL {target_date.strftime('%d/%m/%Y')})",
                style_sec_dev,
            )
        )
        elements.append(Spacer(1, 2 * mm))
        elements.append(
            self.crear_bloque_tabla_grafica(
                ranking_devs,
                "Devolución",
                colors.HexColor("#C0392B"),
                style_body,
            )
        )
        elements.append(Spacer(1, 3 * mm))

        # BLOQUE 3: RANKING UPT ACUMULADO
        style_sec_upt = ParagraphStyle(
            "SUPT", parent=style_sec, textColor=colors.HexColor("#27AE60")
        )
        elements.append(
            Paragraph(
                f"CALIDAD DE VENTA ACUMULADA (AL {target_date.strftime('%d/%m/%Y')}) - UPT NETO",
                style_sec_upt,
            )
        )
        elements.append(Spacer(1, 2 * mm))
        elements.append(
            self.crear_bloque_tabla_grafica(
                res_upt,
                "UPT Net.",
                colors.HexColor("#27AE60"),
                style_body,
            )
        )
        elements.append(Spacer(1, 3 * mm))

        # BLOQUE 4: PESOS SEMANALES
        style_sec_p = ParagraphStyle(
            "SP", parent=style_sec, textColor=colors.HexColor("#8E44AD")
        )
        elements.append(
            Paragraph("ESTUDIO DE PESOS SEMANALES HISTÓRICOS", style_sec_p)
        )
        elements.append(Spacer(1, 2 * mm))
        data_pesos = list(zip(dias_semana_nombres, pesos_pct))
        elements.append(
            self.crear_bloque_tabla_grafica(
                data_pesos,
                "Peso %",
                colors.HexColor("#8E44AD"),
                style_body,
            )
        )

        doc.build(elements)
        
    def cambiar_grafica_control(self, tipo):
        """Alterna dinámicamente el contenido del panel visual de gráficas."""
        if not hasattr(self, "zona_graficas"):
            return

        # Limpiar la zona donde se renderiza la gráfica actual
        self.zona_graficas.clear_widgets()

        if tipo == "ventas":
            self.titulo_mes.text = "VENTAS DEL MES"
            if hasattr(self, "zona_ventas"):
                self.zona_graficas.add_widget(self.zona_ventas)

        elif tipo == "objetivo":
            self.titulo_mes.text = "SEGUIMIENTO DE OBJETIVO"
            if hasattr(self, "zona_objetivo"):
                self.zona_graficas.add_widget(self.zona_objetivo)

        elif tipo == "rendim":
            self.titulo_mes.text = "INDICADORES DE RENDIMIENTO"
            if hasattr(self, "zona_rendimiento"):
                self.zona_graficas.add_widget(self.zona_rendimiento)

        elif tipo == "equipo":
            self.titulo_mes.text = "DESEMPEÑO DEL EQUIPO"
            if hasattr(self, "zona_equipo"):
                self.zona_graficas.add_widget(self.zona_equipo)

        elif tipo == "devoluciones":
            self.titulo_mes.text = "REGISTRO DE DEVOLUCIONES"
            if hasattr(self, "zona_devoluciones"):
                self.zona_graficas.add_widget(self.zona_devoluciones)




    def build(self):
        # 🎨 1. CAMBIO CLAVE: Establece el fondo oscuro elegante para toda la app
        Window.clearcolor = THEME["bg_app"]

        principal = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        # Barra superior estilizada
        barra = BoxLayout(size_hint=(1, 0.08), spacing=dp(10))
        titulo = Label(text="", font_size=sp(24), color=THEME["text_main"])
        
        # Botón de menú estilizado sin textura gris por defecto
        boton_menu = Button(
            text="MENÚ", 
            size_hint=(0.25, 1),
            background_normal='',
            background_color=THEME["primary"],
            color=THEME["text_main"],
            bold=True,
            font_size=sp(14)
        )

        barra.add_widget(titulo)
        barra.add_widget(boton_menu)

        # Menú desplegable
        menu = DropDown()
        opciones = [
            "Nuevo Día",
            "Introducir Ventas",
            "Dashboard",
            "Informe Diario",
            "Devoluciones",
            "Salir",
        ]

        for opcion in opciones:
            btn = Button(
                text=opcion,
                size_hint_y=None,
                height=dp(50),
                background_normal="",
                background_color=THEME["bg_card"],
                color=THEME["text_main"],
                font_size=sp(14),
            )

            if opcion == "Nuevo Día":
                btn.bind(
                    on_release=lambda x: (menu.dismiss(), self.abrir_nuevo_dia())
                )
            elif opcion == "Introducir Ventas":
                btn.bind(
                    on_release=lambda x: (menu.dismiss(), self.abrir_ventas())
                )
            elif opcion == "Dashboard":
                btn.bind(
                    on_release=lambda x: (
                        menu.dismiss(),
                        self.abrir_dashboard(x),
                    )
                )
            elif opcion == "Informe Diario":
                btn.bind(
                    on_release=lambda x: (
                        menu.dismiss(),
                        self.abrir_informe_diario(x),
                    )
                )
            elif opcion == "Devoluciones":
                btn.bind(
                    on_release=lambda x: (
                        menu.dismiss(),
                        self.abrir_devoluciones(x),
                    )
                )
            else:
                btn.bind(on_release=lambda b: menu.select(b.text))

            menu.add_widget(btn)

        boton_menu.bind(on_release=menu.open)

        # Logo e información con fuentes proporcionales y colores del tema
        logo = Image(source="logo.png", size_hint=(1, 0.7))
        bienvenida = Label(
            text="Bienvenido a VIYUVA", 
            font_size=sp(22), 
            bold=True, 
            color=THEME["text_main"],
            size_hint_y=0.1
        )
        version = Label(
            text="Versión 1.0", 
            font_size=sp(12), 
            color=THEME["text_muted"],
            size_hint_y=0.05
        )

        principal.add_widget(barra)
        principal.add_widget(logo)
        principal.add_widget(bienvenida)
        principal.add_widget(version)

        return principal


if __name__ == "__main__":
    ViyuvaApp().run()
