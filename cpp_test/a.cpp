#include <stdio>
#include <string>

int main (void) {
    int a = 1;
    int b = 2;
    int c = 3;

    string abc = "abc";

    float o = 4.0;

    long int r = 3333333;

    double dd = 3.00003;

    for (int i = 0; i < strlen(abc); i++) {
        std::cout << abc[i] << std::endl;
    }
}