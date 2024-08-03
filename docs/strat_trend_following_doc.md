# Lógica da Estratégia de Trend-Following

Na abordagem para a estratégia de trend-following também usa o princípio de [vol. targeting](strat_vol_target_doc.md) na construção da exposição, mas com alguns ajustes.

Em uma determinada data $t$, a estratégia funciona da seguinte forma:
1. Para cada swap $k$ no tempo $t$, obtemos os últimos o retorno mensal dos últimos $2p$ meses
2. Para cada swap $k$ no tempo $t$, obtemos os últimos a vol mensal dos últimos $2p$ meses
3. Para cada swap $k$ no tempo t, fazemos a regressão linear com os últimos $p-1$ retornos mensais tal que:

$$ \frac{r_{k,t}}{\sigma_{k, t-1}} = \alpha_{k,t,p} + \beta_{k, t, p} \frac{r_{k,t-p}}{\sigma_{k, t-1-p}} + \epsilon \tag{1}$$ 

4. Em seguida, com o próximo retorno mensal previsto, o peso da exposição do swap k será:

$$ \rho_{k, t} = 40\% \,\, \text{sign}(r_{k,t}) \,r_{k,t} \,  \overline{w}_{k,t} \tag{2}$$

Onde $\overline{w}_{k,t}$ é dado pela lógica de vol targeting, com a única diferença que:

$$W_{t} = \begin{bmatrix} 
            w_{1,t} \\\
            w_{2,t} \\\
             \vdots \\\ 
             w_{k,t} 
             \end{bmatrix}^T = 
             \begin{bmatrix} 
            sign(r_{1,t})/\sigma_{1,t} \\\
            sign(r_{2,t})/\sigma_{2,t} \\\
             \vdots \\\ 
             sign(r_{k,t})/\sigma_{k,t} 
             \end{bmatrix}^T
             \tag{3}$$

