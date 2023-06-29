"""Main test runner."""

from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import (
    ApplyLayout,
    BasicSwap,
    EnlargeWithAncilla,
    FullAncillaAllocation,
    SabreLayout,
    SabreSwap,
    TrivialLayout,
)

from transpile_benchy.runner import CustomPassManager


class Trivial_Basic(CustomPassManager):
    """Custom pass manager."""

    def main_process(self):
        """Process the circuit."""
        self.pm.append(
            [
                TrivialLayout(self.coupling),
                FullAncillaAllocation(self.coupling),
                EnlargeWithAncilla(),
                ApplyLayout(),
                BasicSwap(self.coupling),
            ]
        )


class SABRE(CustomPassManager):
    """Custom pass manager."""

    def main_process(self):
        """Process the circuit."""
        self.pm.append(
            [
                SabreLayout(self.coupling),
                # FullAncillaAllocation(coupling_map),
                # EnlargeWithAncilla(),
                # ApplyLayout(),
                SabreSwap(self.coupling),
            ]
        )


def test_custom_pass_manager_trivial_basic():
    """Test custom pass manager."""
    coupling_map = CouplingMap.from_grid(4, 5)
    manager = Trivial_Basic(coupling_map)
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    transpiled_circuit = manager.pm.run(circuit)
    assert (
        transpiled_circuit.depth() <= circuit.depth()
    ), "Transpiled circuit should not be deeper than original."


def test_custom_pass_manager_sabre():
    """Test custom pass manager."""
    coupling_map = CouplingMap.from_grid(4, 5)
    manager = SABRE(coupling_map)
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    transpiled_circuit = manager.pm.run(circuit)
    assert (
        transpiled_circuit.depth() <= circuit.depth()
    ), "Transpiled circuit should not be deeper than original."
