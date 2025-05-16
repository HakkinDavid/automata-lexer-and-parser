#include <iostream>
#include <string>

using namespace std;

int main() {
    int x_ = 10;
    int y_;
    string mensaje = "Hola";

    cout << "Introduce_un_número:_";
    cin >> y_;

    if (y_ > x_) {
        cout << "y_es_mayor_que_x" << endl;
    } else if (y_ == x_) {
        cout << "y_es_igual_a_x" << endl;
    } else {
        cout << "y_es_menor_que_x" << endl;
    }

    while (x_ > 0) {
        cout << x_ << endl;
        x_--;
    }

    saludar(mensaje);

    return 0;
}

void saludar(string texto) {
    cout << "Saludo:_" << texto << endl;
}