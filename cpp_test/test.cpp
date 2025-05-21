#include <iostream>
using namespace std;

template <typename T> T myMax(T x, T y) {
    return (x > y) ? x : y;
}

class Test
{
private:
    /* data */
    int ee;
    int ff;
    int gg;
public:
    Test(/* args */);
    ~Test();
};

struct Prueba
{
    /* data */
    int ll;
    string mm = "Hello";
    char nn;    
    float oo;
    double pp;
};




int main(){
    int aa = 5;
    int bb = 10;
    int sum = aa + bb;
    testFunction(aa,bb);

    Prueba prueba;

    cout << prueba.mm << endl;
    return 0;
}

void testFunction(int aa,int bb) {
    cout << "This is a test function: " << endl << aa << " + " << bb << endl;
}