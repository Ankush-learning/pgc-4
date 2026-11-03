# Cache Coherence Protocols & NUMA Memory Performance Analysis

### An Experimental Study of MSI, MESI, MOESI, False Sharing and Non-Uniform Memory Access

![C](https://img.shields.io/badge/C-00599C?style=flat&logo=c&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenMP](https://img.shields.io/badge/OpenMP-Multithreading-blue)
![Linux](https://img.shields.io/badge/Environment-Ubuntu%20WSL2-orange)
![Architecture](https://img.shields.io/badge/Domain-Computer%20Architecture-purple)

---

## 1. Project Overview

Modern multiprocessor systems rely on multiple CPU cores, private caches and shared memory to achieve high computational performance. However, maintaining data consistency between these caches introduces challenges that can significantly affect system performance.

This project explores three important concepts in computer architecture:

1. **Cache Coherence Protocols:** Implementation and simulation of MSI, MESI and MOESI protocols to understand how processors maintain consistent cache data.
2. **False Sharing:** Investigation of cache-line contention when multiple processor cores modify independent variables located within the same cache line.
3. **NUMA Memory Architecture:** Analysis of memory access performance under different thread configurations and memory placement policies.

The experiments combine Python-based cache-coherence simulation with C programming, OpenMP multithreading and Linux NUMA utilities.

The objective is not only to understand these architectural concepts theoretically, but also to observe their effects through measurable performance experiments.

---

## 2. Objectives

- Understand cache coherence in multiprocessor systems.
- Simulate cache state transitions using MSI, MESI and MOESI protocols.
- Compare bus transactions and invalidation events across coherence protocols.
- Investigate the performance implications of false sharing.
- Compare adjacent and cache-line-padded memory layouts.
- Evaluate execution time across different OpenMP thread configurations.
- Explore NUMA topology and memory placement using Linux utilities.
- Analyse experimental results through graphs, tables and performance measurements.

---

## 3. Technologies & Tools

| Technology | Purpose |
|---|---|
| C | Performance benchmarking and memory experiments |
| Python 3 | Cache coherence protocol simulation |
| GCC | Compilation of C programs |
| OpenMP | Parallel execution using multiple CPU threads |
| numactl | NUMA topology and memory placement |
| hwloc | Hardware topology inspection |
| Ubuntu on WSL 2 | Experimental environment |

---

## 4. System Architecture

The experiment consists of four independent programs, each addressing a different aspect of multiprocessor performance.

```text
                 EXPERIMENT 4
                       |
          +------------+------------+
          |            |            |
     CACHE COHERENCE  FALSE       NUMA
      SIMULATION     SHARING    PERFORMANCE
          |            |            |
      Python 3       C + OpenMP   C + OpenMP
          |            |            |
      +---+---+        |         Memory Sweep
      |   |   |        |            |
     MSI MESI MOESI  Adjacent    Thread Scaling
                       vs            |
                     Padded       numactl
                       |
                 Performance
                  Comparison
```

### Program Structure

| Program | Language | Description |
|---|---|---|
| `coherence_sim.py` | Python | Simulates MSI, MESI and MOESI cache-coherence behaviour |
| `false_sharing.c` | C | Measures adjacent versus padded counter performance |
| `numa_sweep.c` | C | Measures memory-sweep execution time |
| `compare_numa.c` | C | Combines false-sharing and memory-sweep benchmarks |

---

# 5. Cache Coherence Protocols

## 5.1 Why Cache Coherence?

In multiprocessor systems, each CPU core may maintain a private cache containing copies of data from main memory.

When one processor modifies a cache block, other processors may still possess outdated copies of that block.

Cache coherence protocols coordinate these copies to ensure that processors observe consistent data.

This project investigates three widely studied protocols.

### MSI Protocol

MSI uses three cache states:

| State | Description |
|---|---|
| Modified (M) | Cache block has been modified and differs from main memory |
| Shared (S) | Multiple caches may contain a clean copy |
| Invalid (I) | Cache block is invalid or unavailable |

### MESI Protocol

MESI extends MSI by introducing the Exclusive state.

| State | Description |
|---|---|
| Modified (M) | Dirty, exclusive cache block |
| Exclusive (E) | Clean cache block held exclusively |
| Shared (S) | Clean block potentially shared by multiple caches |
| Invalid (I) | Invalid cache block |

The Exclusive state allows a processor to transition from E to M without generating an additional bus transaction.

### MOESI Protocol

MOESI extends MESI by introducing the Owned state.

| State | Description |
|---|---|
| Modified (M) | Dirty, exclusive cache block |
| Owned (O) | Dirty block that may be shared, with one cache responsible for supplying the data |
| Exclusive (E) | Clean, exclusively held block |
| Shared (S) | Clean, shared cache block |
| Invalid (I) | Invalid cache block |

The Owned state allows modified data to be shared without requiring an immediate writeback to main memory.

### Simulation Results

The Python simulator models two processor caches and compares adjacent and padded counter layouts over 1,000 iterations.

| Memory Layout | MSI | MESI | MOESI |
|---|---:|---:|---:|
| Adjacent | 4000 | 3999 | 3999 |
| Padded | 4 | 2 | 2 |

*Values represent simulated bus transactions.*

### Analysis

- MSI requires additional bus upgrade operations.
- MESI reduces transactions through its Exclusive state.
- MOESI introduces the Owned state to model dirty cache-line sharing.
- Separating cache lines significantly reduces simulated coherence traffic.

**Note:** This is an educational event-based simulation, not a cycle-accurate processor or hardware cache simulator.

---

# 6. False Sharing Analysis

## 6.1 What is False Sharing?

False sharing occurs when two or more processor cores modify different variables that reside within the same cache line.

Although the variables are logically independent, cache-coherence protocols operate on entire cache lines rather than individual variables.

Consequently, a write by one processor can invalidate another processor's cache-line copy, even when the processors are modifying different variables.

This can result in unnecessary cache-coherence traffic and reduced performance.

## 6.2 Experimental Approach

Two memory layouts were implemented.

**Adjacent Counters**

Multiple counters are stored next to each other in memory. They may occupy the same cache line.

**Padded Counters**

Each counter is separated using padding and aligned to a 64-byte boundary, preventing the counters from sharing a cache line in this experiment.

Both configurations perform the same total number of increments.

The experiment uses OpenMP to execute the workload with different thread counts.

### Benchmark Configuration

- Total increments: 100,000,000
- Thread configurations: 1, 2 and 4
- Compiler: GCC
- Optimization: `-O2`
- Parallelization: OpenMP
- Comparison metric: Execution time in seconds

## 6.3 Experimental Results

### Standalone Benchmark

| Threads | Adjacent (s) | Padded (s) |
|---:|---:|---:|
| 1 | 0.0422 | 0.0438 |
| 2 | 0.0280 | 0.0234 |
| 4 | 0.0209 | 0.0095 |

### Performance Visualization

![False Sharing Benchmark](charts/false_sharing_standalone.png)

### Performance Analysis

The results demonstrate the performance difference between adjacent and padded memory layouts.

At four threads:

- Adjacent execution time: 0.0209 seconds.
- Padded execution time: 0.0095 seconds.
- Padded execution was approximately 2.20 times faster in this recorded run.

The improvement is associated with reduced cache-line contention.

At one thread, both configurations have similar execution times because there is no inter-thread cache-line contention.

**Key Finding:** Memory layout can significantly influence multithreaded application performance, even when the actual computation remains unchanged.

---

# 7. NUMA Memory Performance

## 7.1 Understanding NUMA

NUMA stands for Non-Uniform Memory Access.

It is a multiprocessor memory architecture in which processors have access to their own local memory and memory associated with other processors.

Memory access latency depends on the location of the requested memory.

| Memory Type | Description |
|---|---|
| Local Memory | Memory associated with the processor's NUMA node |
| Remote Memory | Memory associated with another NUMA node |

Local memory access is generally faster than remote memory access.

## 7.2 Experimental Approach

The NUMA experiment uses:

- C programming
- OpenMP parallel processing
- A 512 MB memory buffer
- Four sequential memory-sweep passes
- Different thread configurations
- Linux `numactl` for CPU and memory-node binding

The experiment measures execution time under default memory placement and explicit NUMA node 0 binding.

### NUMA Memory Sweep Results

| Threads | Default Placement (s) | Node 0 Bound (s) |
|---:|---:|---:|
| 1 | 0.2189 | 0.2424 |
| 2 | 0.2238 | 0.2044 |

### Performance Visualization

![NUMA Memory Sweep](charts/numa_memory_sweep.png)

### Hardware Topology

The experimental environment exposed the following hardware configuration:

| Component | Configuration |
|---|---|
| Processor | Intel Core i5-13420H |
| Available CPU threads | 12 |
| CPU cores per socket | 6 |
| CPU sockets | 1 |
| NUMA nodes exposed | 1 |
| Available NUMA node | Node 0 |

### NUMA Limitation

The experiment was conducted using Ubuntu on WSL 2.

The environment exposed only one NUMA node:

```text
available: 1 nodes (0)

node 0 cpus:
0 1 2 3 4 5 6 7 8 9 10 11
```

Attempts to bind memory to node 1 resulted in an error because the node was unavailable.

Therefore, the experiment successfully demonstrated NUMA topology inspection and local node binding, but a genuine local-versus-remote NUMA latency comparison could not be performed.

This limitation is documented rather than presenting fabricated remote-memory measurements.

---

# 8. Combined Performance Comparison

The final program, `compare_numa.c`, combines the false-sharing benchmark and NUMA memory sweep into a single execution.

It evaluates adjacent and padded counters using:

- 1 thread
- 2 threads
- 4 threads

It also measures memory-sweep performance with 1 and 2 threads.

### Combined Benchmark – Node 0 Binding

| Threads | Adjacent (s) | Padded (s) |
|---:|---:|---:|
| 1 | 0.0402 | 0.0343 |
| 2 | 0.0180 | 0.0153 |
| 4 | 0.0110 | 0.0117 |

![Combined Benchmark](charts/false_sharing_combined_runs.png)

### Interpretation

The combined benchmark demonstrates that performance is affected by thread scheduling, memory layout and system conditions.

Although padded counters generally performed better in the recorded standalone experiment, the four-thread node-bound run showed a slightly different result.

This highlights an important principle in performance engineering: benchmark results should be interpreted using repeated measurements rather than assuming that one execution represents universal hardware behaviour.

---

# 9. Repository Structure

```text
pgc-4/
│
├── src/
│   ├── coherence_sim.py
│   ├── false_sharing.c
│   ├── numa_sweep.c
│   └── compare_numa.c
│
├── results/
│   ├── false_sharing_standalone.csv
│   ├── compare_default.csv
│   ├── compare_node0.csv
│   └── numa_sweep.csv
│
├── charts/
│   ├── false_sharing_standalone.png
│   ├── false_sharing_combined_runs.png
│   └── numa_memory_sweep.png
│
├── screenshots/
│   ├── 01-system-topology.png
│   ├── 02-protocol-simulator.png
│   ├── 03-false-sharing.png
│   ├── 04-numa-results.png
│   └── 05-combined-results.png
│
├── docs/
│   └── observations.md
│
└── README.md
```

---

# 10. Installation and Execution

## Prerequisites

Install the required dependencies on Ubuntu or Ubuntu WSL 2.

```bash
sudo apt update

sudo apt install build-essential numactl hwloc python3 -y
```

Verify the compiler and OpenMP installation:

```bash
gcc --version

python3 --version

echo '#include <omp.h>' | gcc -E -fopenmp -xc - > /dev/null && echo "OpenMP OK"
```

## Running the Experiments

### A. Cache Coherence Simulation

```bash
python3 src/coherence_sim.py 1000
```

### B. False Sharing Benchmark

Compile:

```bash
gcc -O2 src/false_sharing.c -fopenmp -o false_sharing
```

Execute:

```bash
OMP_NUM_THREADS=2 ./false_sharing adjacent

OMP_NUM_THREADS=2 ./false_sharing padded
```

### C. NUMA Memory Sweep

Compile:

```bash
gcc -O2 src/numa_sweep.c -fopenmp -o numa_sweep
```

Execute:

```bash
OMP_NUM_THREADS=1 ./numa_sweep

OMP_NUM_THREADS=2 ./numa_sweep
```

### D. Combined Comparison

Compile:

```bash
gcc -O2 src/compare_numa.c -fopenmp -o compare_numa
```

Execute:

```bash
./compare_numa
```

Test NUMA node binding:

```bash
numactl --cpunodebind=0 --membind=0 ./compare_numa
```

---

# 11. Key Findings

The experiments provide several insights into multiprocessor performance.

1. **Cache coherence is essential:** MSI, MESI and MOESI maintain consistency between processor caches using different state-transition mechanisms.

2. **Exclusive ownership matters:** MESI reduces unnecessary bus communication when a processor has exclusive access to a clean cache block.

3. **Memory layout affects performance:** False sharing can significantly reduce the performance of multithreaded programs.

4. **Padding can improve scalability:** Separating frequently modified variables into different cache lines reduces unnecessary invalidations.

5. **NUMA placement matters:** Memory locality is an important consideration in large multiprocessor systems.

6. **Benchmarking requires careful interpretation:** Execution times vary with thread scheduling, system load, virtualization and hardware configuration.

---

# 12. Limitations and Future Improvements

Although the experiments successfully demonstrate the core concepts, several improvements are possible.

### Current Limitations

- The cache coherence simulator is a simplified two-core model.
- The benchmark timings represent individual recorded runs.
- WSL 2 exposed only one NUMA node.
- Remote NUMA memory latency could not be measured.
- Performance measurements may vary across hardware configurations.

### Future Improvements

- Extend the cache-coherence simulator to support more processor cores.
- Visualize cache-state transitions dynamically.
- Implement repeated benchmarks and statistical analysis using averages and medians.
- Perform remote NUMA memory experiments on a multi-node system.
- Investigate cache-line sizes and hardware performance counters.
- Compare additional cache-coherence protocols and memory-placement strategies.

---

# 13. Conclusion

This project demonstrates the relationship between cache coherence, memory organization and parallel execution performance in modern multiprocessor systems.

Through the implementation of MSI, MESI and MOESI simulations, the experiment illustrates how cache-coherence protocols coordinate shared data across processor caches.

The false-sharing benchmark demonstrates that the physical arrangement of independent variables can influence multithreaded execution time, with padded counters generally reducing cache-line contention.

The NUMA experiments provide practical exposure to hardware topology inspection, memory placement policies and parallel memory access. Although the WSL environment restricted testing to a single NUMA node, the limitation helped establish the importance of hardware topology when conducting architecture-level performance experiments.

Overall, the experiment highlights that achieving high performance in multiprocessor systems requires more than parallel execution: cache coherence, memory layout, data locality and hardware architecture all play important roles.

---

## Author

**Ankush**

Computer Science and Artificial Intelligence

KLE Technological University, Hubballi

---

*This repository documents an academic computer architecture experiment involving cache coherence simulation, multithreaded performance benchmarking and NUMA memory analysis.*
