"""Build a library of circuits aggregated from all the interfaces."""

from typing import List, Optional

from transpile_benchy.interfaces.qasm_interface import QASMBench, RedQueen


class Library:
    """A class to handle the library of circuits."""

    # FIXME ???

    def __init__(self, size: str, filter_list: Optional[List[str]] = None):
        """Initialize the library."""
        self.interfaces = []
        self.interfaces.append(QASMBench(size, filter_list))
        self.interfaces.append(RedQueen(filter_list))
        # self.interfaces.append(MQTBench(num_qubits=8))
        # self.interfaces.append(Queko(filter_list))
