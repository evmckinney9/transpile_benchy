"""Numerical decomposition of unitary gates.

Define the decomposition circuit ansatz. This class holds a :class:
qiskit.circuit.QuantumCircuit object, with auxiliary methods to : (0) define
the ansatz with the unitary target, (1) iteratively add layers of gates to the
circuit, (2) evaluate a modular cost function of decomposition, (used in the
optimization) (3) determine an optimized placement of the next basis gate in
the circuit.

An example cost function evaluates the target followed by inverse ansatz circuit.
Therefore, decomposition is complete when the entire circuit converges to identity,
T@U^dagger = I; i.e. the target has been "undone" by the decomposition circuit.

References:
    [1] https://github.com/Pitt-JonesLab/slam_decomposition/blob/main/slam/basis_abc.py
    [2] https://qiskit.org/documentation/stubs/qiskit.circuit.library.EfficientSU2.html

Later, we can extend this class to become a qiskit.transpiler.TransformationPass,
which can be used in the transpiler pipeline.
"""

from abc import ABC, abstractmethod

import numpy as np
from qiskit import QuantumCircuit
from qiskit.algorithms.optimizers import (
    L_BFGS_B,
    NELDER_MEAD,
    Optimizer,
    OptimizerResult,
)
from qiskit.circuit import Parameter
from qiskit.circuit.library import UGate
from qiskit.extensions import UnitaryGate
from qiskit.quantum_info import Operator
from weylchamber import J_T_LI


