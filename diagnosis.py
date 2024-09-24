from cnf import *
from ortools.sat.python import cp_model

objects = ['Outlet', 'Rasp-Pi', 'Power-Board',
           'Arduino', 'Sensor-Board0', 'Sensor-Board1']
actuators = ['Fans', 'LEDs', 'Pump']
sensors = ['H-T0', 'Light0', 'Moisture0', 'H-T1', 'Light1', 'Moisture1',
           'Wlevel']
relations = ['working', 'connected', 'powered', 'signal', 'expected-result']

def powered(comp): return 'powered(%s)' %comp
def working(comp): return 'working(%s)' %comp
def connected(from_comp, to_comp):
    return 'connected(%s, %s)' %(from_comp, to_comp)
def signal(signal, component): return 'signal(%s, %s)' %(signal, component)
def rasp_pi_signal(the_signal): return signal(the_signal, 'Rasp-Pi')
def expected_result(actuator): return 'expected-result(%s)' %actuator

def create_relation(name, model, variables):
    variables[name] = model.NewBoolVar(name)

def create_relations(relations, model, variables):
    for relation in relations: create_relation(relation, model, variables)

def create_working_relations(model, variables):
    create_relations([working(comp) for comp in objects + actuators + sensors],
                     model, variables)

def create_connected_relations(model, variables):
    # BEGIN STUDENT CODE
    connections = [
        ('H-T0', 'Sensor-Board0'),
        ('Light0', 'Sensor-Board0'),
        ('Moisture0', 'Sensor-Board0'),
        ('H-T1', 'Sensor-Board1'),
        ('Light1', 'Sensor-Board1'),
        ('Moisture1', 'Sensor-Board1'),
        ('Sensor-Board0', 'Arduino'),
        ('Sensor-Board1', 'Arduino'),
        ('Wlevel', 'Arduino'),
        ('Rasp-Pi', 'Arduino'),
        ('Arduino', 'Rasp-Pi'), 
        ('Arduino', 'Power-Board'),
        ('Power-Board', 'Pump'),
        ('Power-Board', 'LEDs'),
        ('Power-Board', 'Fans'),
        ('Outlet', 'Power-Board'),
        ('Outlet', 'Rasp-Pi'),
    ]
    
    for from_comp, to_comp in connections:
        create_relation(connected(from_comp, to_comp), model, variables)
    # END STUDENT CODE
    pass

def create_powered_relations(model, variables):
    # BEGIN STUDENT CODE
    create_relation(powered('Outlet'), model, variables)
    model.Add(variables[powered('Outlet')] == True)

    components = ['Rasp-Pi', 'Power-Board', 'Fans', 'LEDs', 'Pump']
    for component in components:
        create_relation(powered(component), model, variables)
    # END STUDENT CODE
    pass

def create_signal_relations(model, variables):
    # BEGIN STUDENT CODE
    sensors_to_boards = [
        ('H-T0', 'Sensor-Board0'),
        ('Light0', 'Sensor-Board0'),
        ('Moisture0', 'Sensor-Board0'),
        ('H-T1', 'Sensor-Board1'),
        ('Light1', 'Sensor-Board1'),
        ('Moisture1', 'Sensor-Board1')
    ]
    
    # Create signal relations for sensors to their sensor boards
    for sensor, board in sensors_to_boards:
        create_relation(signal(sensor, board), model, variables)

    # Actuator signals to Power-Board
    actuators_to_power_board = [
        ('LEDs', 'Power-Board'),
        ('Fans', 'Power-Board'),
        ('Pump', 'Power-Board')
    ]
    
    for actuator, board in actuators_to_power_board:
        create_relation(signal(actuator, board), model, variables)

    # Other signal relations to Arduino and Rasp-Pi already defined
    sensors = ['H-T0', 'Light0', 'Moisture0', 'H-T1', 'Light1', 'Moisture1', 'Wlevel']
    for sensor in sensors:
        # Sensors signal themselves, Arduino, and Rasp-Pi
        create_relation(signal(sensor, sensor), model, variables)
        create_relation(signal(sensor, 'Arduino'), model, variables)
        create_relation(signal(sensor, 'Rasp-Pi'), model, variables)
    
    # Actuators signal Arduino and Rasp-Pi
    actuators = ['LEDs', 'Fans', 'Pump']
    for actuator in actuators:
        create_relation(signal(actuator, 'Rasp-Pi'), model, variables)
        create_relation(signal(actuator, 'Arduino'), model, variables)
    # END STUDENT CODE
    pass

