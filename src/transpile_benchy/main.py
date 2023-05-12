"""Main benchmark runner."""
import glob
import os


class Benchmark:
    """Benchmark runner."""

    def __init__(self):
        """Initialize benchmark runner."""
        pass

    def run(self):
        """Run benchmark."""
        print(os.getcwd())
        filenames = glob.iglob("../../QASMBench/small/**/*.qasm", recursive=True)
        # # Filter out files containing '_transpiled' in their names
        filtered_filenames = (
            filename for filename in filenames if "_transpiled" not in filename
        )

        for filename in filtered_filenames:
            print(filename)


if __name__ == "__main__":
    Benchmark().run()
