#include <iostream>
using namespace std;

int main(){
    int aa = 5;
    int bb = 10;
    int sum = aa + bb;
    cout << "The sum of " << aa << " and " << bb << " is: " << sum << endl;
    cout << "Hello, World!" << endl;
    testFunction(aa,bb);
    return 0;
}

void testFunction(int aa,int bb) {
    cout << "This is a test function: " << endl << aa << " + " << bb << endl;
}