# Observations and interpretation

## Cache coherence simulation
The simulator models two cores and two counter layouts. The adjacent layout maps both counters to one simulated cache line; the padded layout maps them to separate lines. The model is educational and does not emulate real hardware timing.

## False sharing
The standalone benchmark measured:
- 1 thread: adjacent 0.0422 s, padded 0.0438 s
- 2 threads: adjacent 0.0280 s, padded 0.0234 s
- 4 threads: adjacent 0.0209 s, padded 0.0095 s

At four threads, padded was approximately 2.20 times faster in this recorded run. One-thread performance was similar, as expected because there is no inter-thread cache-line ping-pong.

## NUMA
WSL reported one NUMA node. Node 0 binding was possible; node 1 binding failed because node 1 was absent. The memory sweep results are therefore default-placement versus node-0-bound results, not local versus remote NUMA results.

## Limitations
- Timings are individual runs and can vary with system load, scheduling, thermal state and virtualization.
- The simulator is a simplified state/event model, not a cycle-accurate hardware model.
- Genuine remote NUMA testing requires at least two accessible NUMA nodes.