class CircuitAnsatzDecomposer(ABC):
    """Abstract base class for circuit ansatz decomposers."""

    max_iterations = 8  # maximum number of iterations allowed
    reinitialize_attempts = 8

    def __init__(self, basis_gates: list[UnitaryGate]):
        """Initialize the CircuitAnsatzDecomposer class.

        Args:
            target: The unitary target to be decomposed.
            basis_gates: The basis gates to be used in the decomposition.
        """
        self.num_qubits = target.num_qubits
        self.basis_gates = basis_gates
        # assert that all basis_gates >= 2 qubits
        # assert all([basis_gate[0].num_qubits >= 2 for basis_gate in basis_gates])

        self.optimizer: Optimizer = None
        self.convergence_threshold = 1e-6

    def __call__(
        self, target: UnitaryGate, ansatz: QuantumCircuit = None
    ) -> QuantumCircuit:
        """Decompose the target unitary using the basis gates."""
        if ansatz is not None:
            return self.decompose_from_ansatz(target, ansatz)
        return self.decompose(target)

    def decompose(self, target: UnitaryGate) -> QuantumCircuit:
        """Decompose the target unitary using the basis gates.

        NOTE this strategy of repeately place basis followed by
        optimization is similar to QSearch algorithm [1]. This could be
        done in different ways, where not optimizing after each
        placement, e.g. don't bother optimizing until some sufficient
        condition of ansatz expressibility is met.
        """
        # assert target is size of num_qubits
        # optionally, could fix by padding with identity
        assert target.num_qubits == self.num_qubits

        self.converged = False
        self.parameter_count = 0
        self.parameter_values = []
        self.best_cost = None

        self.ansatz = QuantumCircuit(self.num_qubits)
        self._initialize_1Q_gates()

        iterations = 0
        while not self.converged and iterations < self.max_iterations:
            self._iterate_basis()
            for _ in range(
                self.reinitialize_attempts
            ):  # number of times to reinitialize and train on a fixed size template
                ret = self._optimize_parameters(target)
                if self.converged:
                    break
            iterations += 1

        print("Final cost: ", ret.fun)
        # bind the parameters to the circuit
        return self.ansatz.assign_parameters(self.parameter_values)

    def _initialize_1Q_gates(self):
        """Apply a 1Q gate on all qubits."""
        for i in range(self.num_qubits):
            u_params = [
                Parameter(f"p{i:03}")
                for i in range(self.parameter_count, self.parameter_count + 3)
            ]
            self.parameter_count += 3
            self.ansatz.append(UGate(*u_params), [i])

    def decompose_from_ansatz(
        self, target: UnitaryGate, ansatz: QuantumCircuit
    ) -> QuantumCircuit:
        """Decompose the target, only using the given ansatz."""
        assert target.num_qubits == ansatz.num_qubits
        self.converged = False
        self.best_cost = None
        for _ in range(self.reinitialize_attempts):
            ret = self._optimize_parameters(target, ansatz)
            if self.converged:
                break

        print("Final cost: ", ret.fun)
        # bind the parameters to the circuit
        return ansatz.assign_parameters(self.parameter_values)

    @abstractmethod
    def _iterate_basis(self) -> None:
        """Add the next basis gate to the circuit.

        The important question for multi-decomposition is how to determine
        (a) where to place the next gate, and for mixed basis set decomposition
        (b) which gate to place.

        Some methods for (a) include:
            - linear, full, or
            - greedy placement, (bqskit, uses QSearch algorithm which tries all possible
            placements and chooses the best one as root node for the next iteration)
            - iterative disentanglement (SQUANDER)[?]

        Some methods for (b) include:
            - greedy basis selection

        References:
            [3] https://github.com/BQSKit/qsearch
        """
        return NotImplementedError

    @abstractmethod
    def _cost_function(self, target: UnitaryGate, x: np.ndarray) -> float:
        """Evaluate the cost function of the decomposition.

            Args:
            target (UnitaryGate): the target unitary to be decomposed
            x (np.ndarray): the parameter values to evaluate the cost function at,
            passed by the optimizer.minimize function

        References:
            [1] https://github.com/Pitt-JonesLab/slam_decomposition/blob/main/slam/cost_function.py
        """
        return NotImplementedError

    def _optimize_parameters(self, target: UnitaryGate) -> OptimizerResult:
        """Optimize the parameters of the circuit (1Q gates).

        For example, using the :class:
        qiskit.algorithms.optimizers.Optimizer class.
        """
        if self.optimizer is None:
            raise ValueError("Optimizer must be instantiated in the subclass.")

        if len(self.parameter_values) != self.parameter_count:
            self.parameter_values = np.random.uniform(
                -2 * np.pi, 2 * np.pi, self.parameter_count
            )

        def _func(x: np.ndarray) -> float:
            return self._cost_function(target, x)

        ret = self.optimizer.minimize(fun=_func, x0=self.parameter_values)

        # ret.fun is the final cost function value
        self.converged = ret.fun <= self.convergence_threshold
        # ret.x is the final parameter values
        if self.best_cost is None or ret.fun < self.best_cost:
            self.best_cost = ret.fun
            self.parameter_values = ret.x

        return ret


class LinearAnsatz(CircuitAnsatzDecomposer):
    """Linear placement of basis gates."""

    def _iterate_basis(self) -> None:
        """Add the next basis gate to the circuit."""
        return self._linear_placement()

    def _linear_placement(self) -> None:
        """Use linear placement to add the next basis gate to the circuit.

        edge list assumes A2A connectivity, but optionally could be specificed by user
        strategy is to use edge as (index, index+1, ... index+n), where n is the number
        of qubits in the gate
        """
        basis_gate, basis_param_len = self.basis_gates[self.basis_gate_index]

        if basis_param_len > 0:
            basis_gate_params = [
                Parameter(f"p{i:03}")
                for i in range(
                    self.parameter_count, self.parameter_count + basis_param_len
                )
            ]
            basis_gate = basis_gate(*basis_gate_params)
            self.parameter_count += basis_param_len
        else:
            basis_gate = basis_gate()

        # get edge as list of qubit indices
        basis_gate_size = basis_gate.num_qubits
        if basis_gate_size > self.num_qubits:
            raise ValueError(
                "Basis gate size must be less than or equal to the number of qubits."
            )

        edge_indices = [
            i % self.num_qubits
            for i in range(self.edge_index, self.edge_index + basis_gate_size)
        ]

        # add the basis gate to the circuit
        self.ansatz.append(basis_gate, edge_indices)

        # append 1Q gates to all qubits the basis gate was just on
        for i in edge_indices:
            u_params = [
                Parameter(f"p{i:03}")
                for i in range(self.parameter_count, self.parameter_count + 3)
            ]
            self.parameter_count += 3
            self.ansatz.append(UGate(*u_params), [i])

        # wrap index around for linear placement
        self.basis_gate_index += 1
        self.basis_gate_index %= len(self.basis_gates)
        self.edge_index += 1
        self.edge_index %= self.num_qubits


