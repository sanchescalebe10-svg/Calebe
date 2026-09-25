import flet as ft
import json
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from datetime import datetime


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main(page: ft.Page):

    page.title = "Finanças"
    page.bgcolor = "#121212"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    ARQUIVO = "dados_desktop.json"

    borda_normal = "#3a3a3a"

    saldo = {"valor": 0.0}
    gastos_total = {"valor": 0.0}
    orcamento = {"valor": 0.0}

    # =========================================
    # CATEGORIAS DOS GRÁFICOS
    # =========================================
    gastos_categoria = {
        "Moradia": 0,
        "Transporte": 0,
        "Saúde": 0,
        "Educação": 0,
        "Lazer": 0,
        "Alimentação": 0
    }

    grafico_categoria = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO
    )

    lista = ft.Column(
        scroll=ft.ScrollMode.AUTO
    )

    texto_vazio = ft.Text(
        "Ainda não há transações",
        color="white54",
        size=14
    )

    lista.controls.append(texto_vazio)

    painel_aberto = {"valor": False}

    # ---------------- NOTIFICAÇÃO ---------------- #
    def notify(msg, color="#333"):

        sb = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=1500
        )

        page.overlay.append(sb)

        sb.open = True

        page.update()

    # =========================================
    # GRÁFICO EM COLUNAS
    # =========================================
    def atualizar_grafico():

        grafico_categoria.controls.clear()

        cores = {
            "Moradia": "#3B82F6",
            "Transporte": "#10B981",
            "Saúde": "#EF4444",
            "Educação": "#F59E0B",
            "Lazer": "#8B5CF6",
            "Alimentação": "#06B6D4"
        }

        maior = max(
            gastos_categoria.values()
        ) if max(
            gastos_categoria.values()
        ) > 0 else 1

        barras = []

        for categoria_nome, valor in gastos_categoria.items():

            altura = max(
                15,
                (valor / maior) * 140
            )

            barras.append(

                ft.Column(

                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                    controls=[

                        ft.Text(
                            formatar_brl(valor),
                            color="white70",
                            size=10
                        ),

                        ft.Container(
                            width=40,
                            height=altura,
                            bgcolor=cores[categoria_nome],
                            border_radius=8
                        ),

                        ft.Text(
                            categoria_nome,
                            color="white",
                            size=10,
                            text_align=ft.TextAlign.CENTER
                        )

                    ]
                )
            )

        grafico_categoria.controls.append(

            ft.Row(
                controls=barras,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END
            )
        )

        page.update()

    # ---------------- SALVAR DADOS ---------------- #
    def salvar_dados():

        transacoes = []

        for item in lista.controls:

            if isinstance(item, ft.Text) and item != texto_vazio:
                transacoes.append(item.value)

        dados = {
            "saldo": saldo["valor"],
            "gastos_total": gastos_total["valor"],
            "orcamento": orcamento["valor"],
            "gastos_categoria": gastos_categoria,
            "transacoes": transacoes
        }

        with open(ARQUIVO, "w") as f:
            json.dump(dados, f)

    # ---------------- EXPORTAR PDF ---------------- #
    def exportar_pdf(e=None):

        try:

            nome_arquivo = "relatorio_financeiro.pdf"

            pdf = SimpleDocTemplate(
                nome_arquivo,
                pagesize=letter
            )

            styles = getSampleStyleSheet()

            elementos = []

            elementos.append(
                Paragraph(
                    "Relatório Financeiro",
                    styles["Title"]
                )
            )

            elementos.append(Spacer(1, 20))

            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

            elementos.append(
                Paragraph(
                    f"Data: {data_atual}",
                    styles["BodyText"]
                )
            )

            elementos.append(Spacer(1, 20))

            elementos.append(
                Paragraph(
                    f"Saldo Atual: {formatar_brl(saldo['valor'])}",
                    styles["Heading2"]
                )
            )

            elementos.append(
                Paragraph(
                    f"Gastos Totais: {formatar_brl(gastos_total['valor'])}",
                    styles["Heading2"]
                )
            )

            elementos.append(
                Paragraph(
                    f"Orçamento: {formatar_brl(orcamento['valor'])}",
                    styles["Heading2"]
                )
            )

            economia = saldo["valor"] - gastos_total["valor"]

            elementos.append(
                Paragraph(
                    f"Economia: {formatar_brl(economia)}",
                    styles["Heading2"]
                )
            )

            elementos.append(Spacer(1, 25))

            elementos.append(
                Paragraph(
                    "Transações",
                    styles["Heading1"]
                )
            )

            elementos.append(Spacer(1, 10))

            encontrou = False

            for item in lista.controls:

                if isinstance(item, ft.Text) and item != texto_vazio:

                    encontrou = True

                    elementos.append(
                        Paragraph(
                            f"• {item.value}",
                            styles["BodyText"]
                        )
                    )

                    elementos.append(Spacer(1, 5))

            if not encontrou:

                elementos.append(
                    Paragraph(
                        "Nenhuma transação encontrada.",
                        styles["BodyText"]
                    )
                )

            pdf.build(elementos)

            try:
                os.startfile(nome_arquivo)

            except:
                pass

            notify(
                "PDF exportado com sucesso",
                "#0073F7"
            )

        except Exception as erro:

            notify(
                f"Erro ao exportar PDF: {erro}",
                "#D50000"
            )

    saldo_texto = ft.Text(
        "R$ 0,00",
        size=24,
        color="#50C878"
    )

    gastos_texto = ft.Text(
        "R$ 0,00",
        size=24,
        color="#FF5C5C"
    )

    economia_texto = ft.Text(
        "R$ 0,00",
        size=24,
        color="#0073F7"
    )

    orcamento_texto = ft.Text(
        "R$ 0,00",
        size=24,
        color="white"
    )

    progresso = ft.ProgressBar(
        value=0,
        width=180
    )

    # ---------------- UPDATE ---------------- #
    def atualizar_cards():

        saldo_texto.value = formatar_brl(
            saldo["valor"]
        )

        gastos_texto.value = formatar_brl(
            gastos_total["valor"]
        )

        economia_texto.value = formatar_brl(
            saldo["valor"] - gastos_total["valor"]
        )

        orcamento_texto.value = formatar_brl(
            orcamento["valor"]
        )

        if orcamento["valor"] > 0:

            porcentagem = (
                gastos_total["valor"] /
                orcamento["valor"]
            )

        else:
            porcentagem = 0

        progresso.value = min(
            porcentagem,
            1.0
        )

        if porcentagem < 0.5:
            progresso.color = "#00C853"

        elif porcentagem < 0.8:
            progresso.color = "#FFD600"

        else:
            progresso.color = "#D50000"

        atualizar_grafico()

        page.update()

    # ---------------- CARREGAR DADOS ---------------- #
    def carregar_dados():

        if os.path.exists(ARQUIVO):

            with open(ARQUIVO, "r") as f:
                dados = json.load(f)

            saldo["valor"] = dados.get(
                "saldo",
                0.0
            )

            gastos_total["valor"] = dados.get(
                "gastos_total",
                0.0
            )

            orcamento["valor"] = dados.get(
                "orcamento",
                0.0
            )

            categorias_salvas = dados.get(
                "gastos_categoria",
                {}
            )

            for k in gastos_categoria:
                gastos_categoria[k] = categorias_salvas.get(k, 0)

            lista.controls.clear()

            transacoes = dados.get(
                "transacoes",
                []
            )

            if transacoes:

                for t in transacoes:

                    lista.controls.append(
                        ft.Text(
                            t,
                            color="white"
                        )
                    )

            else:
                lista.controls.append(
                    texto_vazio
                )

            atualizar_cards()
            atualizar_grafico()

    # ---------------- FUNÇÕES ---------------- #
    def definir_saldo(e):

        try:

            saldo["valor"] = float(
                saldo_input.value.replace(",", ".")
            )

            atualizar_cards()

            salvar_dados()

            saldo_input.value = ""

            notify(
                "Saldo adicionado",
                "#00C853"
            )

        except:

            notify(
                "Digite um saldo válido",
                "#D50000"
            )

    def adicionar_gasto(e):

        try:

            valor = float(
                valor_input.value.replace(",", ".")
            )

            if valor > saldo["valor"]:

                notify(
                    "Saldo insuficiente",
                    "#D50000"
                )

                return

            saldo["valor"] -= valor

            gastos_total["valor"] += valor

            gastos_categoria[categoria.value] += valor

            if texto_vazio in lista.controls:
                lista.controls.remove(texto_vazio)

            lista.controls.append(

                ft.Text(
                    f"{categoria.value} - "
                    f"{descricao_input.value}: "
                    f"{formatar_brl(valor)}",

                    color="white"
                )
            )

            valor_input.value = ""
            descricao_input.value = ""

            atualizar_cards()

            salvar_dados()

            notify(
                "Transação feita",
                "#919191"
            )

        except:

            notify(
                "Valor inválido",
                "#D50000"
            )

    def definir_orcamento(e):

        try:

            orcamento["valor"] = float(
                orcamento_input.value.replace(",", ".")
            )

            atualizar_cards()

            salvar_dados()

            orcamento_input.value = ""

            notify(
                "Orçamento definido",
                "#0073F7"
            )

        except:

            notify(
                "Orçamento inválido",
                "#D50000"
            )

    def toggle_painel(e):

        painel_aberto["valor"] = not painel_aberto["valor"]

        painel_direita.visible = painel_aberto["valor"]

        page.update()

    # ---------------- RESET ---------------- #
    def resetar(e):

        if os.path.exists(ARQUIVO):
            os.remove(ARQUIVO)

        saldo["valor"] = 0.0
        gastos_total["valor"] = 0.0
        orcamento["valor"] = 0.0

        for k in gastos_categoria:
            gastos_categoria[k] = 0

        lista.controls.clear()

        lista.controls.append(texto_vazio)

        saldo_input.value = ""
        valor_input.value = ""
        descricao_input.value = ""
        orcamento_input.value = ""

        categoria.value = None

        atualizar_cards()
        atualizar_grafico()

        notify(
            "Dados resetados",
            "#FF5C5C"
        )

    # ---------------- FECHAR PAINEL ---------------- #
    def fechar_painel(e=None):

        painel_aberto["valor"] = False

        painel_direita.visible = False

        page.update()

    # ---------------- PAINEL ---------------- #
    painel_direita = ft.Container(
        width=320,
        height=520,
        padding=15,
        border_radius=12,
        bgcolor="#1E1E1E",

        border=ft.border.all(
            1,
            "#9B9B9B"
        ),

        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="black"
        ),

        visible=False,

        content=ft.Column([

            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                controls=[

                    ft.Text(
                        "Transações",
                        size=18,
                        color="white"
                    ),

                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color="red",
                        tooltip="Fechar",
                        on_click=fechar_painel
                    )
                ]
            ),

            ft.Divider(color="white30"),

            lista
        ])
    )

    # ---------------- COMPONENTES ---------------- #
    def card(titulo, valor, icone):

        return ft.Container(
            expand=True,
            height=85,
            padding=12,
            border_radius=8,

            border=ft.border.all(
                1,
                borda_normal
            ),

            bgcolor="#2B2B2B",

            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                controls=[

                    ft.Column([
                        ft.Text(
                            titulo,
                            color="white70",
                            size=12
                        ),

                        valor
                    ]),

                    ft.Icon(
                        icone,
                        color="white70",
                        size=26
                    )
                ]
            )
        )

    def grafico_card(titulo, icone):

        return ft.Container(
            expand=True,
            height=260,
            bgcolor="#1E1E1E",

            border=ft.border.all(
                1,
                borda_normal
            ),

            border_radius=8,
            padding=12,

            content=ft.Column([

                ft.Row([
                    ft.Text(
                        titulo,
                        color="white",
                        size=14
                    ),

                    ft.Icon(
                        icone,
                        color="white70",
                        size=22
                    )
                ]),

                ft.Container(expand=True)

            ])
        )

    # ---------------- HEADER ---------------- #
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

        controls=[

            ft.Text(
                "Finanças Pessoais",
                size=26,
                color="white"
            ),

            ft.Row([

                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=toggle_painel
                ),

                ft.IconButton(
                    icon=ft.Icons.PICTURE_AS_PDF,
                    icon_color="#0073F7",
                    tooltip="Exportar PDF",
                    on_click=exportar_pdf
                ),

                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="red",
                    on_click=resetar
                )

            ])
        ]
    )

    # ---------------- INPUTS ---------------- #
    saldo_input = ft.TextField(
        label="Saldo inicial",
        expand=2
    )

    categoria = ft.Dropdown(
        label="Categoria",

        options=[
            ft.dropdown.Option(c)

            for c in [
                "Moradia",
                "Transporte",
                "Saúde",
                "Educação",
                "Lazer",
                "Alimentação"
            ]
        ],

        expand=2
    )

    descricao_input = ft.TextField(
        label="Descrição",
        expand=2
    )

    valor_input = ft.TextField(
        label="Valor",
        expand=2
    )

    orcamento_input = ft.TextField(
        label="Orçamento",
        expand=2
    )

    inputs = ft.Row([

        saldo_input,
        categoria,
        descricao_input,
        valor_input,
        orcamento_input,

        ft.ElevatedButton(
            "Definir saldo",
            on_click=definir_saldo
        ),

        ft.ElevatedButton(
            "Adicionar",
            on_click=adicionar_gasto
        ),

        ft.ElevatedButton(
            "Definir orçamento",
            on_click=definir_orcamento
        )

    ], spacing=8)

    # ---------------- CARDS ---------------- #
    row_cards = ft.Row([

        card(
            "Saldo",
            saldo_texto,
            ft.Icons.WALLET
        ),

        card(
            "Gastos",
            gastos_texto,
            ft.Icons.TRENDING_DOWN
        ),

        card(
            "Economia",
            economia_texto,
            ft.Icons.SAVINGS
        ),

        ft.Container(
            expand=True,
            height=85,
            padding=12,
            border_radius=8,

            border=ft.border.all(
                1,
                borda_normal
            ),

            bgcolor="#2B2B2B",

            content=ft.Column([

                ft.Text(
                    "Orçamento",
                    color="white70",
                    size=12
                ),

                orcamento_texto,

                progresso
            ])
        )

    ], spacing=6)

    # ---------------- GRÁFICOS ---------------- #
    graficos = ft.Column([

        ft.Row([

            ft.Container(
                expand=True,
                height=260,
                bgcolor="#1E1E1E",

                border=ft.border.all(
                    1,
                    borda_normal
                ),

                border_radius=8,
                padding=12,

                content=ft.Column([

                    ft.Row([

                        ft.Text(
                            "Gastos por Categoria",
                            color="white",
                            size=14
                        ),

                        ft.Icon(
                            ft.Icons.BAR_CHART,
                            color="white70",
                            size=22
                        )

                    ]),

                    ft.Divider(color="white24"),

                    grafico_categoria

                ])
            ),

            grafico_card(
                "Evolução do Saldo",
                ft.Icons.SHOW_CHART
            ),

        ], spacing=6),

        ft.Row([

            grafico_card(
                "Gastos vs Orçamento",
                ft.Icons.BAR_CHART
            ),

            grafico_card(
                "Progresso do Orçamento",
                ft.Icons.TRACK_CHANGES
            ),

        ], spacing=6),

    ], spacing=6)

    # ---------------- LAYOUT ---------------- #
    layout = ft.Row([

        ft.Column([
            header,
            ft.Divider(color="white"),
            inputs,
            row_cards,
            graficos
        ], expand=True),

        painel_direita

    ])

    page.add(layout)

    carregar_dados()


ft.app(target=main)