import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine
from sqlalchemy.types import Date



# 1.EXTRAÇÃO DE DADOS (WEB SCRAPING):

load_dotenv()

def preparar_diretorio_download(nome_pasta="downloads"):
    pasta = os.path.abspath(nome_pasta)
    os.makedirs(pasta, exist_ok=True)
    return pasta

def configurar_driver(download_dir):
    options = Options()
    options.headless = True
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-excel")
    options.set_preference("pdfjs.disabled", True)
    return webdriver.Firefox(options=options)

def capturar_arquivo_baixado(pasta_download, arquivos_antes, extensao=".csv"):
    while True:
        time.sleep(1)
        arquivos_agora = set(os.listdir(pasta_download))
        novos = arquivos_agora - arquivos_antes
        for nome in novos:
            if nome.endswith(extensao):
                return nome

def baixar_csv(driver, url, download_dir, aceitar_lgpd=False):
    driver.get(url)
    time.sleep(2)

    if aceitar_lgpd:
        try:
            botao_ok = driver.find_element(By.XPATH, '//*[@id="btnAccepptLgpdSagi"]')
            botao_ok.click()
            time.sleep(2)
        except:
            pass

    arquivos_antes = set(os.listdir(download_dir))
    botao_csv = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[2]/div[4]/div/div/div/div[2]/div/div[6]/div[2]/div/div[1]/div[2]/div/button[1]')
    botao_csv.click()
    nome_arquivo = capturar_arquivo_baixado(download_dir, arquivos_antes)
    return nome_arquivo

urls = {
    "consumo": {
        "link": "https://aplicacoes.cidadania.gov.br/vis/data3/v.php?q[]=oNOhlMHqwGZsemeZ6au8srNekJavm7mj2ejJZmx4aWepanp%2BaGiJkWWdamOUqH1luL5ma6ptiLSYmcrGbtCen9DgiG%2BiqaGt3nSIwaya06Sc3bGYz%2Bmup1yulqfipbavqZLKgZfPXfb%2B4sKVXLiWrNpZsL2loMzOooplZB8lbffdr6qbolmyvKufvMioz7BTzeC5o1yVeY2ZYY6xrJrMzZTOrFzZ64iwuMRw&ultdisp=1&ultdisp=0&ag=m",
        "aceitar_lgpd": True
    },
    "producao": {
        "link": "https://aplicacoes.cidadania.gov.br/vis/data3/v.php?q[]=oNOhlMHqwGZsemeZ6au8srNekJivm7mj2ejJZmx4bWepanp%2BaGiJkWWdamOUqH1luL5ma6pviLSYmcrGbtCen9DgiG%2BiqaGt3nSIwaya06Sc3bGYz%2Bmup1yulqfipbavqZLKgZfPXfb%2B4sKVXLiWrNpZvcCmkcwk2i3gon2jf%2FbmaPjb4K6ud1eSxdWlz6Sowu5tpKG0pFrGfaBuX2661qDfqZTB6nawrIOxtvV0&ag=m",
        "aceitar_lgpd": False
    },
    "escolar": {
        "link": "https://aplicacoes.cidadania.gov.br/vis/data3/v.php?q[]=oNOhlMHqwGZsemeZ6au8srNfh5Ovm7mj2ejJZmx5Z2epanp%2BaGiJkWWdamOUqH1luL5ma6tqiLSYmcrGbtCen9DgiG%2BiqaGt3nSIwayaetxUzayUyeDAl6FwdbCqan9%2FY12AgV6KoKK%2B57Knn61deu9qfoBnWYeKVOd4mb7nwJl3rpam7J6IiZ2Ow9SYpXim0ujJhbGpo67ina6ynE27xlOtpqbR4L%2BinbtVf%2BycvLqYn7zUU8%2Brp8%2FgtKmhu1VnmZ7Fs5qiGgj2DaxTsMSUVH%2BxqK7eq7uvqlCayqbeoqXL3MBUgbuYqeWav7OqTbzPp9yimtLgwFSsraGpmYaRoVdNf6KW36qoydyxo2XEpXX1tcmJ&ag=m",
        "aceitar_lgpd": False
    }
}

def main():
    download_dir = preparar_diretorio_download()
    driver = configurar_driver(download_dir)

    arquivos_baixados = {}
    for nome, dados in urls.items():
        arquivo = baixar_csv(driver, dados["link"], download_dir, dados["aceitar_lgpd"])
        arquivos_baixados[nome] = arquivo
        print(f"Arquivo baixado ({nome}): {arquivo}")

    time.sleep(20)
    driver.quit()

    return download_dir, arquivos_baixados



# 2.HARMONIZAÇÃO DE DADOS (NORMALIZAÇÃO E UNIFICAÇÃO):

if __name__ == "__main__":
    download_dir, arquivos = main()

    df1 = pd.read_csv(os.path.join(download_dir, arquivos["consumo"]), sep=",", encoding="latin1")
    df2 = pd.read_csv(os.path.join(download_dir, arquivos["producao"]), sep=",", encoding="latin1")
    df3 = pd.read_csv(os.path.join(download_dir, arquivos["escolar"]), sep=",", encoding="latin1")

    df_unificado = pd.concat([df1, df2, df3], join="outer", ignore_index=True)
    df_unificado = df_unificado.groupby(["Código", "Referência"], as_index=False).first()
    df_unificado = df_unificado.drop(columns=["Código", "Data de atualização"], errors="ignore")

    colunas_ordenadas = ["UF", "Unidade Territorial", "Referência"] + \
        [col for col in df_unificado.columns if col not in ["UF", "Unidade Territorial", "Referência"]]
    df_unificado = df_unificado[colunas_ordenadas]

    df_unificado = df_unificado.rename(columns={
        "Unidade Territorial": "Município",
        "Referência": "Mês/Ano",
        "Cisternas familiares de água para consumo (1ª água) entregues pelo MDS (Acumulado)": "Consumo",
        "Cisternas familiares de água para produção (2ª água) entregues pelo MDS (Acumulado)": "Produção",
        "Cisternas Escolares entregues pelo MDS  (Acumulado)": "Escolar"
    })

    df_unificado["Mês/Ano"] = pd.to_datetime(df_unificado["Mês/Ano"], format="%m/%Y")

    print(df_unificado.head())

    agora = datetime.now().strftime("%Y-%m-%d_%H%M")
    nome_arquivo = f"dados_unificados_por_municipio_{agora}.csv"
    df_unificado.to_csv(os.path.join(download_dir, nome_arquivo), index=False, encoding="utf-8-sig")



# 3.ARMAZENAMENTO (BANCO DE DADOS POSTGRESQL):

    usuario = os.getenv("DB_USER")
    senha = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    porta = os.getenv("DB_PORT")
    banco = os.getenv("DB_NAME")

    url_conexao = f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"
    engine = create_engine(url_conexao)

    nome_tabela = "cisternas_municipios"
    df_unificado.to_sql(
    nome_tabela,
    engine,
    if_exists="replace",
    index=False,
    dtype={"Mês/Ano": Date()}
)

    print(f"Dados salvos com sucesso na tabela '{nome_tabela}' do banco '{banco}'")