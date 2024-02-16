"""QASM submodule interface."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface
from transpile_benchy.interfaces.errors import CircuitNotFoundError


class QASMInterface(SubmoduleInterface, ABC):
    """Abstract class for a submodule that has QASM files."""

    def __init__(self, filter_config: Optional[Dict[str, List[str]]] = None) -> None:
        """Initialize QASM submodule."""
        self.path_dict = self._get_path_dict()
        super().__init__(filter_config)

    def _get_all_circuits(self) -> List[str]:
        """Return a list of all possible circuits."""
        return list(self.path_dict.keys())

    def _load_circuit(self, circuit_str: str) -> QuantumCircuit:
        """Load a QuantumCircuit from a string."""
        if circuit_str not in self.path_dict:
            raise CircuitNotFoundError(f"Circuit {circuit_str} not found.")
        circuit_path = self.path_dict[circuit_str]

        try:
            with open(circuit_path, "r") as f:
                qc = QuantumCircuit.from_qasm_str(f.read())
                qc.name = circuit_str
            return qc
        except Exception as e:
            raise CircuitNotFoundError(f"Failed to load {circuit_path}: {e}")

    @abstractmethod
    def _get_path_dict(self) -> Dict[str, Path]:
        """Return a dictionary mapping circuit names to their file paths."""
        raise NotImplementedError


class Hardcoded(QASMInterface):
    """Submodule for .qasm manually loaded into hardcoded/."""

    def _get_path_dict(self) -> Dict[str, str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent
        qasm_files = prepath.glob("hardcoded/*.qasm")
        return {file.stem: str(file) for file in qasm_files}


class QASMBench(QASMInterface):
    """Submodule for QASMBench circuits."""

    def __init__(
        self,
        size: str = None,
        filter_config: Optional[Dict[str, List[str]]] = None,
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

    def _get_path_dict(self) -> Dict[str, str]:
        """Return a dictionary mapping circuit names to their file paths."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(f"submodules/QASMBench/{self.size}/**/*.qasm")
        # specific to this interface - filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        return {file.stem: str(file) for file in qasm_files}


class RedQueen(QASMInterface):
    """Submodule for RedQueen circuits."""

    def _get_path_dict(self) -> Dict[str, str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob("submodules/red-queen/red_queen/games/**/*.qasm")

        # exclude red_queen/games/mapping/benchmarks/queko
        qasm_files = filter(lambda file: "queko" not in str(file), qasm_files)

        # # specific to this interface - need to change _{x} to _n{x} in file names
        # if doesn't have a '_', then return the original name
        # NOTE: files may have multiple '_'s, but we only care about the last one
        def conventional_filename(stem):
            parts = stem.rsplit(
                "_", 1
            )  # split the stem from the right at the first underscore
            if len(parts) == 1:
                # If there is no underscore, return the original name
                return stem
            else:
                # Insert _n between the last two parts
                return "_n".join(parts)

        return {conventional_filename(file.stem): str(file) for file in qasm_files}


class Queko(QASMInterface):
    """Submodule for Queko circuits."""

    def _get_path_dict(self) -> Dict[str, str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob("submodules/QUEKO-benchmark/BNTF/*.qasm")
        return {file.stem: str(file) for file in qasm_files}


class BQSKitInterface(QASMInterface):
    """Submodule for BQSKit circuits."""

    def _get_path_dict(self) -> Dict[str, str]:
        """Return a list of all possible circuits."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(
            "submodules/bqskit/tests/passes/partitioning/_data/*.qasm"
        )

        def conventional_filename(stem):
            return (
                f"{re.findall('[a-zA-Z]+', stem)[0]}_n{re.findall('[0-9]+$', stem)[0]}"
            )

        return {conventional_filename(file.stem): str(file) for file in qasm_files}
