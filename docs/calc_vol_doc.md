# Cálculo da Volatilidade

O cálculo da vol de cada asset e a vol. da estratégia é primordial para o controle geral das estratégias e para a execução individual de cada estratégia, tanto na vol-targeting como na implementação usada pela trend-following.

O cálculo de cada componente está descrito abaixo. Para todas, o número de pontos $n$ usados para o cálculo da vol. foi definido como 90 (embora pudesse ser definido um número diferente para cada estratégia e book).


---

## 1. Swaps

### 1.1. Swaps - Cálculo da volatilidade

Dado a série histórica dos [log-retornos dos swaps](calc_swaps_doc.md) usados em uma determinada estratégia, obtemos os últimos $n$  pontos antes da data $t$ e calculamos o desvio padrão de cada swap:

$$V_{t}^{Swaps} = Std[R^{Swaps}_{t-n-1 \;\le \; d \;< \; t}] \tag{1}$$

``` python
def get_assets_volatility(self, target_date, last_n_points):
    df = self.log_returns[self.log_returns[ias.DATE] < target_date].tail(last_n_points)
    std = df[self.asset_names].std()
    return std
```


### 1.2. Swaps - Cálculo da covariância

Dado a série histórica dos log-retornos dos swaps usados em uma determinada estratégia, obtemos os últimos $n$  pontos antes da data $t$ e a matriz de covariância:

$$COV_{t}^{Swaps} = Cov[R^{Swaps}_{t-n-1 \;\le \; d \;< \; t}] \tag{2}$$

``` python
def get_covariance_matrix(self, target_date, last_n_points):
    df = self.log_returns[self.log_returns[ias.DATE] < target_date].tail(last_n_points)
    covariance_matrix = df[self.asset_names].cov()
    return covariance_matrix
```


----

## 2. Estratégias

### 2.1. Estratégias - Cálculo da volatilidade

Em determinada data $t$, um swap (ou asset, para generalizar) possui uma posição $w_{a,t}$ em determinada estratégia, sendo que cada posição pode variar entre $-\lambda_{max}\le w_{a,t} \le \lambda_{max}$, onde $\lambda_{max}$ é a máxima alavangacem (*leverage*) permitida para essa estratégia. 

Uma posição $w_{a,t} > 0 $ significa que a estratégia está long no swap e uma posição $w_{a,t} < 0$ significa que a estratégia está short no swap.

Sendo uma estratégia com k swaps, o vetor de posições para cada swap usado nessa estratégia é definido por:

$$W_{t} = \begin{bmatrix} w_{1,t} \\ w_{2,t} \\ \vdots \\ w_{k,t} \end{bmatrix}^T \tag{3}$$


Assim, dado o vetor de posições da estratégia e a matriz de covariância dos log-retornos dos swaps $COV_{t}^{Swaps}$, a volatilidade da estratégia é dada por:

$$ V^{Estratégia}_{t} = \sqrt{W_{t} \times COV_{t}^{Swaps} \times W_{t}^{T}} \tag{4}$$


``` python
def get_portfolio_volatility(self, target_date, last_n_points):
    covariance = self.get_covariance_matrix(target_date, last_n_points)
    
    # calculando vol da estratégia
    current_asset_weights_series = pd.Series(self.current_asset_weights)
    portfolio_var =  current_asset_weights_series @ covariance @ current_asset_weights_series.T
    portfolio_vol = np.sqrt(portfolio_var)
    
    return portfolio_vol
```


## 3. Vol. do Trading Book

O Trading Book é formado por um conjunto de estratégias e o peso em cada estratégia pode mudar ao longo do tempo. Nesse sentido, uma estratégia posssui um peso $\rho_{s,t}$ no boook, sendo que:

$$ \begin{cases}
\sum_{s=1}^m \rho_{s,t} = 1  & \forall t \\
0\le \rho_{s,t} \le 1 & \forall t,  
\end{cases} \tag{5}
$$

onde $m$ é o número de estratégias. Com isso, o vetor de pesos para cada estratégia no book é definido por:

$$P_{t} = \begin{bmatrix} \rho_{1,t} \\ \rho_{2,t} \\ \vdots \\ \rho_{m,t} \end{bmatrix}^T \tag{6}$$

Para calcular a matriz de correlação das estratégias, usamos como *proxy* do log-retorno o P&L diário da estratégia, desconsiderando a média de P&L diário dos últimos $n$ dias.

Nesse sentido, para uma data $t$, a covariânica das estratégias $COV_{t}^{Estratégias}$ seria dada por: 

$$COV_{t}^{Estratégias} = Cov[(PnL^{Estratégias}_{t-n-1 \;\le \; d \;< \; t}) - \mathbb{E}(PnL^{Estratégias}_{t-n-1 \;\le \; d \;< \; t} )] \tag{7}$$


Assim, sendo o vetor de pesos das estratégias $P_{t}$ e a matriz de covariância dos pnls diários das estratégias $COV_{t}^{Estratégias}$, a volatilidade do book é dada por:

$$ V^{Book}_{t} = \sqrt{P_{t} \times COV_{t}^{Estratégias} \times P_{t}^{T}} \tag{8}$$


``` python
def calc_portfolio_volatility_with_weights(self, target_date, last_n_points, current_asset_weights):
    covariance = self.get_covariance_matrix(target_date, last_n_points)

    # calculando vol do book
    portfolio_var =  current_asset_weights @ covariance @ current_asset_weights.T
    portfolio_vol = np.sqrt(portfolio_var)
    
    return portfolio_vol
```
