# Cálculo de retorno dos Swaps

O retorno diário do swap é dado por:

$$r^{Swap}_t = r^{ETF}_t - r^{short}_t \tag{1}$$ 

Dessa forma, usando como base o preço do *total return index (gross dividends)* ($p_t$) dos [ETFs usados](desc_etf_doc.md), calculamos o log-retorno diário dos ETFs como:

$$r^{ETF}_t = log(p_t) - log(p_{t-1})\tag{2}$$ 

```python
import pandas as pd
import numpy as np
def calculate_log_return(df : pd.DataFrame, price_col : str):
        return np.log(df[price_col]) - np.log(df[price_col].shift(1))
```


A base da **LIBOR** (índice usado na perna short do swap) foi dado em taxa anual, incialmente precisamos transformar a taxa anual em taxa diária e em seguida transformar em log-retorno:

$$r^{\text{daily-log-return}}_t = log((1 + r^{annual}_t)^{1/365}) \tag{3}$$


```python
import pandas as pd
import numpy as np
def transform_annual_rate_in_daily_log_raturn(df : pd.DataFrame, annual_rate_col: str):
        df2 = df.reset_index()
        return np.log((1 + df2[annual_rate_col])**(1/365))
```


Com isso, os log-retornos diários dos swaps das ETFs ($r^{Swap}_t$)  foram calcualdos.