"""Main test runner."""

from qiskit import QuantumCircuit
from qiskit.circuit.library.standard_gates import CXGate
from qiskit.transpiler import CouplingMap, PassManager
from qiskit.transpiler.passes import (
    ApplyLayout,
    BasicSwap,
    EnlargeWithAncilla,
    FullAncillaAllocation,
    SabreLayout,
    SabreSwap,
    TrivialLayout,
)

from transpile_benchy.metrics import DepthMetric
from transpile_benchy.runner import CustomPassManager

depth_metric = DepthMetric(basis_gate=CXGate())


class Trivial_Basic(CustomPassManager):
    """Custom pass manager."""

    def build_pre_process(self):
        """Build the pre-process PassManager."""
        return super().build_pre_process()

    def build_post_process(self):
        """Build the post-process PassManager."""
        pm = PassManager()
        pm.append(depth_metric.get_pass())
        return pm

    def build_main_process(self):
        """Process the circuit."""
        pm = PassManager()
        pm.append(
            [
                TrivialLayout(self.coupling),
                FullAncillaAllocation(self.coupling),
                EnlargeWithAncilla(),
                ApplyLayout(),
                BasicSwap(self.coupling),
            ]
        )
        return pm


class SABRE(CustomPassManager):
    """Custom pass manager."""

    def build_pre_process(self):
        """Build the pre-process PassManager."""
        return super().build_pre_process()

    def build_post_process(self):
        """Build the post-process PassManager."""
        pm = PassManager()
        pm.append(depth_metric.get_pass())
        return pm

    def build_main_process(self):
        """Process the circuit."""
        pm = PassManager()
        pm.append(
            [
                SabreLayout(self.coupling),
                # FullAncillaAllocation(coupling_map),
                # EnlargeWithAncilla(),
                # ApplyLayout(),
                SabreSwap(self.coupling),
            ]
        )
        return pm


def test_custom_pass_manager_trivial_basic():
    """Test custom pass manager."""
    coupling_map = CouplingMap.from_grid(4, 5)
    manager = Trivial_Basic(coupling=coupling_map)
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    transpiled_circuit = manager.run(circuit)
    assert (
        transpiled_circuit.depth() <= circuit.depth()
    ), "Transpiled circuit should not be deeper than original."


def test_custom_pass_manager_sabre():
    """Test custom pass manager."""
    coupling_map = CouplingMap.from_grid(4, 5)
    manager = SABRE(coupling=coupling_map)
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    transpiled_circuit = manager.run(circuit)
    assert (
        transpiled_circuit.depth() <= circuit.depth()
    ), "Transpiled circuit should not be deeper than original."
