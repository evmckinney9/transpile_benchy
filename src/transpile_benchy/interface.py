"""This is the interface for quantum circuit sources, i.e., submodules.

The base class SubmoduleInterface has the abstract method
get_quantum_circuits(), which should return a list of QuantumCircuits.
This class is intended to be subclassed for different sources of
QuantumCircuits. Example subclasses provided are QASMBench and RedQueen.

File is written with intention that a submodule could either be written
in the form of having a list of QASM files, or having a set of functions
which return QuantumCircuits. The latter is not yet implemented.

Also, we write using Iterator, for sake of memory efficiency, don't want
to spend time building all QuantumCircuits, only build them when needed.
"""
from abc import ABC, abstractmethod
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Type

from mqt.bench.benchmark_generator import get_benchmark
from mqt.bench.utils import get_supported_benchmarks

# from qiskit.circuit.exceptions import QasmError
from qiskit import QuantumCircuit
from qiskit.circuit import QuantumCircuit
import re

### TODO FIXME, the filtering is so bad right now
## refactor, so we filter at lower class levels


class SubmoduleInterface(ABC):
    """Abstract class for a submodule."""

    def __init__(self) -> None:
        self.raw_circuits = None

    def get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over filtered QuantumCircuits."""
        for qc in self._get_quantum_circuits():
            yield qc

    def circuit_count(self) -> int:
        """Returns total number of QuantumCircuits post filtering."""
        return len(self.raw_circuits)


class QiskitInterface(SubmoduleInterface):
    """Abstract class for a submodule that has Qiskit functions."""

    def __init__(self) -> None:
        self.raw_circuits = self._get_qiskit_functions()

    @abstractmethod
    def _get_qiskit_functions(self) -> List[Callable]:
        """Return a list of Qiskit functions."""
        raise NotImplementedError


class QASMInterface(SubmoduleInterface):
    """Abstract class for a submodule that has QASM files."""

    def __init__(self, filter_list) -> None:
        self.raw_circuits = self.get_filtered_files(filter_list)

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
        if filter_list is None or self.qasm_files is None:
            return self.qasm_files

        return [
            s
            for s in self.qasm_files
            if any(re.search(pattern, s.stem) for pattern in filter_list)
        ]

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
        prepath = Path(__file__).resolve().parent.parent.parent
        qasm_files = prepath.glob(f"submodules/{directory}/{size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        # harcode, remove these files that are just way too big or glithcing
        manual_reject = ["vqe", "bwt", "ising_n26", "inverseqft_n4"]
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
        prepath = Path(__file__).resolve().parent.parent.parent
        qasm_files = prepath.glob(
            f"submodules/{directory}/red_queen/games/applications/qasm/*.qasm"
        )
        return list(qasm_files)


class QiskitFunctionInterface(QiskitInterface):
    """Subclass of QiskitInterface with QuantumFunctionFactory integrated.

    This class encapsulates the process of generating Qiskit functions
    of a given type (e.g., QFT or QuantumVolume) for a specified set of
    qubit counts. The QuantumFunctionFactory nested class handles the
    generation of these functions.

    Example usage:\\ num_qubits = [8, 12, 16, 20, 24, 28, 32, 36]\\
    qiskit_functions_qft = QiskitFunctionInterface(QFT, num_qubits)\\
    qiskit_functions_qv = QiskitFunctionInterface(QuantumVolume,
    num_qubits)
    """

    class QuantumFunctionFactory:
        """Factory for creating quantum functions.

        This factory generates Qiskit functions of a given type for a
        specific list of qubit counts. The generated functions can then
        be retrieved as a list through the generate_functions method.
        """

        def __init__(self, function_type: Type[Callable], num_qubits: List[int]):
            self.function_type = function_type
            self.num_qubits = num_qubits

        def generate_functions(self) -> Dict[str, Callable]:
            """Generate a dictionary of quantum functions."""
            return {
                # f"{self.function_type.__name__.lower()}_{n}": self._create_function(n)
                f"{self.function_type.__name__}": self._create_function(n)
                for n in self.num_qubits
            }

        def _create_function(self, num_qubits: int) -> Callable:
            """Create a quantum function with the specified number of
            qubits."""
            func = self.function_type(num_qubits)
            # func.name = f"{self.function_type.__name__.lower()}_{num_qubits}"
            func.name = f"{self.function_type.__name__}"
            return func

    def __init__(self, function_type: Type[Callable], num_qubits: List[int]) -> None:
        self.function_factory = self.QuantumFunctionFactory(function_type, num_qubits)
        super().__init__()

    def _get_qiskit_functions(self) -> List[Callable]:
        """Returns a list of Qiskit functions generated by the
        QuantumFunctionFactory."""
        return list(self.function_factory.generate_functions().values())


class MQTBench(SubmoduleInterface):  # TODO needs filtering
    def __init__(self, num_qubits: int) -> None:
        super().__init__()
        self.num_qubits = num_qubits
        self.raw_circuits = get_supported_benchmarks()

    def _get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for bench_str in self.raw_circuits:
            if bench_str in ["shor", "groundstate"]:
                continue  # NOTE way too big
                # yield get_benchmark(
                #     benchmark_name=bench_str,
                #     level="alg",
                #     circuit_size=self.num_qubits,
                #     benchmark_instance_name="xsmall"
                # )
            else:
                yield get_benchmark(
                    benchmark_name=bench_str,
                    level="alg",
                    circuit_size=self.num_qubits,
                )
