# Asset Allocation

<p>Projeto de Asset Allocation (Mestrado Profissional de Economia)</p>
<p>Início do desenvolvimento: 25/06/2024</p>

---------

## Funcionalidaes:

O projeto apresenta duas funcionalidades. 

1. **BackTest**
   Para rodar o back test, basta rodar o comando:
    ```
    python src/main.py plot_asset_returns
    ```
2. **Plot Asset Returns**
   Para rodar o back test, basta rodar o comando:
    ```
    python src/main.py plot_asset_returns
    ```

## Estrutura do Projeto

Na pasta `data`, temos os inputs usados para rodar o código (na pasta `data/input`) e na pasta `data/output` encontramos os resultados e as configurações dos backtests, bem como as figuras salvas do plots.

Na pasta `docs`, encontramos alguns documentos que podem explicar melhor quais as contas foram feitas, além de outras referências úteis.
- [Lógica para calcular retornos de swaps](docs/calc_swaps_doc.md)
- [Lógica para calcular vol. de cada ativo](docs/calc_vol_doc.md)
- [Lógica para calcular vol. das estratégias](docs/calc_vol_doc.md)
- [Lógica da estratégia de Vol. Targeting](docs/strat_vol_target_doc.md)
- [Lógica da estratégia de Trend-Following](docs/strat_trend_following_doc.md)
- [Lógica de controle do trading book como um todo](docs/book_control_doc.md)

Na parta `src`, encontramos todo o código usado nesse projeto. De forma geral, a pasta `src/presentation` contempla toda a parte do código que é usada para criar gráficos. Na pasta `src/core` está implementada a lógica principal do código.



## Arquitetura de Software

Para desenvolver esse trabalho, o modelo de **Clean Architecture** foi usado como inspiração para a arquitetura de software. Dessa forma, o código salvo em `src/core`, apresenta a seguinte segmentação por camadas:

- <code>**APPLICATION**</code>: onde estão implementadas as classes que são responsáveis pela lógica geral da aplicação. É onde encontramos a implementação da atualização da ***trading position*** das assets, as implemtação das ***trading strategies*** e do ***trading book*** como um todo.
- <code>**DOMAIN**</code>: onde estão implementadas as entidades como resultados dos tradings, swaps e o portfolio. Além disso, também está implementadas cálculos comummente conhecidos, a trasnformação de taxas anuais para uma taxa diária.
- <code>**INFRA**</code>: onde estão implementadas as classes que são responsáveis pela conexão com os dados (no caso, a planilha .csv em `input`).



## Dependências

As dependências para esse projeto estão listadas no arquivo `requirements.txt`. Para instalá-las usando pip, basta escrever no terminal:

`````
pip install -r requirements.txt
`````


As libs externas usadas nesse projeto são:

````
ipython==8.12.3
matplotlib==3.7.5
numpy==1.23.5
pandas==1.1.3
plotly==5.8.0
````
