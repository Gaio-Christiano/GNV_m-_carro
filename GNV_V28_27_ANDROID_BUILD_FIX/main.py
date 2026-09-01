# V28.43 - entrada Android resiliente
#
# O APK deve abrir a interface ANTES de executar qualquer operação pesada.
# As abas são montadas uma por vez dentro do ciclo do Kivy. Se uma aba ou
# inicialização específica falhar, o aplicativo permanece aberto e mostra o
# erro naquela aba, em vez de encerrar todo o processo Android.

import importlib
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


class AndroidGNVApp(App):
    """Launcher Android independente e resiliente."""

    def build(self):
        self.title = "Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV - V28.43"
        self._boot_status = Label(
            text="Loading...\n\nInicializando o sistema GNV...",
            font_size=sp(18),
            halign="center",
            valign="middle",
        )
        self._boot_status.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root = BoxLayout(padding=dp(24))
        root.add_widget(self._boot_status)

        # O primeiro frame precisa ser entregue ao Android antes de importar,
        # abrir SQLite ou construir as 12 telas.
        Clock.schedule_once(self._boot, 0.15)
        return root

    def _status(self, text):
        try:
            self._boot_status.text = text
        except Exception:
            pass

    def _show_fatal(self, title, exc):
        details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        try:
            root = self.root
            root.clear_widgets()
            box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
            box.add_widget(Label(
                text=title,
                font_size=sp(18),
                bold=True,
                size_hint_y=None,
                height=dp(55),
            ))
            box.add_widget(Label(
                text=details,
                font_size=sp(10),
                halign="left",
                valign="top",
            ))
            root.add_widget(box)
        finally:
            print(details)

    def _show_screen_error(self, screen, method_name, exc):
        details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        try:
            screen.clear_widgets()
            screen.add_widget(Label(
                text=(
                    "ERRO AO CARREGAR ESTA ABA\n\n"
                    f"{method_name}\n\n"
                    f"{details}"
                ),
                halign="left",
                valign="top",
                font_size=sp(10),
            ))
        finally:
            print(details)

    def _boot(self, _dt):
        try:
            self._status("Loading...\n\nCarregando bibliotecas do sistema...")
            module = importlib.import_module(APP_MODULE_NAME)

            base_cls = getattr(module, "MobileGNVApp")
            self._base_cls = base_cls
            self._module = module

            # Reaproveita os métodos/classes do aplicativo original, mas a
            # instância que executa é ESTE App, que pertence ao Kivy desde o
            # começo. Não alteramos __class__ e não chamamos App.build().
            self._prepare_model(module)
            self._prepare_ui(module)

            self._status("Loading...\n\nAbrindo a calculadora...")
            Clock.schedule_once(self._build_next_screen, 0.05)

        except BaseException as exc:
            self._show_fatal("O aplicativo encontrou um erro ao iniciar", exc)

    def _prepare_model(self, module):
        # Atributos comuns usados pelos métodos do aplicativo original.
        self.instance = self
        self.title = getattr(module, "APP_TITLE", self.title)
        self.idioma = "pt-BR"
        self.base_dir = __import__("pathlib").Path(self.user_data_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = str(self.base_dir / "gnv_dados.db")
        self.config_path = self.base_dir / "configuracoes.json"

        try:
            self.banco = module.BancoGNV(self.db_path)
            self.banco.conectar()
            self.banco.criar_tabela()
            self.banco.criar_indices()
        except BaseException as exc:
            # SQLite nunca deve impedir o aplicativo de abrir.
            print("Aviso SQLite:", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            try:
                self.banco = module.BancoGNV(":memory:")
                self.banco.conectar()
                self.banco.criar_tabela()
                self.banco.criar_indices()
            except BaseException:
                self.banco = None

        self.formula_pt = self._safe_call("_load_formula_pt", "")
        self.colors = self._safe_call("_default_colors", {}) or {}
        self._colors_personalizadas = False
        self._visual_ready = False

    def _safe_call(self, name, default=None):
        fn = getattr(self, name, None)
        if not callable(fn):
            return default
        try:
            return fn()
        except BaseException as exc:
            print(f"Aviso em {name}:\n", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            return default

    def _prepare_ui(self, module):
        self.sm = ScreenManager()
        self.screen_names = []
        self._tab_defs = [
            ("Cálculos", "_build_calculos"),
            ("Abastecimentos", "_build_abastecimentos"),
            ("ANP", "_build_anp"),
            ("Aquecimento / Compressão", "_build_compressao"),
            ("Histórico de Abastecimentos", "_build_historico"),
            ("Banco SQLite", "_build_sqlite"),
            ("Exportação / Excel", "_build_excel"),
            ("Gráficos de Abastecimento", "_build_graficos"),
            ("Configurações do Sistema", "_build_config"),
            ("Fórmulas e Física", "_build_formulas"),
            ("Total de Abastecimentos", "_build_total"),
            ("Créditos", "_build_creditos"),
        ]

        MobileScreen = getattr(module, "MobileScreen")
        for i, (title, _method) in enumerate(self._tab_defs):
            name = f"screen_{i}"
            self.screen_names.append(name)
            self.sm.add_widget(MobileScreen(title, name=name))

        root = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(5))
        self.header = Label(
            text=getattr(module, "APP_TITLE", self.title),
            size_hint_y=None,
            height=dp(42),
            font_size=sp(15),
            bold=True,
        )
        root.add_widget(self.header)

        # Em vez dos controles completos de navegação logo no startup,
        # usamos o spinner original somente depois que a primeira aba existir.
        nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(4))
        Spinner = getattr(module, "Spinner")
        self.tab_spinner = Spinner(
            text="Cálculos",
            values=tuple(self.screen_names_for_language()),
            size_hint_x=0.78,
        )
        self.tab_spinner.bind(text=self._go_from_spinner)
        nav.add_widget(self.tab_spinner)
        self.lang_spinner = Spinner(
            text="pt-BR",
            values=getattr(module, "IDIOMAS_DISPONIVEIS", ("pt-BR",)),
            size_hint_x=0.22,
        )
        self.lang_spinner.bind(text=self.change_language)
        nav.add_widget(self.lang_spinner)
        root.add_widget(nav)
        root.add_widget(self.sm)

        self.footer = Label(
            text="Analista de Sistemas e Pesquisador - Christiano T.Gaio - Desenvolvedor",
            size_hint_y=None,
            height=dp(34),
            font_size=sp(9),
            halign="center",
            valign="middle",
        )
        self.footer.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root.add_widget(self.footer)

        # self.root existe neste ponto: o App já está rodando.
        self.root.clear_widgets()
        self.root.add_widget(root)
        self._ui_root = root
        self._tab_index = 0

    def _build_next_screen(self, _dt):
        if self._tab_index >= len(self._tab_defs):
            self._finish_boot()
            return

        title, method_name = self._tab_defs[self._tab_index]
        index = self._tab_index
        self._status(f"Loading...\n\nCarregando: {title}")
        try:
            method = getattr(self, method_name)
            method()
        except BaseException as exc:
            print(f"Falha na aba {index} - {title}:\n", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            try:
                screen = self.sm.get_screen(self.screen_names[index])
                self._show_screen_error(screen, method_name, exc)
            except BaseException as nested:
                print("Falha adicional ao exibir diagnóstico:", nested)

        self._tab_index += 1
        Clock.schedule_once(self._build_next_screen, 0.03)

    def _finish_boot(self):
        self._status("Inicialização concluída.")
        try:
            self._safe_call("_load_config", None)
            self._safe_call("_apply_language", None)
            self._safe_call("_mark_visual_ready", None)
        except BaseException as exc:
            print("Aviso final de inicialização:", exc)
        Clock.schedule_once(lambda *_: self._clear_boot_status(), 0.15)

    def _clear_boot_status(self):
        # A tela principal já substituiu o conteúdo do root. O método existe
        # apenas para manter o callback seguro caso uma versão futura mantenha
        # um indicador de inicialização separado.
        pass


if __name__ == "__main__":
    AndroidGNVApp().run()
