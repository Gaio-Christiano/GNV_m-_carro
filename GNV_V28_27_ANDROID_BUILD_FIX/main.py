# V28.38 - Android: subclass real, UI primeiro e abas sob demanda
#
# A V28.37 introduziu a inicializacao por etapas, mas usava delegacao via
# __getattr__. Isso e fragil para metodos do aplicativo original que usam
# super(). Nesta versao a classe AndroidGNVApp herda diretamente de
# MobileGNVApp. Assim todos os metodos originais continuam vendo a hierarquia
# correta de classes.
#
# A mudanca estrutural mantida:
# - nao chama MobileGNVApp.build();
# - nao chama _build_all_screens() durante o startup;
# - mostra a interface com a aba Calculos primeiro;
# - usa SQLite em memoria na subida;
# - abre o SQLite persistente depois da UI estar visivel;
# - cria as outras abas somente quando o usuario as abre.

import traceback
from pathlib import Path

import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as app_module


class AndroidGNVApp(app_module.MobileGNVApp):
    """Versao Android do sistema com inicializacao incremental."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built_tabs = set()
        self._real_db_ready = False
        self.startup_log_path = None
        self.startup_status = None

    def _log_startup(self, message):
        text = str(message)
        print(text, flush=True)
        try:
            if self.startup_log_path is not None:
                with Path(self.startup_log_path).open("a", encoding="utf-8") as f:
                    f.write(text + "\n")
        except Exception:
            pass
        try:
            if self.startup_status is not None:
                self.startup_status.text = text
        except Exception:
            pass

    def _show_startup_error(self, etapa, exc):
        bloco = (
            f"ERRO NA ETAPA: {etapa}\n\n"
            f"Tipo: {type(exc).__name__}\n"
            f"Mensagem: {exc}\n\n"
            f"{traceback.format_exc()}"
        )
        self._log_startup(bloco)
        try:
            if self.startup_status is not None:
                self.startup_status.text = bloco
        except Exception:
            pass

    def build(self):
        """Constroi somente a casca e a primeira aba; nunca o build desktop completo."""
        try:
            self._log_startup("V28.38 - iniciando")

            self.title = app_module.APP_TITLE
            self.idioma = "pt-BR"

            # Armazenamento privado do proprio aplicativo.
            self.base_dir = Path(self.user_data_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(self.base_dir / "gnv_dados.db")
            self.config_path = self.base_dir / "configuracoes.json"
            self.startup_log_path = self.base_dir / "startup_android.log"
            self.startup_log_path.write_text("V28.38\n", encoding="utf-8")

            self._log_startup("ETAPA 1/6 - armazenamento privado OK")

            # Banco temporario apenas para a subida. Nao bloqueia a interface.
            self.banco = app_module.BancoGNV(":memory:")
            self.banco.conectar()
            self.banco.criar_tabela()
            self.banco.criar_indices()
            self._log_startup("ETAPA 2/6 - SQLite em memoria OK")

            self.formula_pt = self._load_formula_pt()
            self.colors = self._default_colors()
            self._colors_personalizadas = False
            self._visual_ready = False

            self.sm = app_module.ScreenManager()
            self.screen_names = []
            keys = (
                "Cálculos", "Abastecimentos", "ANP", "Aquecimento / Compressão",
                "Histórico de Abastecimentos", "Banco SQLite", "Exportação / Excel",
                "Gráficos de Abastecimento", "Configurações do Sistema",
                "Fórmulas e Física", "Total de Abastecimentos", "Créditos"
            )
            for i, key in enumerate(keys):
                name = f"screen_{i}"
                self.screen_names.append(name)
                self.sm.add_widget(app_module.MobileScreen(key, name=name))

            root = app_module.BoxLayout(
                orientation="vertical", spacing=app_module.dp(4), padding=app_module.dp(5)
            )

            self.header = app_module.Label(
                text=app_module.APP_TITLE,
                size_hint_y=None,
                height=app_module.dp(42),
                font_size=app_module.sp(15),
                bold=True,
            )
            root.add_widget(self.header)

            nav = app_module.BoxLayout(
                size_hint_y=None,
                height=app_module.dp(46),
                spacing=app_module.dp(4),
            )

            self.tab_spinner = app_module.Spinner(
                text="Cálculos",
                values=tuple(self.screen_names_for_language()),
                size_hint_x=0.78,
            )
            self.tab_spinner.bind(text=self._go_from_spinner)
            nav.add_widget(self.tab_spinner)

            self.lang_spinner = app_module.Spinner(
                text="pt-BR",
                values=app_module.IDIOMAS_DISPONIVEIS,
                size_hint_x=0.22,
            )
            self.lang_spinner.bind(text=self.change_language)
            nav.add_widget(self.lang_spinner)
            root.add_widget(nav)

            self.startup_status = app_module.Label(
                text="Loading...",
                size_hint_y=None,
                height=app_module.dp(28),
                font_size=app_module.sp(11),
            )
            root.add_widget(self.startup_status)
            root.add_widget(self.sm)

            self.footer = app_module.Label(
                text="Analista de Sistemas e Pesquisador - Christiano T.Gaio - Desenvolvedor | Projeto iniciado o Desenvolvimento em 06/2026",
                size_hint_y=None,
                height=app_module.dp(34),
                font_size=app_module.sp(9),
                halign="center",
                valign="middle",
            )
            self.footer.bind(
                size=lambda w, *_: setattr(w, "text_size", w.size)
            )
            root.add_widget(self.footer)

            # SOMENTE a primeira aba neste momento.
            self._ensure_tab(0)
            self._log_startup("ETAPA 3/6 - aba Cálculos carregada")

            # Tudo que pode demorar ou acessar arquivos persistentes fica fora
            # do primeiro frame.
            app_module.Clock.schedule_once(self._finish_android_startup, 0.5)
            app_module.Clock.schedule_once(self._apply_android_visuals, 0.6)

            return root

        except BaseException as exc:
            self._show_startup_error("build Android", exc)
            # Mesmo em erro, tenta deixar uma tela Kivy visivel.
            return app_module.Label(
                text=f"ERRO DE INICIALIZAÇÃO\n\n{type(exc).__name__}: {exc}",
                halign="left",
                valign="top",
            )

    def _ensure_tab(self, idx):
        """Carrega uma única aba na primeira solicitação do usuário."""
        if idx in self._built_tabs:
            return

        methods = (
            "_build_calculos",
            "_build_abastecimentos",
            "_build_anp",
            "_build_compressao",
            "_build_historico",
            "_build_sqlite",
            "_build_excel",
            "_build_graficos",
            "_build_config",
            "_build_formulas",
            "_build_total",
            "_build_creditos",
        )
        if idx < 0 or idx >= len(methods):
            raise IndexError(f"Aba inválida: {idx}")

        nome = self.screen_names_for_language()[idx]
        self._log_startup(f"ABRINDO ABA {idx + 1}/12 - {nome}")
        getattr(self, methods[idx])()
        self._built_tabs.add(idx)

        try:
            self._apply_result_styles_to_all_tabs()
        except Exception:
            pass

    def _go_from_spinner(self, _spinner, text):
        try:
            names = self.screen_names_for_language()
            idx = names.index(text)
            self._ensure_tab(idx)
            self.sm.current = self.screen_names[idx]
            try:
                self._apply_language()
            except Exception:
                pass
        except BaseException as exc:
            self._show_startup_error(f"abrir aba: {text}", exc)

    def change_language(self, _spinner, idioma):
        try:
            self.idioma = idioma
            current_name = self.sm.current
            idx = self.screen_names.index(current_name)
            self.tab_spinner.values = tuple(self.screen_names_for_language())
            self._ensure_tab(idx)
            self.tab_spinner.text = self.screen_names_for_language()[idx]
            self._apply_language()
            app_module.Clock.schedule_once(lambda _dt: self._apply_colors(), 0)
            try:
                self._save_config()
            except Exception:
                pass
        except BaseException as exc:
            self._show_startup_error("troca de idioma", exc)

    def _apply_android_visuals(self, _dt):
        try:
            self._apply_language()
            self._visual_ready = True
            self._apply_colors()
            self._log_startup("ETAPA 5/6 - visual aplicado")
        except BaseException as exc:
            self._show_startup_error("visual", exc)

    def _finish_android_startup(self, _dt):
        try:
            self._log_startup("ETAPA 4/6 - abrindo SQLite persistente")

            base = Path(self.db_path).parent
            base.mkdir(parents=True, exist_ok=True)

            # Teste real de escrita no diretorio privado.
            teste = base / ".storage_test"
            teste.write_text("ok", encoding="utf-8")
            teste.unlink(missing_ok=True)

            real_db = app_module.BancoGNV(self.db_path)
            real_db.conectar()
            real_db.criar_tabela()
            real_db.criar_indices()

            antigo = getattr(self, "banco", None)
            self.banco = real_db
            self._real_db_ready = True

            if antigo is not None:
                try:
                    antigo.conexao.close()
                except Exception:
                    pass

            # Atualiza somente as telas que ja foram criadas.
            for nome in (
                "_refresh_history",
                "_refresh_sqlite",
                "_refresh_total",
                "_refresh_chart",
            ):
                fn = getattr(self, nome, None)
                if callable(fn):
                    try:
                        fn()
                    except Exception:
                        pass

            self._log_startup("ETAPA 6/6 - SISTEMA PRONTO")
            if self.startup_status is not None:
                self.startup_status.text = "Sistema pronto"

        except BaseException as exc:
            # O aplicativo permanece aberto mesmo que o armazenamento falhe.
            self._show_startup_error("SQLite persistente", exc)


if __name__ == "__main__":
    AndroidGNVApp().run()
