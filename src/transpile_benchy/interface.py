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


class SubmoduleInterface(ABC):
    """Abstract class for a submodule."""

    def __init__(self, filter_str: Optional[str] = None) -> None:
        self.filter_str = filter_str

    def get_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over filtered QuantumCircuits."""
        for qc in self._get_raw_quantum_circuits():
            if self.filter_str is None or fnmatch(qc.name, f"*{self.filter_str}*"):
                yield qc

    @abstractmethod
    def _get_raw_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        pass

    @abstractmethod
    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits.

        Note that this assumes that generating the quantum circuits
        doesn't significantly change the total number of circuits, which
        might not be the case if some files fail to load or are filtered
        out.
        """
        pass


class QiskitInterface(SubmoduleInterface):
    """Abstract class for a submodule that has Qiskit functions."""

    def __init__(self, filter_str: Optional[str] = None) -> None:
        super().__init__(filter_str)
        self.qiskit_functions = self._get_qiskit_functions()

    def _get_raw_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        for qc in self.qiskit_functions:
            yield qc

    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits."""
        return len(self.qiskit_functions)

    @abstractmethod
    def _get_qiskit_functions(self) -> List[Callable]:
        """Return a list of Qiskit functions."""
        raise NotImplementedError


class QASMInterface(SubmoduleInterface):
    """Abstract class for a submodule that has QASM files."""

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

    def _get_raw_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for file in self.qasm_files:
            yield self._load_qasm_file(file)

    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits."""
        return len(self.qasm_files)

    @abstractmethod
    def _get_qasm_files(self, directory: str) -> List[Path]:
        """Return a list of QASM files."""
        raise NotImplementedError


class QASMBench(QASMInterface):
    """Submodule for QASMBench circuits."""

    def __init__(self, size: str):
        """Initialize QASMBench submodule.

        size: 'small', 'medium', or 'large'
        """
        self.size = size
        self.qasm_files = self._get_qasm_files("QASMBench", self.size)

    @staticmethod
    def _get_qasm_files(directory: str, size: str) -> List[Path]:
        """Return a list of QASM files."""
        prepath = Path(__file__).resolve().parent.parent.parent
        qasm_files = prepath.glob(f"submodules/{directory}/{size}/**/*.qasm")
        # filter out the transpiled files
        qasm_files = filter(lambda file: "_transpiled" not in str(file), qasm_files)
        # harcode, remove these files that are just way too big
        too_big = ["vqe", "bwt"]
        qasm_files = filter(
            lambda file: not any(x in str(file) for x in too_big), qasm_files
        )
        return list(qasm_files)


class RedQueen(QASMInterface):
    """Submodule for RedQueen circuits."""

    def __init__(self):
        """Initialize RedQueen submodule."""
        self.qasm_files = self._get_qasm_files("red-queen")

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

    This class encapsulates the process of generating Qiskit functions of a given type (e.g., QFT or QuantumVolume)
    for a specified set of qubit counts. The QuantumFunctionFactory nested class handles the generation of these
    functions.

    Example usage:\\
    num_qubits = [8, 12, 16, 20, 24, 28, 32, 36]\\
    qiskit_functions_qft = QiskitFunctionInterface(QFT, num_qubits)\\
    qiskit_functions_qv = QiskitFunctionInterface(QuantumVolume, num_qubits)
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
                f"{self.function_type.__name__.lower()}_{n}": self._create_function(n)
                for n in self.num_qubits
            }

        def _create_function(self, num_qubits: int) -> Callable:
            """Create a quantum function with the specified number of
            qubits."""
            func = self.function_type(num_qubits)
            func.name = f"{self.function_type.__name__.lower()}_{num_qubits}"
            return func

    def __init__(self, function_type: Type[Callable], num_qubits: List[int]) -> None:
        self.function_factory = self.QuantumFunctionFactory(function_type, num_qubits)
        super().__init__()

    def _get_qiskit_functions(self) -> List[Callable]:
        """Returns a list of Qiskit functions generated by the
        QuantumFunctionFactory."""
        return list(self.function_factory.generate_functions().values())


class MQTBench(SubmoduleInterface):
    def __init__(self, num_qubits: int, filter_str: Optional[str] = None) -> None:
        super().__init__(filter_str)
        self.num_qubits = num_qubits
        self.supported_benchmarks = get_supported_benchmarks()

    def _get_raw_quantum_circuits(self) -> Iterator[QuantumCircuit]:
        """Return an iterator over QuantumCircuits."""
        for bench_str in self.supported_benchmarks:
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

    def estimate_circuit_count(self) -> int:
        """Return an estimate of the total number of QuantumCircuits."""
        return len(self.supported_benchmarks)
