import py_dss_interface as pydss
from dss import DSSInstance
from dataframe import create_empty_dataframe

if __name__ == "__main__":

    project_file = r"C:/Users/gabri/project-tcc/src/circbtfull_storage.dss"
    dss = DSSInstance(file=project_file)
    dss.compile_code()

    nodes_names = dss.circuit.nodes_names
    elements_names = dss.circuit.elements_names
    buses_names = dss.circuit.buses_names
    num_buses = dss.circuit.num_buses
    num_cktelement = dss.circuit.num_ckt_elements

    ar = dss.filter_elements("Generator.", "contains")

    for i in ar:
        dss.change_element_status(i)

    settings = dss.set_config_simulation()

    # dataframe = create_empty_dataframe(
    #     nodes_names, settings["total_simulations"], stepsize=settings["stepsize"]
    # )
    
    
