#include <stdlib.h>
#include <stdio.h>

struct node_t {
    int val;
    struct node_t *prev;
};

struct node_t *make_fib_list(unsigned int n) {
    struct node_t *node = (struct node_t *) malloc(sizeof(struct node_t));
    if(n == 0) {
        node->val = 0;
        node->prev = NULL;
    }
    else {
        struct node_t *prev = make_fib_list(n - 1);
        node->prev = prev;
        node->val = (n == 1) ? 1 : node->prev->val + node->prev->prev->val;
    }
    return node;
}

void free_fib_list(struct node_t *node) {
    if(node != NULL) {
        free_fib_list(node->prev);
        free(node);
    }
}

int main() {
    unsigned int i = 5;
    struct node_t *end_list = make_fib_list(i);
    struct node_t *iter = end_list;

    while(iter != NULL) {
        printf("fib(%d) = %d\n", i, iter->val);
        iter = iter->prev;
        i--;
    }

    free_fib_list(end_list);
    return 0;
}