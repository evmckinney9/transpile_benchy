"""QASM submodule interface."""
from pathlib import Path
from typing import Dict, List, Optional

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface
from transpile_benchy.library import CircuitNotFoundError


class QASMInterface(SubmoduleInterface):
    """Abstract class for a submodule that has QASM files."""

    def __init__(self, filter_config: Optional[Dict[str, List[str]]] = None) -> None:
        """Initialize QASM submodule."""
        super().__init__(filter_config)

    def _load_circuit(self, circuit_str: str) -> QuantumCircuit:
        """Load a QuantumCircuit from a string."""
        try:
            with open(circuit_str, "r") as f:
                qc = QuantumCircuit.from_qasm_str(f.read())
                qc.name = circuit_str.stem
            return qc
        except Exception as e:
            raise CircuitNotFoundError(f"Failed to load {circuit_str}: {e}")


class QASMBench(QASMInterface):
    """Submodule for QASMBench circuits."""

    def __init__(
        self, size: str = None, filter_config: Optional[Dict[str, List[str]]] = None
    ):
        """Initialize QASMBench submodule.

        size: 'small', 'medium', or 'large'
        """
        self.size = size or "**"
        if filter_config is None:
            filter_config = {}
        exclude_circuits = filter_config.setdefault("exclude", [])
        exclude_circuits += [
            "vqe",
            "bwt",
            "ising_n26",
            "inverseqft_n4",
            "cc_n12",
            "wstate_n27",
        ]
        super().__init__(filter_config)

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(f"submodules/QASMBench/{self.size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        return list(qasm_files)


class RedQueen(QASMInterface):
    """Submodule for RedQueen circuits."""

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob("submodules/red-queen/red_queen/games/**/*.qasm")
        return list(qasm_files)


class Queko(QASMInterface):
    """Submodule for Queko circuits.

    NOTE: Queko is a subset of RedQueen, so we don't need to add it to the library.
    """

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob("submodules/QUEKO-benchmark/BNTF/*.qasm")
        return list(qasm_files)


class BQSKitInterface(QASMInterface):
    """Submodule for BQSKit circuits."""

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(
            "submodules/bqskit/tests/passes/partitioning/_data/*.qasm"
        )
        return list(qasm_files)
