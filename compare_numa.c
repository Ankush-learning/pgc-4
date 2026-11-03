#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define N 100000000L
#define MB 512UL

double run_counters(int nt, int stride, long *total) {
    size_t bytes = ((size_t)nt * stride * sizeof(long) + 63) / 64 * 64;
    long *cnt = aligned_alloc(64, bytes);
    if (!cnt) {
        perror("aligned_alloc");
        exit(1);
    }
    memset(cnt, 0, bytes);
    omp_set_num_threads(nt);
    double t0 = omp_get_wtime();
    #pragma omp parallel num_threads(nt)
    {
        volatile long *p = &cnt[omp_get_thread_num() * stride];
        for (long i = 0; i < N / nt; i++) (*p)++;
    }
    double t = omp_get_wtime() - t0;
    *total = 0;
    for (int i = 0; i < nt; i++) *total += cnt[i * stride];
    free(cnt);
    return t;
}

double run_sweep(char *buf, size_t n, int nt) {
    long sum = 0;
    omp_set_num_threads(nt);
    double t0 = omp_get_wtime();
    for (int pass = 0; pass < 4; pass++) {
        #pragma omp parallel for reduction(+:sum)
        for (size_t i = 0; i < n; i += 64) sum += buf[i];
    }
    if (sum == 0) fprintf(stderr, "Unexpected zero sum\n");
    return omp_get_wtime() - t0;
}

int main(void) {
    int tc[] = {1, 2, 4};
    printf("TABLE 1: FALSE SHARING\\n");
    printf("Layout | Threads | Final Count | Correctness | Time(s)\\n");
    for (int i = 0; i < 3; i++) {
        for (int stride = 1; stride <= 8; stride *= 8) {
            long total;
            double t = run_counters(tc[i], stride, &total);
            printf("%-8s | %7d | %11ld | %-11s | %8.4f\\n",
                   stride == 1 ? "adjacent" : "padded", tc[i], total,
                   total == N ? "Correct" : "INCORRECT", t);
        }
    }

    size_t n = MB << 20;
    char *buf = malloc(n);
    if (!buf) {
        perror("malloc");
        return 1;
    }
    memset(buf, 1, n);
    printf("\\nTABLE 2: NUMA MEMORY SWEEP\\n");
    printf("Buffer: %lu MB | Passes: 4\\n", MB);
    printf("Threads | Time(s)\\n");
    for (int i = 0; i < 2; i++)
        printf("%7d | %8.4f\\n", tc[i], run_sweep(buf, n, tc[i]));
    free(buf);
    return 0;
}
