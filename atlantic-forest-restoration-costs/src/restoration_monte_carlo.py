"""Bootstrap Monte Carlo analysis of Atlantic Forest restoration costs.

The detailed project budget is read from the supplied Excel workbook.
The price quotations are independently resampled with replacement.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BUDGET_PATH = ROOT / "data" / "restoration_project_budget.xlsx"
QUOTATIONS_PATH = ROOT / "data" / "input_price_quotations.csv"
NAMES = ["Calcário", "Super Simples", "NPK 06-30-06", "Formicida", "Mourão", "Estaca", "Arame farpado (m)", "Grampo"]
BUDGET_ROWS = [7,9,10,11,13,14,15,16]
CHECKPOINTS = [100,250,500,1000,2500,5000,10000]

def read_budget(path=BUDGET_PATH):
    # Preserve numeric values at source precision; 2-decimal formatting is display-only.
    raw = pd.read_excel(path, sheet_name=0, header=None)
    def cell(row, column):
        value = raw.iat[row - 1, column - 1]
        return float(value) if pd.notna(value) else 0.0
    quantities=np.array([cell(row,14) for row in BUDGET_ROWS], dtype=float)
    unit_prices=np.array([cell(row,3) for row in BUDGET_ROWS], dtype=float)
    seedling_cost=cell(6,15)
    service_cost=cell(34,15)
    input_cost=cell(17,15)
    total_cost=cell(36,15)
    brush_rate=cell(22,3)
    brush_hours=np.array([cell(22,c) for c in (4,6,8,10,12)],dtype=float)
    brush_cost=cell(22,15)
    expected_input=seedling_cost+np.sum(quantities*unit_prices)
    if not np.isclose(expected_input,input_cost,atol=0.02):
        raise ValueError(f'Input total differs from detailed budget: {expected_input:.4f} / {input_cost:.4f}')
    if not np.isclose(input_cost+service_cost,total_cost,atol=0.02):
        raise ValueError('Input and service subtotals do not reconcile with project total.')
    if not (np.isclose(brush_rate,30,atol=0.005) and np.isclose(brush_hours.sum(),60,atol=0.005) and np.isclose(brush_cost,1800,atol=0.02)):
        raise ValueError('Brush-cutter budget must correspond to 60 h × BRL 30 = BRL 1,800.')
    return dict(quantities=quantities, unit_prices=unit_prices, seedling_cost=seedling_cost,
                service_cost=service_cost, input_cost=input_cost,total_cost=total_cost,
                brush_rate=brush_rate,brush_hours=brush_hours,brush_cost=brush_cost)

def read_quotations(path=QUOTATIONS_PATH):
    quotes=pd.read_csv(path)
    if not {'Insumo','Preço'}.issubset(quotes):
        raise ValueError('Quotation file must contain Insumo and Preço.')
    for name in NAMES:
        if len(quotes.loc[quotes['Insumo']==name])!=10:
            raise ValueError(f'Expected 10 price quotations for {name}.')
    return quotes

def simulate(seed=123,n=10000,budget=None,quotes=None):
    budget=read_budget() if budget is None else budget
    quotes=read_quotations() if quotes is None else quotes
    rng=np.random.default_rng(seed)
    columns={}
    for name in NAMES:
        observed=quotes.loc[quotes['Insumo']==name,'Preço'].to_numpy(dtype=float)
        columns[name]=rng.choice(observed,size=(n,len(observed)),replace=True).mean(axis=1)
    result=pd.DataFrame(columns)
    result.insert(0,'Iteration',np.arange(1,n+1))
    result['Input costs']=budget['seedling_cost']+result[NAMES].to_numpy()@budget['quantities']
    result['Service costs']=budget['service_cost']
    result['Total cost']=result['Input costs']+result['Service costs']
    return result

def metrics(values):
    x=np.asarray(values,dtype=float)
    p95=np.percentile(x,95)
    sd=np.std(x,ddof=1)
    return {'Mean':np.mean(x),'Standard deviation':sd,'Minimum':np.min(x),
            'P05':np.percentile(x,5),'P10':np.percentile(x,10),
            'Median (P50)':np.median(x),'P90':np.percentile(x,90),
            'P95 (VaR95)':p95,'P99':np.percentile(x,99),'Maximum':np.max(x),
            'CV (%)':sd/np.mean(x)*100,'CVaR95':np.mean(x[x>=p95])}

def convergence(df):
    result=[]
    for n in CHECKPOINTS:
        if n<=len(df):
            m=metrics(df['Total cost'].to_numpy()[:n])
            result.append({'Iterations':n,'Mean':m['Mean'],'P95':m['P95 (VaR95)'],'CV (%)':m['CV (%)']})
    return pd.DataFrame(result)

def sensitivity(df,budget):
    return pd.DataFrame([{'Input':name,'Pearson r':np.corrcoef(df[name],df['Total cost'])[0,1],
                          'Budgeted quantity':qty}
                         for name,qty in zip(NAMES,budget['quantities'])]).sort_values('Pearson r',ascending=False)

if __name__=='__main__':
    budget=read_budget()
    df=simulate(budget=budget)
    print('Deterministic project cost (BRL):',f"{budget['total_cost']:,.2f}")
    print(pd.Series(metrics(df['Total cost'])).map(lambda x:f'{x:,.2f}'))
