#include <iostream>
#include <vector>

#include "generator.h"

using namespace std;

int main() {
    int m = 5;
    int max_value = 25;
    cout << "Generated P: ";
    vector<int> p = generate_p(m, max_value);
    for (int i : p) {
        cout << i << " ";
    }
    cout << "\n";

    cout << "Generated D: ";
    vector<int> d = generate_d_from_p(p, 0);
    for (int i : d) {
        cout << i << " ";
    }
    cout << "\n";
    return 0;
}