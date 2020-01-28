from numerous.engine.system import Item, Subsystem
from numerous.multiphysics import EquationBase, Equation
from numerous.engine.simulation.simulation_callbacks import _SimulationCallback
from numerous.engine.variables import OverloadAction
from numerous.engine.model import Model, Model_old
from numerous.engine.simulation import Simulation, Simulation_old
import numpy as np
import matplotlib.pyplot as plt
import pytest
from pytest import approx


class Item1(Item, EquationBase):
    def __init__(self, tag='item1'):
        super(Item1, self).__init__(tag)
        self.t1 = self.create_namespace('t1')
        self.add_state('x', 1)
        self.add_state('t', 0)
        self.t1.add_equations([self])

    @Equation()
    def eval(self, scope):
        scope.t_dot = 1
        scope.x_dot = -1 * np.exp(-1 * scope.t)

class DummyHistorian:
    def __init__(self):
        self.callback = _SimulationCallback("save to dataframe")
        self.callback.add_callback_function(self.update)
    def update(self, a, b):
        pass


class Subsystem1(Subsystem, EquationBase):
    def __init__(self, tag='subsystem1', item1=object):
        super(Subsystem1, self).__init__(tag)
        self.t1 = self.create_namespace('t1')
        self.add_parameter('x_dot_mod', 0)
        self.t1.add_equations([self])
        self.register_items([item1])

        item1.t1.x_dot += self.t1.x_dot_mod
        print(self.t1.x_dot_mod)

    @Equation()
    def eval(self, scope):
        scope.x_dot_mod = -1


#@pytest.fixture
def system1():
    class System(Subsystem, EquationBase):
        def __init__(self, tag='system1', subsystem1=object):
            super(System, self).__init__(tag)

            self.register_items([subsystem1])
    return System(subsystem1=Subsystem1(item1=Item1()))

def expected_sol(t):
    return -1*(t*np.exp(t) -1)*np.exp(-t)

def test_overloadaction_sum(system1):
    #model = Model(system1, historian=DummyHistorian())
    model = Model(system1)
    sim = Simulation(model, t_start=0, t_stop=20, num=500)
    sim.solve()
    df = sim.model.historian.df
    df['expected_sol'] = expected_sol(np.linspace(20/500, 20, 500))
    df.plot(y=['system1.subsystem1.item1.t1.x', 'expected_sol'])
    plt.show()
    #assert approx(np.array(df['system1.subsystem1.item1.t1.x']), rel=100) == expected_sol(np.linspace(0, 10, 101)[1:])

if __name__ == "__main__":
    sys1 = system1()
    test_overloadaction_sum(sys1)