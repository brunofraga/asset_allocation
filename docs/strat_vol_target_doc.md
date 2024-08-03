# Lógica da Estratégia de Vol-Targeting

Basicamente, a estratégia de vol-targeting  tem como objetivo controlar a exposição long de um portfólio de forma que ele persiga uma volatilidade alvo definida anteriormente.

Imaginando essa estratégia para um portfólio de k swaps, o vetor de posições para cada swap usada nessa estratégia é dado por: 

$$W_{t} = \begin{bmatrix} 
            w_{1,t} \\\
            w_{2,t} \\\
             \vdots \\\ 
             w_{k,t} 
             \end{bmatrix}^T = 
             \begin{bmatrix} 
            1/\sigma_{1,t} \\\
            1/\sigma_{2,t} \\\
             \vdots \\\ 
             1/\sigma_{k,t} 
             \end{bmatrix}^T
             \tag{1}$$

Assim, dado o vetor de posições da estratégia e a matriz de covariância dos log-retornos dos swaps $COV_{t}^{Swaps}$, a volatilidade da estratégia é dada por:

$$ V^{Estratégia}_{t} = \sqrt{W_{t} \times COV_{t}^{Swaps} \times W_{t}^{T}} \tag{2}$$

O peso atualizado da estratégia é dado por:



$$ \begin{equation}
\overline{W}_{t} = f W_{t}
\text{,}\quad    \text{sendo } \quad 
f = \text{Min} \left(\frac{V^{Estratégia}_{target}}{V^{Estratégia}_{t}}, \lambda_{max} \right)
\tag{3}
\end{equation}
$$

Onde $\lambda_{max}$ é a alavancagem máxima da estratégia

Certamente, não é desejado que a estratégia rebalanceie o portfolio com uma frequência muito alta, o que aumentaria custo de transação. Nesse sentido, existem as seguintes possibilidades para mudança da exposição:
 
1. Periodicamente a cada 90 dias;
2. Volatilidade alta: desvio da média da volatilidade de 30 dias rolling da é maior que 1.65 vezes o desvio padrão. Ou seja:
<!-- $$ \begin{equation} -->
$$
% AND \begin{cases}
V^{Estratégia}_{t} - \mathbb{E}[V^{Estratégia}]_{\text{30 dias}} \ge 1.65 \mathbb{V}[V^{Estratégia}]_{\text{30 dias}}\\\
% \end{cases} 
\tag{4} 
% \end(equation)
$$

Caso a estratégia seja rebalanceada no caso 2, a contagem de dias para o caso 1 é resetada (ou seja, o caso 1 só será ativado caso em 90 dias úteis, caso não haja outro recabelaceamento pelo caso 2).