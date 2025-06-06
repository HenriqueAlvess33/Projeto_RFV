# Importa as bibliotecas necessárias
# Este script realiza a segmentação de clientes utilizando o modelo RFV (Recência, Frequência e Valor) em uma aplicação Streamlit. O objetivo é permitir o upload de um arquivo de compras, calcular os indicadores RFV para cada cliente e exibir os resultados de forma interativa.
# Funções principais:
# - recencia_class(x, r, q_dict): Classifica a recência de um cliente em quartis ('A', 'B', 'C', 'D'), onde 'A' representa os clientes mais recentes.
# - frequencia_class(x, f, q_dict): Classifica a frequência ou valor de um cliente em quartis ('A', 'B', 'C', 'D'), onde 'A' representa os clientes mais frequentes ou de maior valor.
# - main(): Configura a página do Streamlit, definindo título, layout e ícone.
# Fluxo do script:
# 1. Configura a interface do Streamlit, incluindo título, imagem centralizada e instruções na barra lateral.
# 2. Permite o upload de um arquivo de compras nos formatos CSV ou XLSX.
# 3. Lê o arquivo enviado e exibe os dados de compras, se solicitado pelo usuário.
# 4. Calcula os indicadores RFV:
#     - Recência: Dias desde a última compra de cada cliente.
#     - Frequência: Número de compras realizadas por cada cliente.
#     - Valor: Soma do valor gasto por cada cliente.
# 5. Classifica cada indicador em quartis, atribuindo rótulos ('A', 'B', 'C', 'D') para facilitar a segmentação.
# 6. Exibe a tabela RFV resultante, permitindo ao usuário visualizar os dados processados.
# Parâmetros esperados no arquivo de entrada:
# - 'ID_cliente': Identificador único do cliente.
# - 'DiaCompra': Data da compra (deve ser convertível para datetime).
# - 'CodigoCompra': Identificador da compra (usado para contar frequência).
# - 'ValorTotal': Valor monetário da compra (usado para somar o valor total gasto por cliente).
# O script é indicado para análises de segmentação de clientes em projetos de marketing, CRM ou ciência de dados, facilitando a identificação de grupos de clientes com diferentes perfis de comportamento de compra.

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

from io import BytesIO


def df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def recencia_class(x, r, q_dict):
    if x <= q_dict[r][0.25]:
        return "A"
    elif x <= q_dict[r][0.5]:
        return "B"
    elif x <= q_dict[r][0.75]:
        return "C"
    else:
        return "D"


def frequencia_class(x, f, q_dict):
    if x <= q_dict[f][0.25]:
        return "D"
    elif x <= q_dict[f][0.5]:
        return "C"
    elif x <= q_dict[f][0.75]:
        return "B"
    else:
        return "A"


def selecao_valores_categoricos(relatorio, col, selecionados, verificacao):
    if verificacao == True:
        return relatorio
    else:
        return relatorio.loc[relatorio[col] == selecionados].reset_index(drop=True)


def main():
    st.set_page_config(
        page_title="Banco Nacional - RFV",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="ícone_banco_nacional.png",
    )


main()

