int process_data(int a, float b) {
    return "This is a string, not an int!";
}

void test_type_system() {
    int invalid_assign = "Hello World";

    int boolean_to_int = true;

    float valid_assign = 10;

    process_data(5);

    process_data("Not a number", 3.14);
}