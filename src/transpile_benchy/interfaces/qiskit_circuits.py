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

depth = 2  # arbitary idk what to set this to


# VQE
def vqe_linear(q):
    """Return a VQE circuit with linear entanglement."""
    vqe_linear.__name__ = f"vqe_linear_{q}"
    # set np random seed
    # np.random.seed(42)
    # apply the ansatz depth times
    vqe_circuit_linear = EfficientSU2(
        num_qubits=q, entanglement="linear", reps=depth * 2
    )
    for param in vqe_circuit_linear.parameters:
        vqe_circuit_linear.assign_parameters({param: np.random.rand()}, inplace=1)
    return vqe_circuit_linear


def vqe_full(q):
    """Return a VQE circuit with full entanglement."""
    vqe_full.__name__ = f"vqe_full_{q}"
    # set np random seed
    # np.random.seed(42)
    vqe_circuit_full = EfficientSU2(num_qubits=q, entanglement="full")
    for param in vqe_circuit_full.parameters:
        vqe_circuit_full.assign_parameters({param: np.random.rand()}, inplace=1)
    return vqe_circuit_full


# Quantum Volume
def qv(q):
    """Return a Quantum Volume circuit."""
    qv.__name__ = f"qv_{q}"
    qv_qc = QuantumVolume(num_qubits=q, depth=q)
    return qv_qc


# QFT
def qft(q):
    """Return a QFT circuit."""
    qft.__name__ = f"qft_{q}"
    qft_qc = QFT(q)
    return qft_qc


# QAOA
def qaoa(q):
    """Return a QAOA circuit."""
    qaoa.__name__ = f"qaoa_{q}"
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
        cost_operator=qc_p, reps=depth, initial_state=None, mixer_operator=qc_mix
    )
    return qaoa_qc


# Adder
def adder(q):
    """Return a ripple carry adder circuit."""
    adder.__name__ = f"radd_{q}"
    if q % 2 != 0:
        raise ValueError("q must be even")
    add_qc = QuantumCircuit(q).compose(
        CDKMRippleCarryAdder(num_state_qubits=int((q - 1) / 2)), inplace=False
    )
    return add_qc


# Multiplier
def multiplier(q):
    """Return a rgqft multiplier circuit."""
    multiplier.__name__ = f"mul_{q}"
    if q % 4 != 0:
        raise ValueError("q must be divisible by 4")
    mul_qc = QuantumCircuit(q).compose(
        RGQFTMultiplier(num_state_qubits=int(q / 4)), inplace=False
    )
    return mul_qc


# GHZ
def ghz(q):
    """Return a GHZ circuit."""
    ghz.__name__ = f"ghz_{q}"
    ghz_qc = QuantumCircuit(q)
    ghz_qc.h(0)
    for i in range(1, q):
        ghz_qc.cx(0, i)
    return ghz_qc


# Hidden Linear Function
def hlf(q):
    """Return a Hidden Linear Function circuit."""
    hlf.__name__ = f"hlf_{q}"
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
    grover.__name__ = f"grover_{q}"
    q = int(q / 2)  # Grover's take so long because of the MCMT, do a smaller circuit
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


# List of all available circuits
available_circuits = [
    vqe_full,
    vqe_linear,
    qv,
    qft,
    qaoa,
    adder,
    multiplier,
    ghz,
    hlf,
    grover,
]
