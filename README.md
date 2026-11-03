Cache Coherence & NUMA Performance Lab
A hands-on systems experiment exploring MSI, MESI and MOESI cache-coherence protocols, false sharing, and NUMA memory placement using Python, C, GCC and OpenMP.
> **Environment note:** The measurements in this repository were collected in Ubuntu on WSL 2 running on an Intel Core i5-13420H. WSL exposed **one NUMA node (node 0)**, so local placement was tested but a genuine remote-node benchmark was not possible.
Contents
```text
cache-coherence-numa-lab/
├── README.md
├── src/
│   ├── coherence_sim.py
│   ├── false_sharing.c
│   ├── numa_sweep.c
│   └── compare_numa.c
├── results/
│   ├── false_sharing_standalone.csv
│   ├── compare_default.csv
│   ├── compare_node0.csv
│   └── numa_sweep.csv
├── charts/
│   ├── false_sharing_standalone.png
│   ├── false_sharing_combined_runs.png
│   └── numa_memory_sweep.png
├── screenshots/
│   └── README.md
└── docs/
    └── observations.md
```
Objectives
Simulate cache-line state changes under MSI, MESI and MOESI.
Compare adjacent counters (susceptible to false sharing) with cache-line-padded counters.
Measure a memory sweep under different OpenMP thread counts.
Inspect NUMA topology and test node binding where the environment permits it.
Concepts
MSI: Modified, Shared, Invalid.
MESI: Adds Exclusive, allowing a clean private cache line to transition from E to M without a bus transaction.
MOESI: Adds Owned, allowing a dirty line to be shared while an owner supplies data.
False sharing: Independent variables occupy the same cache line; writes by different cores can invalidate each other's cache-line copies.
NUMA: Memory access latency can differ depending on whether memory is local to the executing CPU or attached to another NUMA node.
Requirements
Ubuntu 22.04+ (native Linux or WSL 2)
GCC with OpenMP support
Python 3
`numactl` (for topology and node binding)
Install on Ubuntu:
```bash
sudo apt update
sudo apt install build-essential numactl hwloc python3 -y
```
Verify:
```bash
gcc --version
python3 --version
echo '#include <omp.h>' | gcc -E -fopenmp -xc - > /dev/null && echo "OpenMP OK"
numactl --hardware
lscpu | grep -E "Socket|Core|Thread|NUMA"
```
Run the experiments
From the repository root:
1. MSI / MESI / MOESI simulator
```bash
python3 src/coherence_sim.py 1000
```
The simulator prints bus transaction and coherence-event counters for adjacent and padded layouts. It is a teaching model, not a cycle-accurate CPU/cache simulator.
2. False-sharing benchmark
Compile:
```bash
gcc -O2 src/false_sharing.c -fopenmp -o false_sharing
```
Run two threads:
```bash
OMP_NUM_THREADS=2 ./false_sharing adjacent
OMP_NUM_THREADS=2 ./false_sharing padded
```
Run a small scalability sweep:
```bash
OMP_NUM_THREADS=1 ./false_sharing adjacent
OMP_NUM_THREADS=1 ./false_sharing padded
OMP_NUM_THREADS=4 ./false_sharing adjacent
OMP_NUM_THREADS=4 ./false_sharing padded
```
The expected final count is `100000000` in every run. Compare execution time, not correctness, to study the performance effect.
3. NUMA memory sweep
Compile and run:
```bash
gcc -O2 src/numa_sweep.c -fopenmp -o numa_sweep
OMP_NUM_THREADS=1 ./numa_sweep
OMP_NUM_THREADS=2 ./numa_sweep
```
The default buffer size is 512 MB. An alternate size can be supplied in MB, for example:
```bash
OMP_NUM_THREADS=2 ./numa_sweep 256
```
4. Combined comparison program
Compile and run:
```bash
gcc -O2 src/compare_numa.c -fopenmp -o compare_numa
./compare_numa
```
Try node 0 binding if node 0 exists:
```bash
numactl --cpunodebind=0 --membind=0 ./compare_numa
```
Only attempt a remote-node run if `numactl --hardware` lists another node, for example node 1:
```bash
numactl --cpunodebind=0 --membind=1 ./compare_numa
```
Results collected
False sharing — standalone benchmark
Threads	Adjacent (s)	Padded (s)
1	0.0422	0.0438
2	0.0280	0.0234
4	0.0209	0.0095
The 4-thread padded run was about 2.20× faster than adjacent in this particular run (`0.0209 / 0.0095`). Timings are machine- and load-dependent.
Combined program — default placement
Threads	Adjacent (s)	Padded (s)
1	Not visible in captured output	0.0333
2	0.0267	0.0174
4	0.0188	0.0121
The adjacent 1-thread value was not visible in the supplied screenshot, so it is intentionally not inferred or filled in.
Combined program — node 0 CPU and memory binding
Threads	Adjacent (s)	Padded (s)
1	0.0402	0.0343
2	0.0180	0.0153
4	0.0110	0.0117
This second run shows that timing noise and scheduling can affect small differences; padded layout is not guaranteed to win in every individual measurement.
NUMA memory sweep (512 MB, four passes)
Threads	Default (s)	Node 0 bound (s)
1	0.2189	0.2424
2	0.2238	0.2044
These values compare default placement with explicit node-0 binding. They are not a local-versus-remote comparison.
Important NUMA limitation
The tested WSL environment reported:
```text
available: 1 nodes (0)
node 0 cpus: 0 1 2 3 4 5 6 7 8 9 10 11
```
Therefore, `numactl --membind=1` correctly failed because node 1 did not exist. This setup cannot demonstrate remote NUMA memory latency. A multi-socket machine or a VM configuration that genuinely exposes multiple NUMA nodes is needed for that comparison. Merely seeing virtual nodes does not guarantee physically distinct memory domains.
Observations
The protocol simulator demonstrates that coherence actions operate at cache-line granularity.
The adjacent-counter workload can cause cache-line ping-pong between threads.
Padding separates the counters onto different cache lines and often improves multi-thread performance.
MESI's Exclusive state avoids a bus upgrade when a private clean line is first written.
MOESI's Owned state models dirty sharing without an immediate memory writeback.
NUMA node binding can be tested, but remote-node performance requires at least two available NUMA nodes.
See `docs/observations.md` for a concise lab-record summary.
Screenshots
Add your own terminal screenshots to `screenshots/` before publishing. Suggested captures:
`01-system-topology.png` — `lscpu` and `numactl --hardware`.
`02-protocol-simulator.png` — `python3 src/coherence_sim.py 1000`.
`03-false-sharing.png` — adjacent vs padded timing output.
`04-numa-sweep.png` — memory sweep output.
`05-combined-results.png` — final comparison program.
Do not upload screenshots containing personal paths, usernames, tokens, or unrelated desktop content.
Reproducibility notes
Run benchmarks more than once and report medians for a stronger comparison.
Close CPU-heavy applications while benchmarking.
Keep compiler flags and thread counts consistent between layouts.
Treat the included timings as one recorded run, not universal performance guarantees.
The charts are generated from the recorded measurements included in `results/`.
