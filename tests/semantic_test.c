int factorial(int n) {
    int unused_var = 10;
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int x = 5;
    int y = "invalid_string_type"; // Error: Type mismatch
    int res = factorial(x, 20);    # Error: Wrong argument count
    undefined_func();              // Error: Undefined function
    return 0;
}