#include <stdio.h>

int compute_sum(int limit) {
    int sum = 0;
    int i = 0;

    while (i < limit) {
        if (i == 5) {
            i = i + 1;
            continue;
        }
        sum = sum + i;
        i = i + 1;
    }

    return sum;
}

int main() {
    int target = 10;
    int result = compute_sum(target);

    for (int j = 0; j < 3; j = j + 1) {
        if (j == 2) {
            break;
        }
    }

    return 0;
}