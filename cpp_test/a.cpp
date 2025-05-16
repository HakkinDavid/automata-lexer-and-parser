#include <iostream>
#include<string>

int main (void) {
    int a_ = 1;
    int b_ = 2;
    int c_ = 3;

    std::string abc = "abc";
    char e_ = 'e';

    float o_ = 4.0;

    long int r_ = 3333333;

    double dd = 3.00003;

    for (int i_ = 0; i_ < abc.length(); i_++) {
        std::cout << abc[i_] << std::endl;
    }
}