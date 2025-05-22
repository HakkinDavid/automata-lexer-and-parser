#include <iostream>
using namespace std;

template <typename TT> TT myMax(TT xx, TT yy) {
    return (xx > yy) ? xx : yy;
}


struct Prueba
{
   
    int ll;
    string mm = "Hello";
    char nn;    
    float oo;
    double pp;
};

class Test
{
private:
   
    int ee;
    int ff;
    int gg;
public:
    Test();
    ~Test();
};


void testFunction(int aa,int bb) {
    cout << "This is a test function: " << endl << aa << " + " << bb << endl;
}

int main(){
    int aa = 5;
    int bb = 10;
}

