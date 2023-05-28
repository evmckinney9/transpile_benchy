"""This is the interface for quantum circuit sources, i.e., submodules.

The base class SubmoduleInterface has the abstract method
get_quantum_circuits(), which should return a list of QuantumCircuits.
This class is intended to be subclassed for different sources of
QuantumCircuits. Example subclasses provided are QASMBench and RedQueen.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from qiskit import QuantumCircuit
from qiskit.circuit import CircuitError


class SubmoduleInterface(ABC):
    """Abstract class for a submodule."""

    @abstractmethod
    def get_quantum_circuits(self) -> List[QuantumCircuit]:
        """Return a list of QuantumCircuits."""
        pass

    @staticmethod
    def _load_qasm_file(file: Path) -> QuantumCircuit:
        """Load a QASM file."""
        try:
            with open(file, "r") as f:
                qc = QuantumCircuit.from_qasm_str(f.read())
            return qc
        except CircuitError as e:
            print(f"Failed to load {file}: {e}")
            return None


class QASMBench(SubmoduleInterface):
    """Submodule for QASMBench circuits."""

    def get_quantum_circuits(self, size: str) -> List[QuantumCircuit]:
        """Return a list of QuantumCircuits.

        Args:
        size: 'small', 'medium', or 'large'
        """
        qasm_files = self._get_qasm_files("QASMBench", size)
        return [self._load_qasm_file(file) for file in qasm_files]

    @staticmethod
    def _get_qasm_files(directory: str, size: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent
        qasm_files = prepath.glob(f"submodules/{directory}//{size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        # harcode, remove these files that are just way too big
        too_big = ["vqe", "bwt"]
        qasm_files = filter(
            lambda file: not any(x in str(file) for x in too_big), qasm_files
        )
        return list(qasm_files)


class RedQueen(SubmoduleInterface):
    """Submodule for RedQueen circuits."""

    def get_quantum_circuits(self) -> List[QuantumCircuit]:
        """Return a list of QuantumCircuits."""
        qasm_files = self._get_qasm_files("red-queen")
        return [self._load_qasm_file(file) for file in qasm_files]

    @staticmethod
    def _get_qasm_files(directory: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent
        qasm_files = prepath.glob(
            f"submodules/{directory}/red_queen/games/applications/qasm/*.qasm"
        )
        return list(qasm_files)
