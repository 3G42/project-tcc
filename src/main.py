import datetime

import pandas as pd
import py_dss_interface as pydss
import seaborn as sns


dssObj = pydss.DSS()


def float_to_time(hours_float):
    start_date = datetime.datetime(2024, 11, 20)
    time_delta = datetime.timedelta(hours=hours_float)
    time_obj = (start_date + time_delta).time()

    return str(time_obj)


def get_monitor_data(name: str):
    dssObj.monitors.name = name
    dssObj.monitors.save()
    num_channels = dssObj.monitors.num_channels
    header = dssObj.monitors.header
    data = {}
    for i in range(num_channels):
        data[header[i]] = dssObj.monitors.channel(i + 1)
    return {"monitor_name": name, "data": data}


dss_project_file = r"C:/Users/gabri/project-tcc/src/circbtfull_storage.dss"
dssObj.text(f"compile {dss_project_file}")
dssObj.solution.mode = 1
print("")
dssObj.solution.step_size = 600
dssObj.solution.number = 24 * 6
myDef = dssObj.solution.default_daily
print(myDef)
print(dssObj.solution.mode_id)
dssObj.solution.solve()
print("")

name_monitors = dssObj.monitors.names
monitors_obj = []
for name in name_monitors:
    monitors_obj.append(get_monitor_data(name))
dfs = dict(
    map(lambda d: (d["monitor_name"], pd.DataFrame(data=d["data"])), monitors_obj)
)
df = dfs[name_monitors[0]]

sns.lineplot(data=df[df.columns[0]])
