"""QASM submodule interface."""
import re
from abc import abstractmethod
from pathlib import Path
from typing import Iterator, List, Optional

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit

from transpile_benchy.interfaces.abc_interface import SubmoduleInterface


class QASMInterface(SubmoduleInterface):
    """Abstract class for a submodule that has QASM files."""

    def __init__(self, filter_list) -> None:
        """Initialize QASM submodule."""
        self.raw_circuits = self.get_filtered_files(filter_list)

    def __len__(self):
        """Return the number of circuits."""
        return len(self.raw_circuits)

    def _load_qasm_file(self, file: Path) -> QuantumCircuit:
        """Load a QASM file."""
        try:
            with open(file, "r") as f:
                qc = QuantumCircuit.from_qasm_str(f.read())
                qc.name = file.stem
            return qc
        except Exception as e:
            print(f"Failed to load {file}: {e}")
            return None

    def _get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for file in self.raw_circuits:
            yield self._load_qasm_file(file)

    def get_filtered_files(self, filter_list) -> List:
        """Return a list of filtered QASM files."""
        if filter_list is None or self.qasm_files is None:
            return self.qasm_files

        return [
            s
            for s in self.qasm_files
            if any(re.search(pattern, s.stem) for pattern in filter_list)
        ]

    def __str__(self):
        """Build string as all the available circuit names."""
        return str([s.stem for s in self.qasm_files])

    @abstractmethod
    def _get_qasm_files(self, directory: str) -> List[Path]:
        """Return a list of QASM files."""
        raise NotImplementedError


class QASMBench(QASMInterface):
    """Submodule for QASMBench circuits."""

    def __init__(self, size: str, filter_list: Optional[List[str]] = None):
        """Initialize QASMBench submodule.

        size: 'small', 'medium', or 'large'
        """
        self.size = size
        self.qasm_files = self._get_qasm_files("QASMBench", self.size)
        super().__init__(filter_list)

    @staticmethod
    def _get_qasm_files(directory: str, size: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(f"submodules/{directory}/{size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        # harcode, remove these files that are just way too big or glithcing
        # cc_n12 has classical control, so it's not a good candidate
        manual_reject = ["vqe", "bwt", "ising_n26", "inverseqft_n4", "cc_n12"]
        qasm_files = filter(
            lambda file: not any(x in str(file) for x in manual_reject), qasm_files
        )
        return list(qasm_files)


class RedQueen(QASMInterface):
    """Submodule for RedQueen circuits."""

    def __init__(self, filter_str: Optional[str] = None):
        """Initialize RedQueen submodule."""
        self.qasm_files = self._get_qasm_files("red-queen")
        super().__init__(filter_str)

    @staticmethod
    def _get_qasm_files(directory: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent.parent.parent
        qasm_files = prepath.glob(
            f"submodules/{directory}/red_queen/games/applications/qasm/*.qasm"
        )
        return list(qasm_files)