def create_expected_result_relations(model, variables):
    # BEGIN STUDENT CODE
    for actuator in actuators:
        create_relation(expected_result(actuator), model, variables)
    # END STUDENT CODE
    pass

def create_relation_variables(model):
    variables = {}
    create_working_relations(model, variables)
    create_connected_relations(model, variables)
    create_powered_relations(model, variables)
    create_signal_relations(model, variables)
    create_expected_result_relations(model, variables)

    return variables

def add_constraint_to_model(constraint, model, variables):
    for disj in (eval(constraint) if isinstance(constraint, str) else constraint):
        conv_disj = [variables[lit] if not is_negated(lit) else
                     variables[lit[1]].Not() for lit in disj]
        model.AddBoolOr(conv_disj)

def create_powered_constraint(from_comp, to_comp, model, variables):
    constraint = "IFF('%s', AND('%s', '%s'))" %(powered(to_comp),
                                                connected(from_comp, to_comp),
                                                working(from_comp))
    add_constraint_to_model(constraint, model, variables)

def create_powered_actuator_constraint(actuator, model, variables):
    constraint = ("IFF('%s', AND('%s', AND('%s', AND('%s', '%s'))))"
                  %(powered(actuator), connected('Power-Board', actuator),
                    powered('Power-Board'), working('Power-Board'),
                    signal(actuator, 'Power-Board')))
    add_constraint_to_model(constraint, model, variables)

def create_powered_constraints(model, variables):
    add_constraint_to_model(LIT(powered('Outlet')), model, variables)
    
    create_powered_constraint('Outlet', 'Rasp-Pi', model, variables)
    create_powered_constraint('Outlet', 'Power-Board', model, variables)

    for actuator in actuators:
        create_powered_actuator_constraint(actuator, model, variables)

def create_signal_constraints(model, variables):
    # BEGIN STUDENT CODE
    sensors0 = ['H-T0', 'Light0', 'Moisture0']
    sensors1 = ['H-T1', 'Light1', 'Moisture1']

    #6 constraints
    for sensor in sensors0:
        sensor_to_sb0 = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                  %(signal(sensor, 'Sensor-Board0'), connected(sensor, 'Sensor-Board0'),
                    working(sensor), signal(sensor, sensor)))
        sensor_to_arduino = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                  %(signal(sensor, 'Arduino'), connected('Sensor-Board0', 'Arduino'),
                    working('Sensor-Board0'), signal(sensor, 'Sensor-Board0')))
        add_constraint_to_model(sensor_to_sb0, model, variables)
        add_constraint_to_model(sensor_to_arduino, model, variables)

    #6 constraints = 12
    for sensor in sensors1:
        sensor_to_sb1 = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                %(signal(sensor, 'Sensor-Board1'), connected(sensor, 'Sensor-Board1'),
                working(sensor), signal(sensor, sensor)))
        sensor_to_arduino = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                  %(signal(sensor, 'Arduino'), connected('Sensor-Board1', 'Arduino'),
                    working('Sensor-Board1'), signal(sensor, 'Sensor-Board1')))
        add_constraint_to_model(sensor_to_sb1, model, variables)
        add_constraint_to_model(sensor_to_arduino, model, variables)

    #7 constraints = 19
    for sensor in sensors:
        sensor_to_rasppi = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                  %(signal(sensor, 'Rasp-Pi'), connected('Arduino', 'Rasp-Pi'),
                    working('Arduino'), signal(sensor, 'Arduino')))
        add_constraint_to_model(sensor_to_rasppi, model, variables)

    #1 constraint = 20
    wlvl_to_arduino = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                %(signal('Wlevel', 'Arduino'), connected('Wlevel', 'Arduino'),
                working('Wlevel'), signal('Wlevel', 'Wlevel')))
    add_constraint_to_model(wlvl_to_arduino, model, variables)
    
    #6 constraints = 26
    for actuator in actuators:
        actuator_to_arduino = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                %(signal(actuator, 'Arduino'), connected('Rasp-Pi', 'Arduino'),
                working('Rasp-Pi'), signal(actuator, 'Rasp-Pi')))
        add_constraint_to_model(actuator_to_arduino, model, variables)

        actuator_to_pb = ("IFF('%s', AND('%s', AND('%s', '%s')))"
                %(signal(actuator, 'Power-Board'), connected('Arduino', 'Power-Board'),
                working('Arduino'), signal(actuator, 'Arduino')))
        add_constraint_to_model(actuator_to_pb, model, variables)
    # END STUDENT CODE
    pass

