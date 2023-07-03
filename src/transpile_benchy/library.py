"""Build a library of circuits aggregated from all the interfaces."""

from typing import List, Optional

from transpile_benchy.interfaces.qasm_interface import QASMBench, RedQueen


class Library:
    """A class to handle the library of circuits."""

    def __init__(self, size: str, filter_list: Optional[List[str]] = None):
        """Initialize the library."""
        self.interfaces = []
        self.interfaces.append(QASMBench(size, filter_list))
        self.interfaces.append(RedQueen(filter_list))

    def __str__(self):
        """Build string as all the available circuit names."""
        return str([str(intf) for intf in self.interfaces])

    def __iter__(self):
        """Iterate over all the circuits."""
        for interface in self.interfaces:
            for circuit in interface:
                yield circuit

    def __len__(self):
        """Return the number of circuits."""
        return sum(len(interface) for interface in self.interfaces)
