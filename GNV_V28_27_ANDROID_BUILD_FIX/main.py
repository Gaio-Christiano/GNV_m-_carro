# V28.41 - entrada Android simplificada
# Uma unica instancia real de MobileGNVApp. Sem troca dinamica de __class__.

import importlib
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


def safe_text(exc):
    return f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}"


def write_log(base, lines):
    try:
        base = Path(base)
        base.mkdir(parents=True, exist_ok=True)
        (base / "startup_android.log").write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


class AndroidStartupApp(App):
    def build(self):
        self.title = "GNV V28.41"
        self._log_lines = ["GNV V28.41 - inicializacao Android", ""]
        self.status = Label(text="INICIANDO KIVY...", halign="left", valign="top")
        self.status.bind(
            size=lambda w, *_: setattr(w, "text_size", (max(1, w.width - 30), None))
        )
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)
        root.add_widget(self.status)
        Clock.schedule_once(self._start_gnv, 0.20)
        return root

    def _start_gnv(self, _dt):
        base = Path(self.user_data_dir)
        self._log_lines.append("ETAPA 1: Kivy inicializado")
        self.status.text = "GNV V28.41\n\nETAPA 1/3 - Kivy: OK\nETAPA 2/3 - carregando sistema GNV..."

        try:
            module = importlib.import_module(APP_MODULE_NAME)
            real_app = module.MobileGNVApp()
            self._log_lines.append("ETAPA 2: modulo GNV importado")
            real_root = real_app.build()
            real_app.root = real_root
            self.real_app = real_app
            self.real_module = module
            self._log_lines.append("ETAPA 3: MobileGNVApp.build() concluido")
            write_log(base, self._log_lines)
            self.root.clear_widgets()
            self.root.add_widget(real_root)
        except BaseException as exc:
            self._log_lines.extend(["ETAPA 2/3: FALHA", safe_text(exc)])
            write_log(base, self._log_lines)
            self.root.clear_widgets()
            self.root.add_widget(
                Label(
                    text="ERRO AO INICIAR O SISTEMA GNV\n\n" + safe_text(exc),
                    halign="left",
                    valign="top",
                )
            )


if __name__ == "__main__":
    AndroidStartupApp().run()
