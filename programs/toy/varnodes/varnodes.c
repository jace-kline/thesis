
#include <stdio.h>

int main() {
    int a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p = 0;

    printf("Enter an integer: ");
    scanf("%d", &a);
    b = a + 1;
    c = a + 2;
    d = a + 3;
    e = a + 4;

    f = b + 1;
    g = b + 2;
    h = b + 3;
    i = b + 4;

    j = c + 1;
    k = c + 2;
    l = c + 3;
    m = c + 4;

    b = l + m;
    b = b * 2;
    printf("a = %d", b);
    return 0;
}