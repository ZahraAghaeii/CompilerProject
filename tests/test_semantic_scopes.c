int global_var = 100;

int complex_func(int param, int param) {
    int global_var = 200;

    int param = 5;

    int uninit_var;

    {
        int global_var = 300;

        int block_var = 50;

        int z = uninit_var;
    }

    block_var = 10;

    return 0;
}