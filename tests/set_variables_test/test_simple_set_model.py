import pytest

from numerous.multiphysics.equation_decorators import Equation
from numerous.multiphysics.equation_base import EquationBase
from numerous.engine.system.item import Item
from numerous.engine.system import Subsystem, ItemsStructure
from pytest import approx
from numerous.engine import model, simulation
from numerous.engine.simulation.solvers.base_solver import solver_types


class Simple(EquationBase, Item):
    """
        Equation and item modelling a spring and dampener
    """

    def __init__(self, tag="simple", x0=1, k=1):
        super(Simple, self).__init__(tag)
        # define variables
        self.add_constant('k', k)

        self.add_state('x', x0)
        # define namespace and add equation
        mechanics = self.create_namespace('mechanics')
        mechanics.add_equations([self])

    @Equation()
    def eval(self, scope):
        scope.x_dot = scope.k + 0*scope.x


class SimpleSystem(Subsystem):
    def __init__(self, tag, k=.1, n=1, x0=[0]):
        super().__init__(tag)
        simples = []
        for i in range(n):
            # Create oscillator
            simple = Simple('simple' + str(i), k=k*(i+1), x0=x0[i])
            simples.append(simple)

        self.register_items(simples, tag="simples", structure=ItemsStructure.SET)



@pytest.mark.parametrize("solver", solver_types)
@pytest.mark.parametrize("use_llvm", [True, False])
def test_simple_set_model(solver, use_llvm):
    n = 100
    subsystem = SimpleSystem('system', k=.1, n=n, x0=[0]*n)

    s = simulation.Simulation(
        model.Model(subsystem,use_llvm=use_llvm),
        t_start=0, t_stop=1, num=100, num_inner=100, max_step=1,
        solver_type = solver
    )
    # Solve and plot
    s.solve()
    for i in range(n):
        assert approx(s.model.historian_df['system.SET_simples.simple'+ str(i) +'.mechanics.x'][100], rel=0.01) ==\
               s.model.historian_df['system.SET_simples.simple' + str(i) + '.mechanics.k'][100]

