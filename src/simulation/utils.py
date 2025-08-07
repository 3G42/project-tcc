import pandas as pd


def drp_drc_define(v_indicators: pd.DataFrame):
    drps = v_indicators.loc[['DRP_A', 'DRP_B', 'DRP_C']]
    drcs = v_indicators.loc[['DRC_A', 'DRC_B', 'DRC_C']]
    drp_per_bus = drps.sum(axis=0)
    drc_per_bus = drcs.sum(axis=0)

    return drp_per_bus, drc_per_bus
