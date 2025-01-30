import py_dss_interface


class DSSInstance(py_dss_interface.DSS):
    def __init__(self, file):
        super().__init__()
        self.pathfile = file
        

    def compile_code(self):
        self.text(f"compile {self.pathfile}")

    def change_element_status(self, name):
        self.circuit.set_active_element(name)
        if self.cktelement.is_enabled == 1:
            print("Status enabled...")
            self.cktelement.enabled(0)
            print("... change to disabled")
        elif self.cktelement.is_enabled == 0:
            print("Status disabled...")
            self.cktelement.enabled(1)
            print("... change to enabled")

    def filter_elements(self, part, criteria="contains"):
        criterias = {"contains": lambda x: x.find(part) != -1}
        return filter(criterias[criteria], self.circuit.elements_names)

    def set_config_simulation(self, stepsize_min=15):
        step_size_sec = 60 * stepsize_min
        total_time_hour = 24  # hours
        total_simulations = int(total_time_hour * 60 / stepsize_min)
        self.solution.mode = 1
        self.solution.step_size = (
            step_size_sec  ## ESTE VALOR DETERMINA O STEP_SIZE EM SEGUNDOS
        )
        self.solution.number = 1
        
        self.total_steps = total_simulations
        

        
