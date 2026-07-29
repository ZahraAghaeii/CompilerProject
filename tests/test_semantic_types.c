// تابعی که یک عدد صحیح و یک اعشاری می‌گیرد
int process_data(int a, float b) {
    // نقطه کور 1: تلاش برای برگرداندن یک رشته در تابعی که خروجی‌اش int است
    return "This is a string, not an int!";
}

void test_type_system() {
    // نقطه کور 2: متغیر از نوع int است، اما رشته به آن داده شده
    int invalid_assign = "Hello World";

    // نقطه کور 3: مقداردهی bool به int (باید خطا بدهد چون توابع ریاضی و منطقی در تایپ‌چکر ما جدا هستند)
    int boolean_to_int = true;

    // کاملا درست (تطابق int و float مجاز است)
    float valid_assign = 10;

    // نقطه کور 4: فراخوانی تابع با تعداد آرگومان اشتباه
    process_data(5);

    // نقطه کور 5: فراخوانی تابع با تعداد درست، اما نوع اشتباه (رشته به جای عدد)
    process_data("Not a number", 3.14);
}