class HilbertSchmidt(CircuitAnsatzDecomposer):
    """Use Hilbert-Schmidt distance as the cost function."""

    def _cost_function(self, target: UnitaryGate, x: np.ndarray) -> float:
        """Evaluate the cost function of the decomposition."""
        bind_circuit = self.ansatz.assign_parameters(x)
        current_u = Operator(bind_circuit).data
        target_unitary = Operator(target.inverse()).data
        return self._hilbert_schmidt_cost(target_unitary, current_u)

    def _hilbert_schmidt_cost(
        self, target_unitary: np.ndarray, current_unitary: np.ndarray
    ) -> float:
        """Evaluate the Hilbert-Schmidt inner product.

        A value of 0 indicates perfect overlap, and a value of
        1 indicates no overlap. (?) # TODO check this.

        References:
            [4] https://mrmgroup.cs.princeton.edu/papers/pmurali-isca21.pdf
        """
        dim = target_unitary.shape[0]
        return 1 - np.abs(np.trace(current_unitary @ target_unitary)) / dim


class MakhlinFunctional(CircuitAnsatzDecomposer):
    """Use Makhlin functional as the cost function."""

    def __init__(self, **kwargs):
        """Initialize the MakhlinFunctional class.

        Note that this class is only defined for 2 qubits.
        """
        super().__init__(**kwargs)
        assert self.num_qubits == 2

    def _cost_function(self, target: UnitaryGate, x: np.ndarray) -> float:
        """Evaluate the cost function of the decomposition."""
        bind_circuit = self.ansatz.assign_parameters(x)
        current_u = Operator(bind_circuit).data
        target_u = Operator(target).data
        return self._makhlin_functional(target_u, current_u)

    def _makhlin_functional(
        self, target_unitary: np.ndarray, current_unitary: np.ndarray
    ) -> float:
        """Evaluate the Makhlin functional."""
        return J_T_LI(target_unitary, current_unitary)


class BasicDecomposer(LinearAnsatz, HilbertSchmidt):
    """Basic decomposition class."""

    def __init__(self, basis_gates: list[UnitaryGate]):
        """Initialize the Basic class."""
        super().__init__(basis_gates=basis_gates)
        self.optimizer = L_BFGS_B()
        self.basis_gate_index = 0
        self.edge_index = 0


class Advanced2QDecomposer(LinearAnsatz, MakhlinFunctional):
    """Advanced decomposition class."""

    def __init__(self, basis_gates: list[UnitaryGate]):
        """Initialize the Advanced class."""
        super().__init__(basis_gates=basis_gates)
        self.optimizer = NELDER_MEAD()
        self.basis_gate_index = 0
        self.edge_index = 0


if __name__ == "__main__":
    import numpy as np
    from qiskit.circuit.library import RZXGate

    target = QuantumCircuit(2)
    # target.h(0)
    # target.cx(0, 1)
    # target.cx(1, 2)

    target.rzx(7 * np.pi / 8, 0, 1)
    # target.ccx(1, 2, 0)
    target.rzx(9 * np.pi / 8, 1, 0)

    # basis gates are tuples of (gate, num_params)
    # NOTE, basis gate is only parameterized if considering a continuous basis set
    # basis_gates = [(RZXGate, 1), (CCXGate, 0)]
    basis_gates = [(RZXGate, 1)]

    decomposer = BasicDecomposer(basis_gates)
    ansatz = decomposer(target)
    print(ansatz)

    decomposer = Advanced2QDecomposer(basis_gates)
    ansatz = decomposer(target)
    print(ansatz)
