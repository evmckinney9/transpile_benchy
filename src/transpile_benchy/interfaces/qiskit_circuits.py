"""Non-exhaustive list of circuits defined by Qiskit.

Each function returns a QuantumCircuit object, only paramerized by the
number of qubits.
"""
import networkx as nx
import numpy as np
from qiskit import QuantumCircuit
from qiskit.algorithms import AmplificationProblem, Grover
from qiskit.circuit.library import (
    EfficientSU2,
    HiddenLinearFunction,
    QAOAAnsatz,
    QuantumVolume,
)
from qiskit.circuit.library.arithmetic.adders.cdkm_ripple_carry_adder import (
    CDKMRippleCarryAdder,
)
from qiskit.circuit.library.arithmetic.multipliers import RGQFTMultiplier
from qiskit.circuit.library.basis_change import QFT
from qiskit.circuit.library import TwoLocal

depth = 4  # arbitary idk what to set this to


# VQE
def vqe_linear(q):
    """Return a VQE circuit with linear entanglement."""
    # set np random seed
    # np.random.seed(42)
    # apply the ansatz depth times
    vqe_circuit_linear = EfficientSU2(
        num_qubits=q, entanglement="linear", reps=depth * 2
    )
    for param in vqe_circuit_linear.parameters:
        vqe_circuit_linear.assign_parameters(
            {param: np.random.rand()}, inplace=1
        )
    return vqe_circuit_linear


def vqe_full(q):
    """Return a VQE circuit with full entanglement."""
    # set np random seed
    # np.random.seed(42)
    vqe_circuit_full = EfficientSU2(
        num_qubits=q, entanglement="full", reps=depth * 2
    )
    for param in vqe_circuit_full.parameters:
        vqe_circuit_full.assign_parameters(
            {param: np.random.rand()}, inplace=1
        )
    return vqe_circuit_full


# Quantum Volume
def qv(q):
    """Return a Quantum Volume circuit."""
    return QuantumVolume(num_qubits=q, depth=q)


# QFT
def qft(q):
    """Return a QFT circuit."""
    return QFT(q)


# QAOA
def qaoa(q):
    """Return a QAOA circuit."""
    # set np random seed
    # np.random.seed(42)
    qc_mix = QuantumCircuit(q)
    for i in range(0, q):
        qc_mix.rx(np.random.rand(), i)
    # create a random Graph
    G = nx.gnp_random_graph(q, 0.5)  # , seed=42)
    qc_p = QuantumCircuit(q)
    for pair in list(G.edges()):  # pairs of nodes
        qc_p.rzz(2 * np.random.rand(), pair[0], pair[1])
        qc_p.barrier()
    qaoa_qc = QAOAAnsatz(
        cost_operator=qc_p,
        reps=depth,
        initial_state=None,
        mixer_operator=qc_mix,
    )
    return qaoa_qc


# Adder
def adder(q):
    """Return a ripple carry adder circuit."""
    if q % 2 != 0:
        raise ValueError("q must be even")
    add_qc = QuantumCircuit(q).compose(
        CDKMRippleCarryAdder(num_state_qubits=int((q - 1) / 2)), inplace=False
    )
    return add_qc


# Multiplier
def mul(q):
    """Return a rgqft multiplier circuit."""
    if q % 4 != 0:
        raise ValueError("q must be divisible by 4")
    mul_qc = QuantumCircuit(q).compose(
        RGQFTMultiplier(num_state_qubits=int(q / 4)), inplace=False
    )
    return mul_qc


# GHZ
def ghz(q):
    """Return a GHZ circuit."""
    ghz_qc = QuantumCircuit(q)
    ghz_qc.h(0)
    for i in range(1, q):
        ghz_qc.cx(0, i)
    return ghz_qc


# Hidden Linear Function
def hlf(q):
    """Return a Hidden Linear Function circuit."""
    # set np random seed
    # np.random.seed(42)
    # create a random symmetric adjacency matrix
    adj_m = np.random.randint(2, size=(q, q))
    adj_m = adj_m + adj_m.T
    adj_m = np.where(adj_m == 2, 1, adj_m)
    hlf_qc = HiddenLinearFunction(adjacency_matrix=adj_m)
    return hlf_qc


# Grover
def grover(q):
    """Return a Grover circuit."""
    q = int(
        q / 2
    )  # Grover's take so long because of the MCMT, do a smaller circuit
    # set numpy seed
    np.random.seed(42)
    # integer iteration
    oracle = QuantumCircuit(q)
    # mark a random state
    oracle.cz(0, np.random.randint(1, q))
    problem = AmplificationProblem(oracle)
    g = Grover(
        iterations=int(depth / 2)
    )  # takes too long to find SWAPs if too many iters
    grover_qc = g.construct_circuit(problem)
    return grover_qc


# TwoLocal
# CX, iSWAP, sqrt(iSWAP), ECP
# twolocalcnot_n16
# twolocaliswap_n16
# twolocalsqrtiswap_n16
# twolocalecp_n16
from qiskit.circuit.library import TwoLocal, CXGate, iSwapGate
from qiskit.quantum_info.operators import Operator

ecp = QuantumCircuit(2)
ecp.append(iSwapGate().power(1 / 2), [0, 1])
ecp.swap(0, 1)
ecp = ecp.to_gate()


def two_local_function_generator(entanglement_gate, func_name):
    def twolocal(q):
        return TwoLocal(
            num_qubits=q,
            reps=depth,
            rotation_blocks=["rx", "ry"],
            entanglement_blocks=entanglement_gate,
        )

    twolocal.__name__ = func_name
    return twolocal


# Create functions using the generator:
twolocalcnot = two_local_function_generator(CXGate(), "twolocalcnot")
twolocaliswap = two_local_function_generator(iSwapGate(), "twolocaliswap")
twolocalsqrtiswap = two_local_function_generator(
    iSwapGate().power(1 / 2), "twolocalsqrtiswap"
)
twolocalecp = two_local_function_generator(ecp, "twolocalecp")

# List of all available circuits
available_circuits = [
    vqe_full,
    vqe_linear,
    qv,
    qft,
    qaoa,
    adder,
    mul,
    ghz,
    hlf,
    grover,
    twolocalcnot,
    twolocaliswap,
    twolocalsqrtiswap,
]
