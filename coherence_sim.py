#!/usr/bin/env python3
"""Small educational two-core MSI/MESI/MOESI cache-coherence simulator."""
import sys

def make_cores(n=2):
    return [dict() for _ in range(n)]

def access(proto, caches, core, line, op, st):
    me = caches[core]
    state = me.get(line, "I")
    others = [i for i in range(len(caches)) if i != core]
    holders = [i for i in others if caches[i].get(line, "I") != "I"]

    if op == "R":
        if state != "I":
            return
        st["BusRd"] += 1
        new = "S"
        for i in holders:
            other = caches[i][line]
            if other == "M":
                if proto == "MOESI":
                    caches[i][line] = "O"
                    st["C2C"] += 1
                else:
                    caches[i][line] = "S"
                    st["WB"] += 1
            elif other == "O":
                st["C2C"] += 1
            elif other == "E":
                caches[i][line] = "S"
        if not holders and proto in ("MESI", "MOESI"):
            new = "E"
        me[line] = new
    else:
        if state == "M":
            return
        if state == "E":
            me[line] = "M"
            st["Silent E-M"] += 1
            return
        if state in ("S", "O"):
            st["BusUpgr"] += 1
        else:
            st["BusRdX"] += 1
        for i in holders:
            other = caches[i][line]
            if other in ("M", "O"):
                if proto == "MOESI":
                    st["C2C"] += 1
                else:
                    st["WB"] += 1
            caches[i][line] = "I"
            st["Invalidations"] += 1
        me[line] = "M"

def run(proto, layout, iterations):
    keys = ["BusRd", "BusRdX", "BusUpgr", "Invalidations",
            "WB", "C2C", "Silent E-M"]
    stats = dict.fromkeys(keys, 0)
    caches = make_cores()
    lx, ly = ("A", "A") if layout == "adjacent" else ("A", "B")
    for _ in range(iterations):
        for core, line, op in [(0, lx, "R"), (0, lx, "W"),
                               (1, ly, "R"), (1, ly, "W")]:
            access(proto, caches, core, line, op, stats)
    stats["Bus transactions"] = (
        stats["BusRd"] + stats["BusRdX"] + stats["BusUpgr"])
    return stats

if __name__ == "__main__":
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    print("CACHE COHERENCE SIMULATION")
    print("Iterations:", iterations)
    for layout in ("adjacent", "padded"):
        print(f"\n{layout.upper()} COUNTERS")
        for proto in ("MSI", "MESI", "MOESI"):
            stats = run(proto, layout, iterations)
            print(f"\n{proto}:")
            for key, value in stats.items():
                print(f"{key:20}: {value}")
