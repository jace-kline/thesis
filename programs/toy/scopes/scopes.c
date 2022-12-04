
#include <stdio.h>

int main() {
    {
        int arr1[10];
        printf("In scope 1. Ghidra detects this array at the top-level.\n");
        for(int i = 0; i < 10; i++) {
            arr1[i] = i;
        }
    }

    {
        int arr2[20];
        printf("In scope 2. Ghidra misses this array.\n");
        for(int i = 0; i < 20; i++) {
            arr2[i] = i;
        }

    }

    return 0;
}
