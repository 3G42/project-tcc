import datetime
import pandas as pd


def create_empty_dataframe(indexes,total_simulations:int, stepsize):
    header = pd.date_range('00:00:00', periods=total_simulations, freq=f'{stepsize}min').strftime('%H:%M')
    df = pd.DataFrame(index=indexes,columns=header)
    
    return df

def data_mount(total_simulations,df,func):
    for h in range(total_simulations):
        o=func(h)
        instant = o['instant']
        values = o['values']
        is_complex = o['complex']
        if is_complex:
            df[instant] = [
                (values[j] + 1j * values[j+1]) for j in range(0,len(values),2)
            ]
        else:
            df[instant] = [
                values[j] for j in range(0,len(values))
            ]