if "comentarios_rfv" not in st.session_state:
    st.session_state["comentarios_rfv"] = {}

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro&display=swap" rel="stylesheet">

    <h1 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 2.5em;'>
        <strong>Definição de conjunto de clientes RFV</strong>
    </h1>
    """,
    unsafe_allow_html=True,
)

# Define o caminho da imagem do rótulo do aplicativo
image_rotulo_app = "Banco_Nacional_8394.png"

# Cria três colunas na página, sendo a coluna do meio (col2) maior para centralizar a imagem
col1, col2, col3 = st.columns([1, 2, 1])

# Exibe a imagem do rótulo do aplicativo centralizada na coluna do meio
with col2:
    st.image(image_rotulo_app, use_container_width=True)


# Adiciona uma mensagem na barra lateral do Streamlit para instruir o usuário a fazer upload do arquivo
st.sidebar.markdown("Faça o upload do arquivo de compras para calcular o modelo RFV.")

# Cria um componente de upload de arquivo na barra lateral, aceitando arquivos CSV e XLSX
uploaded_file = st.sidebar.file_uploader(
    "Dataset para segregar clientes", type=["csv", "xlsx"]
)


# Detalhes do código para upload de conjunto de dados de compras e cálculo do modelo RFV:
# Este código permite ao usuário fazer upload de um arquivo contendo dados de compras, processa esses dados para calcular os indicadores de Recência, Frequência e Valor (RFV) e exibe os resultados em uma tabela interativa.
# Parâmetros utilizados no código:
# - uploaded_file: Arquivo de compras enviado pelo usuário via interface Streamlit. Aceita arquivos nos formatos CSV e XLSX.
# - df_compras: DataFrame contendo os dados de compras lidos do arquivo enviado. Espera-se que contenha as colunas 'ID_cliente', 'DiaCompra', 'CodigoCompra' e 'ValorTotal'.
# - dia_atual: Data de referência para cálculo da recência, definida como o dia seguinte à última compra registrada no dataset.
# - df_recencia: DataFrame com o ID do cliente e a data da última compra de cada cliente.
# - df_frequencia: DataFrame com o ID do cliente e a quantidade de compras realizadas (frequência).
# - df_valor: DataFrame com o ID do cliente e o valor total gasto (soma dos valores das compras).
# - df_RF: DataFrame intermediário contendo recência e frequência por cliente.
# - df_RFV: DataFrame final contendo recência, frequência e valor por cliente, indexado pelo ID do cliente.
# O script espera que o arquivo de entrada possua as seguintes colunas:
# - 'ID_cliente': Identificador único do cliente.
# - 'DiaCompra': Data da compra (deve ser convertível para datetime).
# - 'CodigoCompra': Identificador da compra (usado para contar frequência).
# - 'ValorTotal': Valor monetário da compra (usado para somar o valor total gasto por cliente).


# Verifica se um arquivo foi enviado pelo usuário
if uploaded_file is not None:
    # Lê o arquivo CSV enviado, convertendo a coluna 'DiaCompra' para o tipo datetime automaticamente
    df_compras = pd.read_csv(
        uploaded_file,
        infer_datetime_format=True,
        parse_dates=["DiaCompra"],
    )

    dados_compras = st.checkbox(
        "Exibir dados do arquivo de compras",
        value=True,
        help="Marque para visualizar os dados do arquivo de compras.",
    )

    # Adiciona uma linha divisória e um título para a visualização dos dados
    if dados_compras == True:
        st.markdown("---")
        st.markdown(
            """
        <h2 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 1.5em;'>Visualização dos dados de compras</h2>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        <h3 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 0.8em;'>{df_compras.shape}</h3>
        """,
            unsafe_allow_html=True,
        )

        # Exibe as primeiras linhas do DataFrame de compras para conferência
        st.dataframe(df_compras, use_container_width=True, height=250)

    # Obtém as datas mínima e máxima das compras
    data_minima = df_compras["DiaCompra"].min()
    data_maxima = df_compras["DiaCompra"].max()

    # Define o dia atual como o dia seguinte à última compra registrada
    dia_atual = df_compras["DiaCompra"].max() + pd.Timedelta(days=1)

    # Agrupa por cliente e pega a data da última compra de cada um
    df_recencia = df_compras.groupby(by="ID_cliente", as_index=False)["DiaCompra"].max()
    df_recencia.columns = ["ID_cliente", "DiaUltimaCompra"]

    # Calcula a recência: quantos dias desde a última compra de cada cliente
    df_recencia["Recencia"] = df_recencia["DiaUltimaCompra"].apply(
        lambda x: (dia_atual - x).days
    )

    # Atualiza o dia atual (opcional, pois já foi feito acima)
    dia_atual = df_compras["DiaCompra"].max() + pd.Timedelta(days=1)

    # Remove a coluna de data da última compra, pois não será mais usada
    df_recencia.drop("DiaUltimaCompra", axis=1, inplace=True)

    # Calcula a frequência: quantidade de compras por cliente
    df_frequencia = (
        df_compras[["ID_cliente", "CodigoCompra"]]
        .groupby("ID_cliente")
        .count()
        .reset_index()
    )
    df_frequencia.columns = ["ID_cliente", "Frequencia"]

    # Calcula o valor: soma do valor gasto por cliente
    df_valor = (
        df_compras[["ID_cliente", "ValorTotal"]]
        .groupby("ID_cliente")
        .sum()
        .reset_index()
    )
    df_valor.columns = ["ID_cliente", "Valor"]

    # Junta as tabelas de recência e frequência
    df_RF = df_recencia.merge(df_frequencia, on="ID_cliente")

    # Junta a tabela anterior com o valor, formando a tabela RFV final
    df_RFV = df_RF.merge(df_valor, on="ID_cliente")

    # Define o índice da tabela como o ID do cliente
    df_RFV.set_index("ID_cliente", inplace=True)

    # Calcula os quartis (25%, 50%, 75%) para as colunas Recencia, Frequencia e Valor
    quartis = df_RFV.quantile([0.25, 0.5, 0.75])
    quartis.to_dict()  # Converte os quartis para um dicionário

    # Classifica a recência de cada cliente em quartis (A, B, C, D)
    df_RFV["R_quartil"] = df_RFV["Recencia"].apply(
        recencia_class, args=("Recencia", quartis)
    )

    # Classifica a frequência de cada cliente em quartis (A, B, C, D)
    df_RFV["F_quartil"] = df_RFV["Frequencia"].apply(
        frequencia_class, args=("Frequencia", quartis)
    )

    # Classifica o valor gasto de cada cliente em quartis (A, B, C, D)
    df_RFV["V_quartil"] = df_RFV["Valor"].apply(
        frequencia_class, args=("Valor", quartis)
    )

    # Cria um seletor na barra lateral para escolher a classe de recência ('A', 'B', 'C', 'D')
    selecao_recencia = st.sidebar.selectbox(
        "Selecione a classe da característica recência",
        options=["A", "B", "C", "D"],
        index=0,
        help="Selecione a classe da característica recência para filtrar os clientes. 'A' representa os clientes mais recentes.",
    )

    # Cria um seletor na barra lateral para escolher a classe de frequência ('A', 'B', 'C', 'D')
    selecao_frequencia = st.sidebar.selectbox(
        "Selecione a classe da característica frequência",
        options=["A", "B", "C", "D"],
        index=0,
        help="Selecione a classe da característica frequência para filtrar os clientes. 'A' representa os clientes mais frequentes.",
    )

    # Cria um seletor na barra lateral para escolher a classe de valor ('A', 'B', 'C', 'D')
    selecao_valor = st.sidebar.selectbox(
        "Selecione a classe da característica valor",
        options=["A", "B", "C", "D"],
        index=0,
        help="Selecione a classe da característica valor para filtrar os clientes. 'A' representa os clientes que mais gastaram.",
    )

    # Aplica o filtro usando a função selecao_valores_categoricos para as colunas de recência, frequência e valor
    df_RFV1 = (
        df_RFV.pipe(
            selecao_valores_categoricos,
            col="R_quartil",
            selecionados=selecao_recencia,
            verificacao=False,
        )
        .pipe(
            selecao_valores_categoricos,
            col="F_quartil",
            selecionados=selecao_frequencia,
            verificacao=False,
        )
        .pipe(
            selecao_valores_categoricos,
            col="V_quartil",
            selecionados=selecao_valor,
            verificacao=False,
        )
    )

    # Cria uma checkbox na barra lateral para exibir a tabela RFV filtrada
    if st.sidebar.checkbox(
        "Exibir tabela RFV filtrada",
        value=True,
        help="Marque para visualizar a tabela RFV filtrada pelos critérios selecionados.",
    ):
        # Exibe a tabela RFV filtrada conforme os critérios escolhidos
        st.markdown("---")
        st.markdown(
            """
        <h2 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 1.5em;'>Tabela RFV Filtrada</h2>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <h3 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 0.8em;'>{df_RFV1.shape}</h3>
        """,
            unsafe_allow_html=True,
        )
        st.dataframe(df_RFV1, use_container_width=True, height=250)

        df_xlsx = df_RFV1.pipe(df_to_excel)
        st.sidebar.download_button(
            label="🟢⬇️ Faça o download do Dataframe RFV filtrado em excel",
            data=df_xlsx,
            file_name="dados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.markdown("---")

        st.markdown(
            """
        <h2 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 1.5em;'>Estratégia de marketing</h2>
        """,
            unsafe_allow_html=True,
        )

        df_marketing_strategy1 = (
            df_RFV1["R_quartil"] + df_RFV1["F_quartil"] + df_RFV1["V_quartil"]
        )
        df_marketing_strategy1 = pd.DataFrame(
            df_marketing_strategy1, columns=["RFV Score"]
        )

        # Aplica os comentários salvos para cada RFV Score
        df_marketing_strategy1["Comentário"] = df_marketing_strategy1["RFV Score"].map(
            lambda x: st.session_state["comentarios_rfv"].get(x, "")
        )

        # Cria o RFV Score atual com base nos filtros selecionados
        rfv_score_atual = selecao_recencia + selecao_frequencia + selecao_valor

        # Campo de texto com valor recuperado do session_state se existir
        comentario_input = st.text_input(
            f"Comentário para o perfil {rfv_score_atual}:",
            value=st.session_state["comentarios_rfv"].get(rfv_score_atual, ""),
            key="comentario_atual",
        )

        col1, col2 = st.columns([1, 1])
        submit_button = col1.button("Enviar Comentário")
        erase_button = col2.button("Limpar Comentário")

        # Atualiza ou limpa o comentário no session_state
        if submit_button:
            st.session_state["comentarios_rfv"][rfv_score_atual] = comentario_input
            st.success("Comentário enviado com sucesso!")

        elif erase_button:
            st.session_state["comentarios_rfv"].pop(rfv_score_atual, None)
            st.success("Comentário apagado com sucesso!")

        st.dataframe(df_marketing_strategy1, use_container_width=True, height=250)

        df_estrategias = df_RFV1[["Recencia", "Frequencia", "Valor"]].copy()
        df_estrategias["RFV Score"] = df_marketing_strategy1["RFV Score"]
        df_estrategias["Sugestão de estratégia"] = df_marketing_strategy1["Comentário"]

        df_xlsx2 = df_estrategias.pipe(df_to_excel)

        download_button = st.download_button(
            "🟢⬇️ Faça o download do Dataframe RFV filtrado com estratégia de marketing em excel",
            key="download_marketing_strategy",
            data=df_xlsx2,
            file_name="dados_filtrados_marketing.xlsx",
            help="Clique para baixar o DataFrame RFV filtrado com a estratégia de marketing em formato Excel.",
        )

    else:
        # Caso a checkbox não esteja marcada, exibe a tabela RFV completa (sem filtros)
        st.markdown("---")
        st.markdown(
            """
        <h2 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 1.5em;'>Tabela RFV Completa</h2>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <h3 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 0.8em;'>{df_RFV.shape}</h3>
        """,
            unsafe_allow_html=True,
        )
        st.dataframe(df_RFV, use_container_width=True, height=250)

        df_xlsx = df_RFV.pipe(df_to_excel)
        st.sidebar.download_button(
            label="🟢⬇️ Faça o download do Dataframe RFV completo em excel",
            data=df_xlsx,
            file_name="dados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.markdown("---")

        st.markdown(
            """
        <h2 style='text-align: center; font-family: "Kantumruy Pro", sans-serif; font-size: 1.5em;'>Estratégia de marketing</h2>
        """,
            unsafe_allow_html=True,
        )

        df_marketing_strategy = (
            df_RFV["R_quartil"] + df_RFV["F_quartil"] + df_RFV["V_quartil"]
        )
        df_marketing_strategy = pd.DataFrame(
            df_marketing_strategy, columns=["RFV Score"]
        )
        df_marketing_strategy["Comentário"] = df_marketing_strategy["RFV Score"].map(
            lambda x: st.session_state["comentarios_rfv"].get(x, "")
        )

        df_marketing_strategy["Comentário"] = df_marketing_strategy["RFV Score"].apply(
            lambda x: st.session_state["comentarios_rfv"].get(x, "")
        )

        st.dataframe(df_marketing_strategy, use_container_width=True, height=250)

        df_estrategias1 = df_RFV[["Recencia", "Frequencia", "Valor"]].copy()
        df_estrategias1["RFV Score"] = df_marketing_strategy["RFV Score"]
        df_estrategias1["Sugestão de estratégia"] = df_marketing_strategy["Comentário"]

        df_xlsx2 = df_estrategias1.pipe(df_to_excel)

        download_button = st.download_button(
            "🟢⬇️ Faça o download do Dataframe RFV com estratégia de marketing em excel",
            key="download_marketing_strategy",
            data=df_xlsx2,
            file_name="dados_filtrados_marketing.xlsx",
            help="Clique para baixar o DataFrame RFV com a estratégia de marketing em formato Excel.",
        )

    st.sidebar.button(
        "Limpar comentários salvos",
        on_click=lambda: st.session_state.pop("comentarios_rfv", None),
        help="Clique para limpar todos os comentários salvos sobre os perfis RFV.",
        key="limpar_comentarios",
    )

    st.sidebar.button(
        "🔄 Limpar dados",
        on_click=lambda: st.session_state.clear(),
        help="Clique para limpar todos os dados e reiniciar a aplicação.",
    )
