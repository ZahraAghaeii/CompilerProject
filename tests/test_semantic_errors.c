int outer_var = 10;

// خطا: پارامترهای تکراری (param1)
int calculate(int param1, int param1) {
    // هشدار: سایه‌اندازی (Shadowing) روی متغیر outer_var
    int outer_var = 20;

    int x;
    // هشدار: استفاده از x قبل از مقداردهی
    int y = x;

    int z = 5;
    // خطا: تعریف مجدد متغیر z در همان دامنه
    int z = 10;

    // خطا: متغیر تعریف نشده
    missing_var = 100;

    return 0;
}

// خطا: تعریف مجدد یک تابع با همان نام
int calculate(int a) {
    return a;
}