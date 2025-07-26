Link para o "notion.so" para detalhes do funcionamento: https://www.notion.so/Detalhes-do-Desenvolvimento-do-Desafio-de-Gabriel-Linard-Leite-23cc350ff2db809e9abbd86cdb3aaffe?source=copy_link

1.Para executar o código Python "baixar_csv_firefox.py", é necessário modificar o arquivo ".env" onde tem "sua_senha_aqui", colocando a sua senha real do 
banco de dados PostgreSQL. 

2.Na parte de extração dos dados do código Python do arquivo "baixar_csv_firefox.py", foram alterados os links enviados no desafio, devido o link do site 
"https://aplicacoes.cidadania.gov.br/ ..." direcionar para a tabela "Brasil". Porém, para realizar o webscraping de todos os municípios, foi necessário 
realizar um filtro no próprio site, que direciona para um outro link que apresenta os dados com as informações solicitadas no desafio.

3.Na parte do código do arquivo "baixar_csv_firefox.py", na linha 84, com o comando "time.sleep(20)", o valor "20" pode ser alterado para um valor menor 
ou maior dependendo da taxa de transmissão da internet. Pois, esse tempo é para aguardar o download do último arquivo ".csv".

4.Na função de armazenamento no banco, foi modificado o formato da coluna "Mês/Ano" de "07/2024" para "2024-07-01" de forma que seja possível realizar 
filtros e ordenações pelas datas, pois foi feito um teste de filtros no banco de dados, com "Where" e "Between" e foi visto que o filtro não foi reali- 
zado corretamente.
