#include <stdio.h>

typedef struct {
    int day;
    int month;
    int year;
} Date;

typedef struct {
    char* name;
    int ssn;
    float height;
    float weight;
    Date dob;
} Person;

Person people[2];

int main() {
    int x = 999999999;
    printf("%ld %ld %ld\n", sizeof(people), sizeof(Person), sizeof(float));
    return 0;
}