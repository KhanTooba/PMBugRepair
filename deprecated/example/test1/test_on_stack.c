#include <string.h>

#include "cc_stack.h"
//#include "CppUTest/TestHarness_c.h"

static Stack *s;
static Stack *s2;

int main(int argc, char **argv) {
    stack_new(&s);

    int a = 1;
    int b = 2;
    int c = 3;

    int *p;

    stack_push(s, (void *)&a);
    stack_peek(s, (void *)&p);
    //CHECK_EQUAL_C_POINTER(&a, p);

    stack_push(s, (void *)&b);
    stack_peek(s, (void *)&p);
    //CHECK_EQUAL_C_POINTER(&b, p);

    stack_push(s, (void *)&c);
    stack_peek(s, (void *)&p);
    //CHECK_EQUAL_C_POINTER(&c, p);

    stack_destroy(s);
}