def create_sensor_generation_constraints(model, variables):
    # BEGIN STUDENT CODE
    sensors = ['H-T0', 'Light0', 'Moisture0', 'H-T1', 'Light1', 'Moisture1', 'Wlevel']

    for sensor in sensors:
        constraint = "IFF('%s', '%s')" % (signal(sensor, sensor), working(sensor))
        add_constraint_to_model(constraint, model, variables)
    # END STUDENT CODE
    pass

def create_expected_result_constraints(model, variables):
    # BEGIN STUDENT CODE
    # Expected result for Fans
    # Fans
    add_constraint_to_model("IFF('%s', AND('%s', AND('%s', OR('%s', '%s'))))" % (
        expected_result('Fans'), powered('Fans'), working('Fans'), 
        signal('H-T0', 'Rasp-Pi'), signal('H-T1', 'Rasp-Pi')), model, variables)
    
    # LEDs
    add_constraint_to_model("IFF('%s', AND('%s', AND('%s', OR('%s', '%s'))))" % (
        expected_result('LEDs'), powered('LEDs'), working('LEDs'), 
        signal('Light0', 'Rasp-Pi'), signal('Light1', 'Rasp-Pi')), model, variables)
    
    # Pump
    add_constraint_to_model("IFF('%s', AND('%s', AND('%s', OR('%s', OR('%s', '%s')))))" % (
        expected_result('Pump'), powered('Pump'), working('Pump'), 
        signal('Moisture0', 'Rasp-Pi'), signal('Moisture1', 'Rasp-Pi'), signal('Wlevel', 'Rasp-Pi')), model, variables)
    # END STUDENT CODE
    pass

def create_constraints(model, variables):
    create_powered_constraints(model, variables)
    create_signal_constraints(model, variables)
    create_sensor_generation_constraints(model, variables)
    create_expected_result_constraints(model, variables)

def create_greenhouse_model():
    model = cp_model.CpModel()
    variables = create_relation_variables(model)
    create_constraints(model, variables)
    return (model, variables)
    
def collect_diagnosis(solver, variables):
    return set([var for var in variables
                if ((var.startswith('connected') or var.startswith('working')) and
                    solver.BooleanValue(variables[var]) == False)])

class DiagnosesCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        # BEGIN STUDENT CODE
        self.variables = variables
        self.diagnoses = []
        # END STUDENT CODE

    def OnSolutionCallback(self):
        # Extract the connected and working relations that are False
        # BEGIN STUDENT CODE
        diagnosis = collect_diagnosis(self, self.variables)
        self.diagnoses.append(diagnosis)
        # END STUDENT CODE
        pass

def diagnose(observations):
    model, variables = create_greenhouse_model()
    add_constraint_to_model(observations, model, variables)

    collector = DiagnosesCollector(variables)
    diagnoses = []
    solver = cp_model.CpSolver()
    solver.SearchForAllSolutions(model, collector)
    # Remove all redundant diagnoses (those that are supersets
    #   of other diagnoses).
    # BEGIN STUDENT CODE
    diagnoses = collector.diagnoses
    minimal_diagnoses = []
    
    for diag in diagnoses:
        if not any(diag > other for other in diagnoses):
            minimal_diagnoses.append(diag)

    return minimal_diagnoses
    # END STUDENT CODE

    # return diagnoses