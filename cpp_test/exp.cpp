#include <iostream>
#include <string>

using namespace std;

void saludar(string texto) {
    cout << "Saludo: " << texto << endl;
}

int main() {
    int x_ = 10;
    int y_;
    string mensaje = "Hola, amigo.";

    cout << "Introduce un número: ";
    cin >> y_;

    if (y_ > x_) {
        cout << "y es mayor que x" << endl;
    } else if (y_ == x_) {
        cout << "y es igual a x" << endl;
    } else {
        cout << "y es menor que x" << endl;
    }

    while (x_ > 0) {
        cout << x_ << endl;
        x_--;
    }

    saludar(mensaje);

    return 0;
}
