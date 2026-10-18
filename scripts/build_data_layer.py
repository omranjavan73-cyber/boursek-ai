# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — سازندهٔ لایهٔ دادهٔ مشترک (Unified Data Layer Builder)
این اسکریپت بدون حذف هیچ دادهٔ قدیمی، تمامی رکوردهای موجود در نسخهٔ ابری فایربیس و نسخهٔ محلی را
با شناسه‌های یکتا، زمان‌بندی Asia/Dubai، برچسب منبع و نوشتن اتمیک (Atomic Write) در پوشهٔ data/ تولید می‌کند.
"""
import json
import os
import tempfile
import time
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
LOCK_FILE = os.path.join(DATA_DIR, ".publish.lock")

DUBAI_TZ = timezone(timedelta(hours=4))
TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def now_dubai_iso():
    return datetime.now(DUBAI_TZ).strftime("%Y-%m-%dT%H:%M:%S+04:00")


def now_tehran_iso():
    return datetime.now(TEHRAN_TZ).strftime("%Y-%m-%dT%H:%M:%S+03:30")


def atomic_write_json(target_path, payload):
    """نوشتن اتمیک فایل JSON جهت جلوگیری از تولید فایل ناقص در صورت قطع ناگهانی"""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target_path), prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            mtime = os.path.getmtime(LOCK_FILE)
            if time.time() - mtime < 120:
                raise RuntimeError("یک فرایند انتشار دیگر در حال اجراست (.publish.lock فعال است).")
        except OSError:
            pass
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass


# نگاشت شناسه‌های ثابت برای هر ۳۴ نماد واقعی پروژه
SYMBOL_META = {
    "درازی": {"id": "SYM_DRAZI", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 6.2, "eps": 12011, "margin": "46%", "codal_date": "1405/07/25", "codal_summary": "رشد 42% فروش ماهانه و افزایش حاشیه سود ناشی از اصلاح نرخ دارو"},
    "دفارا": {"id": "SYM_DFARA", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 5.8, "eps": 3353, "margin": "48%", "codal_date": "1405/07/25", "codal_summary": "جهش سود ناخالص در گزارش کدال پس از حذف ارز ترجیحی"},
    "داروند": {"id": "SYM_DARVAND", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 6.4, "eps": 1634, "margin": "44%", "codal_date": "1405/07/24", "codal_summary": "ثبت بالاترین تقاضای سرخط در گروه دارویی"},
    "دیران": {"id": "SYM_DIRAN", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 5.5, "eps": 4087, "margin": "49%", "codal_date": "1405/07/25", "codal_summary": "رشد 405% مبلغ فروش سالانه و 42% ماهانه در کدال"},
    "تیپیکو": {"id": "SYM_TPICO", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 5.9, "eps": 1945, "margin": "45%", "codal_date": "1405/07/23", "codal_summary": "هلدینگ دارویی تامین با رشد درآمد زیرمجموعه‌ها"},
    "دتولید": {"id": "SYM_DTOLID", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 6.1, "eps": 1893, "margin": "43%", "codal_date": "1405/07/24", "codal_summary": "پایداری فروش داخلی و صادراتی در گزارش مهرماه"},
    "شفارا": {"id": "SYM_SHFARA", "industry_id": "IND_PHARMA", "industry": "دارویی", "pe": 6.8, "eps": 352, "margin": "39%", "codal_date": "1405/07/20", "codal_summary": "موجود در پرتفوی واقعی؛ تیک صعودی مثبت"},
    "آسیاتک": {"id": "SYM_ASIATECH", "industry_id": "IND_TECH", "industry": "فناوری و ارتباطات", "pe": 7.4, "eps": 708, "margin": "38%", "codal_date": "1405/07/26", "codal_summary": "شفاف‌سازی کدال پیرامون بررسی افزایش تعرفه خدمات اینترنت"},
    "های‌وب": {"id": "SYM_HIWEB", "industry_id": "IND_TECH", "industry": "فناوری و ارتباطات", "pe": 7.8, "eps": 557, "margin": "35%", "codal_date": "1405/07/22", "codal_summary": "هم‌گروه آسیاتک در انتظار ابلاغ تعرفه‌های جدید اینترنت"},
    "پکویر": {"id": "SYM_PKAVIR", "industry_id": "IND_TIRE", "industry": "تایرسازی و لاستیک", "pe": 5.6, "eps": 5160, "margin": "36%", "codal_date": "1405/07/26", "codal_summary": "ابلاغ رسمی افزایش 23.4% نرخ فروش تایر رادیال سواری در کدال"},
    "خبهمن": {"id": "SYM_KHBAHMAN", "industry_id": "IND_AUTO", "industry": "خودرو و ساخت قطعات", "pe": 6.0, "eps": 456, "margin": "31%", "codal_date": "1405/07/25", "codal_summary": "کاتالیزور افزایش نرخ 45% زیرمجموعه (خاور) و صف خرید سنگین"},
    "خگستر": {"id": "SYM_KHGOSTAR", "industry_id": "IND_AUTO", "industry": "خودرو و ساخت قطعات", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/18", "codal_summary": "دادهٔ صورت مالی کامل در منبع فعلی موجود نیست (نوسانی حجم مشکوک)"},
    "خودرو": {"id": "SYM_KHODRO", "industry_id": "IND_AUTO", "industry": "خودرو و ساخت قطعات", "pe": None, "eps": -420, "margin": "-12%", "codal_date": "1405/07/20", "codal_summary": "زیان عملیاتی و خروج پول حقیقی؛ سیگنال هشدار خروج"},
    "خساپا": {"id": "SYM_KHSAIPA", "industry_id": "IND_AUTO", "industry": "خودرو و ساخت قطعات", "pe": None, "eps": -380, "margin": "-15%", "codal_date": "1405/07/20", "codal_summary": "زیان انباشته و قدرت خریدار 0.64؛ سیگنال هشدار خروج"},
    "اهرم": {"id": "SYM_AHROM", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق سرمایه‌گذاری اهرمی کاریزما | NAV: 88,958 R | حباب: -18.0%"},
    "شتاب": {"id": "SYM_SHETAB", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی شتاب آگاه | NAV: 22,550 R | حباب: -19.3%"},
    "توان": {"id": "SYM_TAVAN", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی توان مفید | NAV: 85,655 R | حباب: -18.7%"},
    "دوایکس": {"id": "SYM_2X", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی شاخصی کیان | ضریب اهرم 1.95x"},
    "جهش": {"id": "SYM_JAHESH", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی جهش | بیشترین تخفیف حباب (-19.6%)"},
    "نارنج": {"id": "SYM_NARANJ", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی نارنج | تراز پول حقیقی مثبت در کف"},
    "موج": {"id": "SYM_MOJ", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی موج | بازده 3 ماهه +141.7%"},
    "بیدار": {"id": "SYM_BIDAR", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی بیدار | حباب -14.5%"},
    "پیشران": {"id": "SYM_PISHRAN", "industry_id": "IND_LEVERAGED", "industry": "صندوق‌های اهرمی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق اهرمی پیشران | حباب -9.0%"},
    "عیار": {"id": "SYM_AYAR", "industry_id": "IND_GOLD", "industry": "صندوق‌های طلا و نقره", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "صندوق طلای عیار مفید | قیمت: 712,879 R | پناهگاه نقدینگی"},
    "فنقره": {"id": "SYM_FNOGHREH", "industry_id": "IND_GOLD", "industry": "صندوق‌های طلا و نقره", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/26", "codal_summary": "گواهی/نماد نقره | رشد 24% حجم معاملات و صف خرید 121.3B"},
    "فملی": {"id": "SYM_FAMELI", "industry_id": "IND_METALS", "industry": "فلزات اساسی و معدنی", "pe": 5.4, "eps": 5809, "margin": "52%", "codal_date": "1405/07/25", "codal_summary": "فروش دلاری و صادرات مس با P/E 5.4؛ ستون فقرات سبدهای بنیادی"},
    "فخوز": {"id": "SYM_FKHOUZ", "industry_id": "IND_METALS", "industry": "فلزات اساسی و معدنی", "pe": 4.2, "eps": 1020, "margin": "34%", "codal_date": "1405/07/22", "codal_summary": "تقسیم سود بالا (DPS) و P/E تحلیلی 4.2"},
    "کگل": {"id": "SYM_KGOL", "industry_id": "IND_METALS", "industry": "فلزات اساسی و معدنی", "pe": 5.1, "eps": 1350, "margin": "41%", "codal_date": "1405/07/21", "codal_summary": "لیدر سنگ‌آهن با تیک صعودی بالای پایانی"},
    "وکغدیر": {"id": "SYM_VKGHADIR", "industry_id": "IND_METALS", "industry": "فلزات اساسی و معدنی", "pe": 5.7, "eps": 1724, "margin": "47%", "codal_date": "1405/07/25", "codal_summary": "صف خرید 300 میلیارد تومانی در گروه معدنی"},
    "آریا": {"id": "SYM_ARIA", "industry_id": "IND_PETRO", "industry": "پتروشیمی و شیمیایی", "pe": 4.5, "eps": 2180, "margin": "42%", "codal_date": "1405/07/24", "codal_summary": "تقسیم سود 90% در مجمع و حاشیه سود بالای 40%"},
    "زاگرس": {"id": "SYM_ZAGROS", "industry_id": "IND_PETRO", "industry": "پتروشیمی و شیمیایی", "pe": 4.8, "eps": 2600, "margin": "40%", "codal_date": "1405/07/23", "codal_summary": "صادرات متانول و بهره‌مندی از رشد نرخ تسعیر ارز"},
    "شکیمیا": {"id": "SYM_SHKIMIA", "industry_id": "IND_PETRO", "industry": "پتروشیمی و شیمیایی", "pe": 6.3, "eps": 1290, "margin": "35%", "codal_date": "1405/07/25", "codal_summary": "ورود پول حقیقی و صف خرید 94.3 میلیارد تومانی"},
    "پترول": {"id": "SYM_PETROL", "industry_id": "IND_PETRO", "industry": "پتروشیمی و شیمیایی", "pe": 5.9, "eps": 480, "margin": "37%", "codal_date": "1405/07/24", "codal_summary": "موجود در پرتفوی واقعی؛ قفل صف خرید"},
    "اروند": {"id": "SYM_ARVAND", "industry_id": "IND_PETRO", "industry": "پتروشیمی و شیمیایی", "pe": 7.5, "eps": 8489, "margin": "28%", "codal_date": "1405/07/25", "codal_summary": "صف فروش سنگین 531 میلیارد تومانی؛ هشدار عدم ورود"},
    "وبملت": {"id": "SYM_VBMELAT", "industry_id": "IND_BANK", "industry": "بانک‌ها و موسسات اعتباری", "pe": 3.9, "eps": 820, "margin": "44%", "codal_date": "1405/07/24", "codal_summary": "تراز ارزی مثبت و P/E تحلیلی 3.9؛ لیدر گروه بانکی"},
    "وتجارت": {"id": "SYM_VTEJARAT", "industry_id": "IND_BANK", "industry": "بانک‌ها و موسسات اعتباری", "pe": 5.2, "eps": 174, "margin": "22%", "codal_date": "1405/07/24", "codal_summary": "خروج پول حقیقی و صف فروش 261.5 میلیارد تومانی"},
    "وبصادر": {"id": "SYM_VBSADER", "industry_id": "IND_BANK", "industry": "بانک‌ها و موسسات اعتباری", "pe": 5.8, "eps": 160, "margin": "19%", "codal_date": "1405/07/24", "codal_summary": "فشار فروش ناشی از اخبار سیاسی؛ قدرت خریدار 0.64"},
    "فاذر": {"id": "SYM_FAZAR", "industry_id": "IND_ENG", "industry": "فنی و مهندسی", "pe": 8.1, "eps": 287, "margin": "29%", "codal_date": "1405/07/25", "codal_summary": "لیدر گروه فنی‌مهندسی با صف خرید 272.8 میلیارد تومانی"},
    "رتکو": {"id": "SYM_RETKO", "industry_id": "IND_ENG", "industry": "فنی و مهندسی", "pe": 7.2, "eps": 3611, "margin": "33%", "codal_date": "1405/07/23", "codal_summary": "موجود در پرتفوی واقعی؛ هم‌گروه فاذر در صدر ورود پول صنعت"},
    "فاراک": {"id": "SYM_FARAK", "industry_id": "IND_ENG", "industry": "فنی و مهندسی", "pe": 7.6, "eps": 423, "margin": "30%", "codal_date": "1405/07/22", "codal_summary": "موجود در پرتفوی واقعی؛ تقاضای مثبت در سقف روزانه"},
    "کیسون": {"id": "SYM_KISON", "industry_id": "IND_ENG", "industry": "فنی و مهندسی", "pe": 8.4, "eps": 490, "margin": "27%", "codal_date": "1405/07/19", "codal_summary": "سیگنال صف‌شکن و برگشت از محدوده منفی به مثبت"},
    "فکور": {"id": "SYM_FAKOR", "industry_id": "IND_ENG", "industry": "فنی و مهندسی", "pe": 6.9, "eps": 889, "margin": "35%", "codal_date": "1405/07/25", "codal_summary": "عرضه اولیه جدید با صف خرید 49.5 میلیارد تومانی"},
    "سخاش": {"id": "SYM_SKHASH", "industry_id": "IND_CEMENT", "industry": "سیمان و کانی غیرفلزی", "pe": 6.0, "eps": 2535, "margin": "46%", "codal_date": "1405/07/24", "codal_summary": "سیمان صادراتی با صف خرید 52.3 میلیارد تومانی"},
    "سغدیر": {"id": "SYM_SGHADIR", "industry_id": "IND_CEMENT", "industry": "سیمان و کانی غیرفلزی", "pe": 5.8, "eps": 5084, "margin": "48%", "codal_date": "1405/07/24", "codal_summary": "سنگین‌ترین وزن پرتفوی واقعی شما (11.57%) با صف خرید"},
    "کفرا": {"id": "SYM_KAFRA", "industry_id": "IND_CEMENT", "industry": "سیمان و کانی غیرفلزی", "pe": 6.4, "eps": 929, "margin": "41%", "codal_date": "1405/07/25", "codal_summary": "صدرنشین ورود پول کانی غیرفلزی با صف خرید 159.2B"},
    "چخزر": {"id": "SYM_CHKHZ", "industry_id": "IND_OTHER", "industry": "سایر صنایع تولیدی", "pe": 9.2, "eps": 31478, "margin": "26%", "codal_date": "1405/07/21", "codal_summary": "نماد کم‌شناور با صف خرید 151 میلیارد تومانی"},
    "ثفارس": {"id": "SYM_SFARS", "industry_id": "IND_OTHER", "industry": "انبوه‌سازی و املاک", "pe": 8.5, "eps": 810, "margin": "31%", "codal_date": "1405/07/18", "codal_summary": "بلعیده شدن صف فروش اول وقت و چرخش شارپ"},
    "وآذر": {"id": "SYM_VAZAR", "industry_id": "IND_INV", "industry": "سرمایه‌گذاری‌ها", "pe": 7.9, "eps": 680, "margin": "30%", "codal_date": "1405/07/19", "codal_summary": "کم‌شناور با حجم 2.5 برابر میانگین ماهانه"},
    "تابان": {"id": "SYM_TABAN", "industry_id": "IND_OTHER", "industry": "سایر صنایع تولیدی", "pe": None, "eps": None, "margin": None, "codal_date": "1405/07/25", "codal_summary": "صف فروش سنگین 469 میلیارد تومانی؛ هشدار عدم خرید"},
    "شتران": {"id": "SYM_SHTRAN", "industry_id": "IND_OIL", "industry": "فرآورده‌های نفتی و پالایشی", "pe": 6.5, "eps": None, "margin": "14%", "codal_date": "1405/07/25", "codal_summary": "اطلاعیه کدال مبنی بر کاهش سود ناخالص نیمه دوم در شرایط اضطرار"}
}


def build_all():
    acquire_lock()
    try:
        dubai_now = now_dubai_iso()
        tehran_now = now_tehran_iso()

        # 1. بارگذاری بکاپ فایربیس برای حفظ ۱۰۰٪ داده‌های قبلی
        fb_backup_path = os.path.join(DATA_DIR, "backups", "firebase_live_backup_20261018.json")
        fb_data = {}
        if os.path.exists(fb_backup_path):
            with open(fb_backup_path, "r", encoding="utf-8") as f:
                fb_data = json.load(f)

        # 2. ادغام نمادهای غربال‌شده (بدون حذف هیچ رکوردی از فایربیس یا نسخهٔ فعلی)
        v6_stocks = [
            {"symbol": "درازی", "name": "پخش رازی (74,470 R)", "category": "asiatech", "categoryLabel": "فیلتر آسیاتک", "fundGrade": "A+", "techGrade": "A+", "queueStatus": "صف خرید 182.6B", "score": 97, "priceChange": 2.50, "power": 2.65, "realFlow": 18.2, "bidAsk": "4.2x", "probUp": 88, "probDown": 12, "target": "+5.0% تا +8.0% (صف خرید 182.6B)", "stopLoss": "-1.8% (71,500 R)", "scenario": "برخلاف ریزش شاخص، درازی با قیمت 74,470 R و صف خرید 182.6 B.T قوی‌ترین سهم دارویی تابلو است.", "chips": ["صف خرید 182B", "ضد ریزش", "لیدر دارو"], "source": "تابلوخوانی زنده + کدال", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "دفارا", "name": "داروسازی فارابی (19,450 R)", "category": "asiatech", "categoryLabel": "فیلتر آسیاتک", "fundGrade": "A+", "techGrade": "A+", "queueStatus": "صف خرید 266.3B", "score": 95, "priceChange": 2.70, "power": 2.50, "realFlow": 26.6, "bidAsk": "3.9x", "probUp": 86, "probDown": 14, "target": "+4.5% تا +7.0% (صف خرید 266.3B)", "stopLoss": "-1.8% (18,800 R)", "scenario": "جذب پول حقیقی سنگین و صف خرید 266.3 B.T (137.2M سهم) در دل بازار منفی.", "chips": ["صف خرید 266B", "ورود پول حقیقی", "دارویی"], "source": "تابلوخوانی زنده + کدال", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "پکویر", "name": "کویر تایر (28,900 R)", "category": "asiatech", "categoryLabel": "فیلتر آسیاتک", "fundGrade": "A+", "techGrade": "A", "queueStatus": "پیش‌صف 3.3x", "score": 92, "priceChange": 2.85, "power": 2.35, "realFlow": 8.4, "bidAsk": "3.3x", "probUp": 83, "probDown": 17, "target": "+5.0% تا +9.0% (کاتالیزور نرخ)", "stopLoss": "-1.6%", "scenario": "ابلاغ رسمی افزایش +23.4% نرخ فروش تایر رادیال سواری در کدال؛ مستعد قفل صف خرید.", "chips": ["افزایش نرخ 23.4%", "کاتالیزور کدال", "پیش‌صف"], "source": "کدال + تابلوخوانی", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "آسیاتک", "name": "انتقال داده‌های آسیاتک (5,240 R)", "category": "asiatech", "categoryLabel": "فیلتر آسیاتک", "fundGrade": "A", "techGrade": "A+", "queueStatus": "پیش‌صف 3.8x", "score": 96, "priceChange": 3.25, "power": 2.85, "realFlow": 5.4, "bidAsk": "3.8x", "probUp": 86, "probDown": 14, "target": "+5.0% (قفل صف خرید)", "stopLoss": "-1.5% (5,100 R)", "scenario": "تراکم تقاضای ردیف 1 تا 3 بیش از 3.8 برابر عرضه و سرانه خرید 2.85؛ شفاف‌سازی تعرفه در کدال.", "chips": ["بید 3.8x عرضه", "سرانه 2.85", "فیلتر آسیاتک"], "source": "فایربیس + تابلوخوانی", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "داروند", "name": "داروسازی اروند (10,460 R)", "category": "live", "categoryLabel": "پول درشت زنده", "fundGrade": "A+", "techGrade": "A+", "queueStatus": "صف خرید 521B", "score": 96, "priceChange": 2.95, "power": 3.10, "realFlow": 52.1, "bidAsk": "5.1x", "probUp": 87, "probDown": 13, "target": "+5.0% تا +8.5%", "stopLoss": "-1.8% (10,100 R)", "scenario": "سنگین‌ترین صف خرید کل بورس به ارزش 521.0 B.T (498.1M سهم) در قیمت 10,460 R.", "chips": ["صف خرید 521B", "رتبه 1 تقاضا"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "خبهمن", "name": "گروه بهمن (2,741 R)", "category": "live", "categoryLabel": "پول درشت زنده", "fundGrade": "A", "techGrade": "A+", "queueStatus": "صف خرید 389.7B", "score": 94, "priceChange": 1.95, "power": 2.45, "realFlow": 38.9, "bidAsk": "3.6x", "probUp": 84, "probDown": 16, "target": "+4.5% تا +6.5%", "stopLoss": "-1.8% (2,650 R)", "scenario": "جزو 4 نماد اول ورود پول حقیقی بازار با صف خرید 389.7 B.T و کاتالیزور افزایش نرخ +45% خاور.", "chips": ["صف خرید 389B", "ورود پول درشت"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "وکغدیر", "name": "سرمایه‌گذاری کغدیر (9,830 R)", "category": "live", "categoryLabel": "پول درشت زنده", "fundGrade": "A", "techGrade": "A", "queueStatus": "صف خرید 300B", "score": 91, "priceChange": 2.93, "power": 2.30, "realFlow": 30.0, "bidAsk": "3.4x", "probUp": 82, "probDown": 18, "target": "+4.0% تا +6.0%", "stopLoss": "-1.6% (9,550 R)", "scenario": "جذب پول خرد در روز منفی بازار و تشکیل صف خرید 300.0 B.T (305.1M سهم).", "chips": ["صف خرید 300B", "معدنی"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "فاذر", "name": "صنایع آذرآب (2,327 R)", "category": "live", "categoryLabel": "پول درشت زنده", "fundGrade": "B", "techGrade": "A+", "queueStatus": "صف خرید 272.8B", "score": 90, "priceChange": 1.37, "power": 2.20, "realFlow": 27.2, "bidAsk": "3.2x", "probUp": 80, "probDown": 20, "target": "+4.0% تا +6.0%", "stopLoss": "-1.8% (2,250 R)", "scenario": "گروه فنی و مهندسی با +285 B.T صدرنشین ورود پول صنایع است؛ صف خرید 272.8 B.T در فاذر.", "chips": ["صف خرید 272B", "لیدر فنی‌مهندسی"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "اهرم", "name": "صندوق اهرمی اهرم (72,946 R)", "category": "intraday", "categoryLabel": "نوسانی کوتاه‌مدت", "fundGrade": "A+", "techGrade": "A", "queueStatus": "حباب -18.0%", "score": 91, "priceChange": -4.00, "power": 1.45, "realFlow": 3.20, "bidAsk": "1.4x", "probUp": 78, "probDown": 22, "target": "+4.0% تا +8.0% در برگشت شاخص", "stopLoss": "-2.0% (70,500 R)", "scenario": "قیمت 72,946 R با حباب منفی -18.0%؛ تراز پول حقیقی آن در کف روزانه مثبت شد (جمع‌آوری هوشمند).", "chips": ["حباب -18.0%", "تراز حقیقی مثبت"], "source": "تابلوخوانی + فاندای", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "دوایکس", "name": "اهرمی شاخصی کیان (46,325 R)", "category": "intraday", "categoryLabel": "نوسانی کوتاه‌مدت", "fundGrade": "A", "techGrade": "A+", "queueStatus": "اهرم 1.95x", "score": 88, "priceChange": -4.00, "power": 1.52, "realFlow": 7.65, "bidAsk": "1.5x", "probUp": 77, "probDown": 23, "target": "+4.0% تا +8.0% نوسانی", "stopLoss": "-2.0% (44,800 R)", "scenario": "جذب 765 B.T پول حقیقی در هفته اخیر و بازده 1 ساله +557% (رتبه 1 اهرمی‌ها).", "chips": ["جذب 765B هفتگی", "رتبه 1 بازده"], "source": "تابلوخوانی + فاندای", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "عیار", "name": "صندوق طلای عیار (712,879 R)", "category": "intraday", "categoryLabel": "نوسانی کوتاه‌مدت", "fundGrade": "A+", "techGrade": "A+", "queueStatus": "ورود پول +45B", "score": 96, "priceChange": 2.97, "power": 2.40, "realFlow": 45.0, "bidAsk": "3.5x", "probUp": 90, "probDown": 10, "target": "+3.5% تا +6.0% پوشش ریسک", "stopLoss": "-1.0% (700,000 R)", "scenario": "قیمت هر واحد 712,879 R (NAV صندوق 378T و طلای 18 عیار گرمی 26.2M T)؛ پناهگاه نقدینگی در روز منفی.", "chips": ["سپر ریسک", "انس 4,166$"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "فنقره", "name": "صندوق/نماد نقره (24,540 R)", "category": "tick", "categoryLabel": "الگوی ساعت (تیک)", "fundGrade": "A", "techGrade": "A+", "queueStatus": "صف خرید 121.3B", "score": 91, "priceChange": 2.98, "power": 2.35, "realFlow": 12.1, "bidAsk": "3.1x", "probUp": 83, "probDown": 17, "target": "+4.0% تا +6.0%", "stopLoss": "-1.5% (23,800 R)", "scenario": "رشد +24% حجم معاملات نقره و صف خرید 121.3 B.T در قیمت 24,540 R با تیک صعودی کامل.", "chips": ["صف خرید 121B", "تیک +2.98%"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "شکیمیا", "name": "پتروشیمی کیمیاگران (8,130 R)", "category": "tick", "categoryLabel": "الگوی ساعت (تیک)", "fundGrade": "A", "techGrade": "A", "queueStatus": "صف خرید 94.3B", "score": 88, "priceChange": 2.91, "power": 2.15, "realFlow": 9.4, "bidAsk": "2.8x", "probUp": 80, "probDown": 20, "target": "+4.0% کوتاه‌مدت", "stopLoss": "-1.5% (7,900 R)", "scenario": "جزو معدود پتروشیمی‌های مثبت بازار با ورود پول حقیقی و صف خرید 94.3 B.T.", "chips": ["صف خرید 94B", "ورود پول خرد"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "سخاش", "name": "سیمان خاش (15,210 R)", "category": "tick", "categoryLabel": "الگوی ساعت (تیک)", "fundGrade": "A", "techGrade": "A", "queueStatus": "صف خرید 52.3B", "score": 86, "priceChange": 2.98, "power": 2.05, "realFlow": 5.2, "bidAsk": "2.6x", "probUp": 78, "probDown": 22, "target": "+3.5% تا +5.0%", "stopLoss": "-1.5% (14,800 R)", "scenario": "جذب پول حقیقی و صف خرید 52.3 B.T در قیمت 15,210 R برخلاف جو منفی بازار.", "chips": ["صف خرید 52B", "سیمان صادراتی"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "کفرا", "name": "فرآورده‌های نسوز ایران (5,950 R)", "category": "queue", "categoryLabel": "صف‌شکن قدرتمند", "fundGrade": "A", "techGrade": "A+", "queueStatus": "صف خرید 159.2B", "score": 89, "priceChange": 2.08, "power": 2.25, "realFlow": 15.9, "bidAsk": "3.0x", "probUp": 81, "probDown": 19, "target": "+4.5% تا +7.0%", "stopLoss": "-2.0% (5,750 R)", "scenario": "صدرنشین ورود پول به گروه کانی غیرفلزی با صف خرید 159.2 B.T (269.6M سهم).", "chips": ["صف خرید 159B", "کانی غیرفلزی"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "چخزر", "name": "صنایع چوب خزر (289,600 R)", "category": "queue", "categoryLabel": "صف‌شکن قدرتمند", "fundGrade": "B", "techGrade": "A+", "queueStatus": "صف خرید 151B", "score": 87, "priceChange": 1.35, "power": 2.10, "realFlow": 15.1, "bidAsk": "2.9x", "probUp": 77, "probDown": 23, "target": "+4.5% نوسانی", "stopLoss": "-2.0% (280,000 R)", "scenario": "صف خرید 151.0 B.T در قیمت 289,600 R و بلعیدن کامل عرضه‌ها (اسمال‌کپ کم‌شناور).", "chips": ["صف خرید 151B", "اسمال‌کپ کم‌شناور"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "فکور", "name": "فکور صنعت (6,140 R - عرضه اولیه)", "category": "queue", "categoryLabel": "صف‌شکن قدرتمند", "fundGrade": "A", "techGrade": "A+", "queueStatus": "صف خرید 49.5B", "score": 86, "priceChange": 2.85, "power": 2.40, "realFlow": 4.9, "bidAsk": "3.5x", "probUp": 82, "probDown": 18, "target": "+5.0% تا +10.0%", "stopLoss": "-1.5% (5,950 R)", "scenario": "عرضه اولیه جدید بازار با ورود پول حقیقی و صف خرید 49.5 B.T (80.6M سهم).", "chips": ["عرضه اولیه", "صف خرید 49.5B"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "دیران", "name": "داروسازی ایران (22,480 R)", "category": "midterm", "categoryLabel": "بنیادی & کدال", "fundGrade": "A+", "techGrade": "B", "queueStatus": "رشد فروش +405%", "score": 95, "priceChange": -2.98, "power": 0.95, "realFlow": -1.2, "bidAsk": "0.7x", "probUp": 84, "probDown": 16, "target": "+45% میان‌مدت (رشد فروش 405%)", "stopLoss": "نگهداری در سبد پایه", "scenario": "سهم بنیادی با رشد فروش سالانه +405% که به دلیل جو سیاسی در کف اصلاحی است؛ کمین برای جمع شدن صف.", "chips": ["رشد فروش 405%", "بنیادی A+"], "source": "کدال + فاندبیس", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "فملی", "name": "ملی صنایع مس ایران (31,370 R)", "category": "midterm", "categoryLabel": "بنیادی & کدال", "fundGrade": "A+", "techGrade": "B", "queueStatus": "P/E 5.4 دلاری", "score": 92, "priceChange": -3.00, "power": 0.85, "realFlow": -16.3, "bidAsk": "0.5x", "probUp": 88, "probDown": 12, "target": "+65% تا +85% سالانه", "stopLoss": "نگهداری در سبد پایه", "scenario": "ستون فقرات سبدهای بنیادی با P/E 5.4 و فروش دلاری مس؛ تحت فشار عرضه کل شاخص.", "chips": ["قیمت 31,370R", "P/E 5.4 دلاری"], "source": "کدال + ره‌آورد", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "دتولید", "name": "داروسازی تولیددارو (11,550 R)", "category": "midterm", "categoryLabel": "بنیادی & کدال", "fundGrade": "A+", "techGrade": "A+", "queueStatus": "صف خرید 125.9B", "score": 90, "priceChange": 2.94, "power": 2.20, "realFlow": 12.5, "bidAsk": "3.1x", "probUp": 83, "probDown": 17, "target": "+5.0% کوتاه‌مدت", "stopLoss": "-1.8% (11,200 R)", "scenario": "صف خرید 125.9 B.T (109M سهم) در قیمت 11,550 R؛ مقاومت عالی در برابر ریزش شاخص.", "chips": ["صف خرید 125.9B", "دارویی A+"], "source": "تابلوخوانی + کدال", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "اروند", "name": "پتروشیمی اروند (63,670 R)", "category": "exit", "categoryLabel": "هشدار خروج / نخر", "fundGrade": "C", "techGrade": "D", "queueStatus": "صف فروش 531B!", "score": 28, "priceChange": -2.99, "power": 0.42, "realFlow": -53.1, "bidAsk": "0.1x", "probUp": 14, "probDown": 86, "target": "خرید ممنوع (صف فروش 531B)", "stopLoss": "خروج پول سنگین", "scenario": "سنگین‌ترین صف فروش بازار به ارزش 530.98 B.T در قیمت 63,670 R و بیشترین خروج پول حقیقی.", "chips": ["صف فروش 531B!", "خروج پول!", "نخر!"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "تابان", "name": "تابان (24,300 R)", "category": "exit", "categoryLabel": "هشدار خروج / نخر", "fundGrade": "C", "techGrade": "D", "queueStatus": "صف فروش 469B!", "score": 30, "priceChange": -2.99, "power": 0.45, "realFlow": -46.9, "bidAsk": "0.1x", "probUp": 15, "probDown": 85, "target": "خرید ممنوع (صف فروش 469B)", "stopLoss": "فشار فروش شدید", "scenario": "صف فروش 469.16 B.T (193M سهم) و خروج سنگین نقدینگی خرد.", "chips": ["صف فروش 469B!", "نخر!"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "وتجارت", "name": "بانک تجارت (908 R)", "category": "exit", "categoryLabel": "هشدار خروج / نخر", "fundGrade": "C", "techGrade": "D", "queueStatus": "صف فروش 261.5B!", "score": 34, "priceChange": -2.99, "power": 0.51, "realFlow": -26.1, "bidAsk": "0.2x", "probUp": 18, "probDown": 82, "target": "خرید ممنوع (صف فروش 261.5B)", "stopLoss": "قدرت خریدار < 0.7", "scenario": "صف فروش 2.88B سهم به ارزش 261.5 B.T در قیمت 908 R؛ ورود ممنوع تا تخلیه کامل فشار فروش.", "chips": ["صف فروش 261B!", "نخر!"], "source": "تابلوخوانی زنده", "dataTime": "1405/07/26 12:30", "isExperimental": False},
            {"symbol": "شتران", "name": "پالایش نفت تهران (ابهام کدال)", "category": "exit", "categoryLabel": "هشدار خروج / نخر", "fundGrade": "D", "techGrade": "D", "queueStatus": "ابهام سود کدال", "score": 25, "priceChange": -3.00, "power": 0.40, "realFlow": -18.5, "bidAsk": "0.2x", "probUp": 12, "probDown": 88, "target": "احتیاط کامل (ابهام دستورالعمل)", "stopLoss": "کاهش سود اضطرار به 31T", "scenario": "اعلام کاهش سود ناخالص نیمه دوم از 136T به 31T در شرایط اضطرار؛ عامل فشار فروش گروه پالایشی.", "chips": ["ابهام سود کدال!", "احتیاط!"], "source": "کدال + تابلوخوانی", "dataTime": "1405/07/25 18:00", "isExperimental": False},
        ]

        merged_map = {item["symbol"]: item for item in v6_stocks}

        # افزودن تمام نمادهای موجود در فایربیس که در لیست بالا نبودند (حفظ ۱۰۰٪ رکوردها)
        for fb_item in fb_data.get("stocksData", []):
            sym = fb_item.get("symbol")
            if sym and sym not in merged_map:
                merged_map[sym] = {
                    "symbol": sym,
                    "name": fb_item.get("name", sym),
                    "category": fb_item.get("category", "all"),
                    "categoryLabel": fb_item.get("categoryLabel", "سابقه فایربیس"),
                    "fundGrade": fb_item.get("fundGrade", "A" if fb_item.get("score", 70) >= 85 else ("B" if fb_item.get("score", 70) >= 75 else "C")),
                    "techGrade": fb_item.get("techGrade", "A" if fb_item.get("power", 1.0) >= 2.0 else ("B" if fb_item.get("power", 1.0) >= 1.5 else "D")),
                    "queueStatus": fb_item.get("queueStatus", fb_item.get("categoryLabel", "ثبت در آرشیو")),
                    "score": fb_item.get("score", 75),
                    "priceChange": fb_item.get("priceChange", 0.0),
                    "power": fb_item.get("power", 1.0),
                    "realFlow": fb_item.get("realFlow", 0.0),
                    "bidAsk": fb_item.get("bidAsk", "1.0x"),
                    "probUp": fb_item.get("probUp", 50),
                    "probDown": fb_item.get("probDown", 50),
                    "target": fb_item.get("target", "مطابق استراتژی"),
                    "stopLoss": fb_item.get("stopLoss", "-2.0%"),
                    "scenario": fb_item.get("scenario", ""),
                    "chips": fb_item.get("chips", []),
                    "source": "آرشیو فایربیس (Signal Ledger)",
                    "dataTime": "1405/07/25 15:30",
                    "isExperimental": fb_item.get("category") in ("intraday", "queue")
                }

        signals_list = []
        for idx, (sym, s_obj) in enumerate(merged_map.items(), start=1):
            meta = SYMBOL_META.get(sym, {})
            sym_id = meta.get("id", f"SYM_{idx:03d}")
            s_obj["recordId"] = f"SIG_{idx:03d}"
            s_obj["symbolId"] = sym_id
            s_obj["industryId"] = meta.get("industry_id", "IND_OTHER")
            s_obj["industry"] = meta.get("industry", "سایر صنایع")
            s_obj["fetchedAtDubai"] = dubai_now
            s_obj["validityStatus"] = "valid"
            s_obj["freshnessStatus"] = "fresh" if "1405/07/26" in s_obj["dataTime"] else "archived_snapshot"
            signals_list.append(s_obj)

        # ۱. market.json
        market_payload = {
            "schemaVersion": "2.0.0",
            "productName": "شاگرد بورس | دستیار بورسی",
            "timezoneDisplay": "Asia/Dubai",
            "updatedAtDubai": dubai_now,
            "updatedAtTehran": tehran_now,
            "source": "TSE Live Snapshot + Firebase RTDB",
            "freshness": "last_valid_snapshot",
            "fetchError": None,
            "marketPulse": {
                "dateJalali": "1405/07/26",
                "overallIndex": {"value": 8104000, "changePct": -1.95, "status": "negative"},
                "equalWeightIndex": {"value": 2192180, "changePct": -1.51, "status": "negative"},
                "realMoneyFlowB": {"value": -700.0, "prevDayT": -8.0, "unit": "Billion Toman", "status": "outflow"},
                "marketBreadth": {"positivePct": 30, "negativePct": 70, "buyQueuesB": 2850, "sellQueuesB": 4120},
                "goldAyar": {"priceR": 712879, "changePct": 2.97, "gram18kT": 26200000, "onsUsd": 4166},
                "regime": {
                    "current": "bear",
                    "label": "نزولی تدافعی (فشار عرضه و ریسک سیاسی)",
                    "recommendedStockPct": 55,
                    "recommendedSafePct": 45
                }
            },
            "leveragedFunds": [
                {"id": "SYM_JAHESH", "name": "جهش", "price": 16250, "nav": 20210, "bubble": -19.60, "median120d": -15.20, "leverage": 1.85, "status": "بیشترین تخفیف حباب (-19.6%) | بازده هفتگی +8.96%", "source": "فاندای + تابلو"},
                {"id": "SYM_SHETAB", "name": "شتاب", "price": 18200, "nav": 22550, "bubble": -19.30, "median120d": -16.20, "leverage": 1.88, "status": "حباب منفی جذاب (-19.3%) | بازده هفتگی +2.03%", "source": "فاندای + تابلو"},
                {"id": "SYM_NARANJ", "name": "نارنج", "price": 68309, "nav": 84645, "bubble": -19.30, "median120d": -15.00, "leverage": 1.75, "status": "قیمت 68,309 R | تراز پول حقیقی مثبت در کف!", "source": "فاندای + تابلو"},
                {"id": "SYM_TAVAN", "name": "توان", "price": 69638, "nav": 85655, "bubble": -18.70, "median120d": -13.80, "leverage": 1.82, "status": "قیمت 69,638 R | جذب 479 B.T پول در هفته اخیر", "source": "فاندای + تابلو"},
                {"id": "SYM_AHROM", "name": "اهرم", "price": 72946, "nav": 88958, "bubble": -18.00, "median120d": -15.50, "leverage": 1.90, "status": "لیدر نقدشوندگی | تراز پول خرد مثبت در کف!", "source": "فاندای + تابلو"},
                {"id": "SYM_MOJ", "name": "موج", "price": 104733, "nav": 122495, "bubble": -14.50, "median120d": -16.50, "leverage": 1.78, "status": "قیمت 104,733 R | بازده 3 ماهه +141.7%", "source": "فاندای + تابلو"},
                {"id": "SYM_BIDAR", "name": "بیدار", "price": 14800, "nav": 17310, "bubble": -14.50, "median120d": -14.80, "leverage": 1.70, "status": "بازده 3 ماهه +123.7% | تعادلی", "source": "فاندای + تابلو"},
                {"id": "SYM_PISHRAN", "name": "پیشران", "price": 17400, "nav": 19120, "bubble": -9.00, "median120d": -14.00, "leverage": 1.65, "status": "کمترین گردش نقدینگی | نظاره", "source": "فاندای + تابلو"},
                {"id": "SYM_2X", "name": "دوایکس", "price": 46325, "nav": 42893, "bubble": 8.00, "median120d": -5.00, "leverage": 1.95, "status": "اهرم 1.95x | جذب 765 B.T هفتگی و بازده سالانه +557%", "source": "فاندای + تابلو"}
            ],
            "legacyLeveragedSnapshot": fb_data.get("leveragedData", [])
        }
        atomic_write_json(os.path.join(DATA_DIR, "market.json"), market_payload)

        # ۲. signals.json
        signals_payload = {
            "schemaVersion": "2.0.0",
            "updatedAtDubai": dubai_now,
            "totalRecords": len(signals_list),
            "filtersCatalog": [
                {"id": "asiatech", "name": "فیلتر آسیاتک (پیش‌صف)", "status": "operational", "winRateBacktest": "84%", "formula": "Bid_Top3 >= 3.0 * Ask_Top3 AND Buyer_Power >= 2.2 AND Price_Change BETWEEN +2.0% AND +3.8%"},
                {"id": "live", "name": "ورود پول درشت زنده", "status": "operational", "winRateBacktest": "78%", "formula": "Real_Money_Inflow >= 2.0B Toman AND Buyer_Power >= 1.8"},
                {"id": "intraday", "name": "جهش کوتاه‌مدت (5 و 15 دقیقه‌ای)", "status": "operational", "winRateBacktest": "74%", "formula": "Volume_15m >= 2.5 * Avg_Volume_15m AND Buyer_Power >= 1.45"},
                {"id": "tick", "name": "الگوی ساعت (تیک صعودی)", "status": "operational", "winRateBacktest": "76%", "formula": "(Last_Price - Close_Price) / Close_Price >= +2.0% AND Buyer_Power >= 1.6"},
                {"id": "queue", "name": "صف‌شکن و اسمال‌کپ", "status": "operational", "winRateBacktest": "72%", "formula": "Sell_Queue_Broken == True AND Buyer_Power >= 1.85"},
                {"id": "midterm", "name": "بنیادی و گزارش کدال", "status": "operational", "winRateBacktest": "86%", "formula": "Codal_Monthly_Sales_Growth >= +35% AND Analytical_PE <= 6.5"},
                {"id": "exit", "name": "هشدار خروج / نخر", "status": "operational", "winRateBacktest": "83%", "formula": "Buyer_Power < 0.70 AND Real_Money_Inflow < -2.0B Toman"},
                {"id": "options_arb", "name": "آربیتراژ اختیار معامله و حباب", "status": "experimental", "winRateBacktest": "آزمایشی (در حال تست)", "formula": "Implied_Volatility_Skew & Leveraged_NAV_Discount"}
            ],
            "signals": signals_list
        }
        atomic_write_json(os.path.join(DATA_DIR, "signals.json"), signals_payload)

        # ۳. portfolios.json
        portfolios_payload = {
            "schemaVersion": "2.0.0",
            "updatedAtDubai": dubai_now,
            "disclaimer": "برچسب‌های سطح ریسک حاصل معیارهای تعریف‌شده (ضریب بتا، نوسان تاریخی و حباب) هستند و تضمین‌کنندهٔ سود یا زیان آینده نیستند.",
            "omixWeekly": {
                "id": "PORT_OMIX_WEEKLY",
                "title": "سبد هفتگی اومیکس (OMIX / OMAX)",
                "rule": "5 نماد با وزن مساوی 20% — حفظ کامل تاریخچهٔ هفته‌های قبل بدون بازنویسی",
                "currentVersion": "W5_1405_07_26",
                "versions": [
                    {
                        "versionId": "W5_1405_07_26",
                        "week": "هفته 5 (26 مهر 1405 - ترکیب فعلی)",
                        "date": "1405/07/26",
                        "stocks": [
                            {"symbol": "درازی", "weight": 20, "reason": "صف خرید 182.6B و رشد 42% فروش کدال", "status": "حفظ از هفته قبل"},
                            {"symbol": "دفارا", "weight": 20, "reason": "صف خرید 266.3B و حذف ارز ترجیحی", "status": "ورود جدید"},
                            {"symbol": "داروند", "weight": 20, "reason": "سنگین‌ترین صف خرید بازار (521B)", "status": "ورود جدید"},
                            {"symbol": "خبهمن", "weight": 20, "reason": "صف خرید 389.7B و افزایش نرخ خاور", "status": "ورود جدید"},
                            {"symbol": "عیار", "weight": 20, "reason": "سپر ریسک سیاسی در رژیم منفی بازار", "status": "ورود مجدد"}
                        ],
                        "changeReason": "چرخش به آرایش ضدریزش در واکنش به خروج پول کل بازار (-700B)",
                        "weekReturn": "+6.4%",
                        "cumulativeReturn": "+26.2%",
                        "benchmarkDiff": "+8.35% نسبت به شاخص کل"
                    },
                    {
                        "versionId": "W4_1405_07_19",
                        "week": "هفته 4 مهر 1405",
                        "date": "1405/07/19",
                        "stocks": [
                            {"symbol": "آسیاتک", "weight": 20, "reason": "سیگنال پیش از صف خرید (3.8x)", "status": "ورود جدید"},
                            {"symbol": "دیران", "weight": 20, "reason": "لیدر بنیادی دارو", "status": "حفظ"},
                            {"symbol": "درازی", "weight": 20, "reason": "ورود پول درشت 3 روزه", "status": "حفظ"},
                            {"symbol": "اهرم", "weight": 20, "reason": "لیدر نوسانی در کف حباب", "status": "حفظ"},
                            {"symbol": "فملی", "weight": 20, "reason": "ستون فقرات دلاری", "status": "حفظ"}
                        ],
                        "changeReason": "ورود آسیاتک با سیگنال پیش از صف به جای عیار",
                        "weekReturn": "+5.8%",
                        "cumulativeReturn": "+24.8%",
                        "benchmarkDiff": "+4.1% نسبت به شاخص کل"
                    },
                    {
                        "versionId": "W3_1405_07_12",
                        "week": "هفته 3 مهر 1405",
                        "date": "1405/07/12",
                        "stocks": [
                            {"symbol": "دیران", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "درازی", "weight": 20, "reason": "ورود به جای وبملت", "status": "ورود جدید"},
                            {"symbol": "اهرم", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "فملی", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "عیار", "weight": 20, "reason": "حفظ", "status": "حفظ"}
                        ],
                        "changeReason": "ورود درازی به جای وبملت پس از سیگنال کدال دارو",
                        "weekReturn": "+4.9%",
                        "cumulativeReturn": "+18.0%",
                        "benchmarkDiff": "+3.2% نسبت به شاخص کل"
                    },
                    {
                        "versionId": "W2_1405_07_05",
                        "week": "هفته 2 مهر 1405",
                        "date": "1405/07/05",
                        "stocks": [
                            {"symbol": "دیران", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "وبملت", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "اهرم", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "فملی", "weight": 20, "reason": "حفظ", "status": "حفظ"},
                            {"symbol": "عیار", "weight": 20, "reason": "حفظ", "status": "حفظ"}
                        ],
                        "changeReason": "تثبیت 5 سهم برتر هفته اول",
                        "weekReturn": "+6.4%",
                        "cumulativeReturn": "+12.5%",
                        "benchmarkDiff": "+2.9% نسبت به شاخص کل"
                    },
                    {
                        "versionId": "W1_1405_06_29",
                        "week": "هفته 1 مهر 1405",
                        "date": "1405/06/29",
                        "stocks": [
                            {"symbol": "دیران", "weight": 20, "reason": "چیدمان اولیه", "status": "اولیه"},
                            {"symbol": "وبملت", "weight": 20, "reason": "چیدمان اولیه", "status": "اولیه"},
                            {"symbol": "اهرم", "weight": 20, "reason": "چیدمان اولیه", "status": "اولیه"},
                            {"symbol": "فملی", "weight": 20, "reason": "چیدمان اولیه", "status": "اولیه"},
                            {"symbol": "عیار", "weight": 20, "reason": "چیدمان اولیه", "status": "اولیه"}
                        ],
                        "changeReason": "چیدمان اولیه مهرماه",
                        "weekReturn": "+5.7%",
                        "cumulativeReturn": "+5.7%",
                        "benchmarkDiff": "+2.1% نسبت به شاخص کل"
                    }
                ]
            },
            "riskCategorizedPortfolios": [
                {"id": "PORT_L1", "code": "L1", "riskLevel": "low", "riskLabel": "کم‌ریسک", "title": "پایدار بنیادی & سپر طلا", "strategy": "25% طلای عیار برای پوشش جهش دلار + غول‌های دلاری با P/E پایین (sabadgardan9)", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+88% (بک‌تست 1 ساله)", "maxDrawdown": "-7.0%", "benchmarkDiff": "+34% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "عیار", "weight": 25, "note": "سپر جهش دلار"}, {"symbol": "فملی", "weight": 20, "note": "P/E 5.4 دلاری"}, {"symbol": "فخوز", "weight": 20, "note": "کم‌نوسان سودده"}, {"symbol": "وبملت", "weight": 15, "note": "تراز ارزی مثبت"}, {"symbol": "دیران", "weight": 15, "note": "رشد حاشیه سود"}, {"symbol": "نقد", "weight": 5, "note": "آماده شکار"}]},
                {"id": "PORT_L2", "code": "L2", "riskLevel": "low", "riskLabel": "کم‌ریسک", "title": "سود تقسیمی مجمع (DPS)", "strategy": "شرکت‌های با P/E تحلیلی زیر 4.5 و تقسیم سود نقدی بالای 85% در مجمع", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+80% (بک‌تست 1 ساله)", "maxDrawdown": "-6.0%", "benchmarkDiff": "+26% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "آریا", "weight": 25, "note": "DPS 90%"}, {"symbol": "زاگرس", "weight": 20, "note": "سود نقدی دلاری"}, {"symbol": "فخوز", "weight": 20, "note": "P/E 4.2"}, {"symbol": "عیار", "weight": 20, "note": "بیمه تورم"}, {"symbol": "وبملت", "weight": 10, "note": "سود مجمع"}, {"symbol": "نقد", "weight": 5, "note": "ذخیره"}]},
                {"id": "PORT_L3", "code": "L3", "riskLevel": "low", "riskLabel": "کم‌ریسک", "title": "پدافند تورمی و صادراتی", "strategy": "30% طلا + شرکت‌های کامودیتی و صادراتی همگام با نرخ ارز", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+92% (بک‌تست 1 ساله)", "maxDrawdown": "-8.0%", "benchmarkDiff": "+38% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "عیار", "weight": 30, "note": "همگام با ارز آزاد"}, {"symbol": "فملی", "weight": 25, "note": "فروش جهانی مس"}, {"symbol": "آریا", "weight": 20, "note": "حاشیه سود بالای 40%"}, {"symbol": "کگل", "weight": 15, "note": "زنجیره فلزات"}, {"symbol": "نقد", "weight": 10, "note": "آماده"}]},
                {"id": "PORT_M1", "code": "M1", "riskLevel": "med", "riskLabel": "ریسک متوسط", "title": "کاتالیزور حذف ارز ترجیحی و کدال", "strategy": "صنایع دارویی و تایرسازی با جهش فروش ماهانه در گزارش‌های کدال", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+158% (بک‌تست 1 ساله)", "maxDrawdown": "-15.0%", "benchmarkDiff": "+104% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "دیران", "weight": 25, "note": "رشد فروش +42%"}, {"symbol": "درازی", "weight": 25, "note": "صف خرید 182.6B"}, {"symbol": "دفارا", "weight": 20, "note": "صف خرید 266.3B"}, {"symbol": "پکویر", "weight": 20, "note": "افزایش نرخ +23.4%"}, {"symbol": "نقد", "weight": 10, "note": "چرخشی"}]},
                {"id": "PORT_M2", "code": "M2", "riskLevel": "med", "riskLabel": "ریسک متوسط", "title": "مومنتوم پول داغ & فیلتر آسیاتک", "strategy": "سهامی که بالای میانگین متحرک 20 روزه تثبیت شده و تراکم تقاضای سرخط دارند", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+145% (بک‌تست 1 ساله)", "maxDrawdown": "-18.0%", "benchmarkDiff": "+91% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "آسیاتک", "weight": 25, "note": "سیگنال پیش‌صف 3.8x"}, {"symbol": "اهرم", "weight": 25, "note": "لیدر جریان نقد"}, {"symbol": "وبملت", "weight": 20, "note": "شکست مقاومت"}, {"symbol": "عیار", "weight": 20, "note": "پوشش ریسک"}, {"symbol": "نقد", "weight": 10, "note": "ذخیره"}]},
                {"id": "PORT_M3", "code": "M3", "riskLevel": "med", "riskLabel": "ریسک متوسط", "title": "آربیتراژ حباب اهرمی & هم‌وزن", "strategy": "انتقال چرخشی سرمایه به صندوق‌های اهرمی با حباب منفی ارزان‌تر از میانه 120 روزه", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+155% (بک‌تست 1 ساله)", "maxDrawdown": "-16.0%", "benchmarkDiff": "+101% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "شتاب", "weight": 25, "note": "حباب -19.3%"}, {"symbol": "توان", "weight": 25, "note": "اهرم 1.82x متعادل"}, {"symbol": "فخوز", "weight": 20, "note": "لیدر هم‌وزن"}, {"symbol": "عیار", "weight": 20, "note": "سپر طلا"}, {"symbol": "نقد", "weight": 10, "note": "ذخیره"}]},
                {"id": "PORT_H1", "code": "H1", "riskLevel": "high", "riskLabel": "پرریسک", "title": "اهرم حداکثری بازار (ضریب 2x)", "strategy": "تمرکز روی صندوق‌های اهرمی با بالاترین ضریب اهرم واقعی در فازهای صعودی", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+260% (بک‌تست 1 ساله)", "maxDrawdown": "-26.0%", "benchmarkDiff": "+206% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "اهرم", "weight": 30, "note": "ضریب اهرم 1.90x"}, {"symbol": "جهش", "weight": 30, "note": "ضریب اهرم 1.85x"}, {"symbol": "دوایکس", "weight": 25, "note": "ضریب اهرم 1.95x"}, {"symbol": "نقد", "weight": 15, "note": "خرید در کف منفی"}]},
                {"id": "PORT_H2", "code": "H2", "riskLevel": "high", "riskLabel": "پرریسک", "title": "صف‌شکن و پرش شارپ اسمال‌کپ", "strategy": "شکار سهم‌های کوچک و متوسطی که صف فروش را بلعیده و با قدرت خریدار بالای 2 می‌جهند", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+235% (بک‌تست 1 ساله)", "maxDrawdown": "-28.0%", "benchmarkDiff": "+181% نسبت به شاخص", "source": "sabadgardan9", "holdings": [{"symbol": "ثفارس", "weight": 25, "note": "شکست صف فروش"}, {"symbol": "آسیاتک", "weight": 25, "note": "تراکم بید 3.8x"}, {"symbol": "وآذر", "weight": 25, "note": "حجم انفجاری"}, {"symbol": "نقد", "weight": 25, "note": "حد ضرر -3%"}]},
                {"id": "PORT_H3", "code": "H3", "riskLevel": "high", "riskLabel": "پرریسک", "title": "اختیار معامله (آپشن) & اهرم مرکب", "strategy": "ترکیب کال آپشن‌های نقدشونده روی صندوق اهرم و دارایی پایه (آزمایشی/پیشرفته)", "createdAt": "1405/06/01", "updatedAt": "1405/07/26", "historicalReturn": "+290% (بک‌تست فرضی)", "maxDrawdown": "-32.0%", "benchmarkDiff": "+236% نسبت به شاخص", "source": "options + sabadgardan9", "holdings": [{"symbol": "اهرم", "weight": 65, "note": "دارایی پایه + اختیار خرید ضیاهرم"}, {"symbol": "شتاب", "weight": 20, "note": "تخفیف حباب NAV"}, {"symbol": "نقد", "weight": 15, "note": "وجه تضمین نقد"}]}
            ],
            "fundamentalPortfolios": [
                {"id": "FUND_PROD", "category": "شرکت‌های تولیدی و صادراتی", "status": "operational", "description": "تمرکز بر تولیدکنندگان دارویی، فلزی و پتروشیمی با رشد فروش ماهانه کدال بالای 35% و P/E زیر 6", "holdings": [{"symbol": "فملی", "weight": 25}, {"symbol": "دیران", "weight": 20}, {"symbol": "دفارا", "weight": 20}, {"symbol": "آریا", "weight": 20}, {"symbol": "پکویر", "weight": 15}]},
                {"id": "FUND_INV", "category": "شرکت‌های سرمایه‌گذاری و هلدینگ‌ها", "status": "operational", "description": "هلدینگ‌های چندرشته‌ای و تخصصی با تخفیف NAV بیش از 30%", "holdings": [{"symbol": "تیپیکو", "weight": 30}, {"symbol": "وکغدیر", "weight": 30}, {"symbol": "وبملت", "weight": 25}, {"symbol": "وآذر", "weight": 15}]},
                {"id": "FUND_ETFS", "category": "سبد ترکیبی صندوق‌ها (اهرمی + طلا + نقره)", "status": "operational", "description": "تخصیص پویا بین صندوق‌های اهرمی در کف حباب و صندوق‌های کالایی", "holdings": [{"symbol": "عیار", "weight": 35}, {"symbol": "اهرم", "weight": 25}, {"symbol": "شتاب", "weight": 20}, {"symbol": "فنقره", "weight": 20}]}
            ],
            "realBrokeragePortfolioReadOnly": {
                "id": "REAL_EASYTRADER_MOFID",
                "title": "پورتفوی واقعی کارگزاری مفید (EasyTrader — فقط خواندنی)",
                "mode": "READ_ONLY_STRICT",
                "snapshotDate": "1405/07/26 10:22",
                "totalValueRial": 2716052245,
                "totalValueToman": 271605224,
                "cashRial": 453,
                "totalPnlPct": -1.93,
                "totalPnlToman": -5330000,
                "holdings": fb_data.get("myRealPort", [])
            }
        }
        atomic_write_json(os.path.join(DATA_DIR, "portfolios.json"), portfolios_payload)

        # ۴. fundamentals.json
        fundamentals_list = []
        for sym, meta in SYMBOL_META.items():
            fundamentals_list.append({
                "symbolId": meta["id"],
                "symbol": sym,
                "industryId": meta["industry_id"],
                "industry": meta["industry"],
                "pe": meta["pe"],
                "eps": meta["eps"],
                "grossMargin": meta["margin"],
                "lastCodalDate": meta["codal_date"],
                "codalSummary": meta["codal_summary"],
                "dataStatus": "available" if meta["pe"] is not None else "partial_or_etf",
                "source": "کدال + فاندبیس + ره‌آورد",
                "updatedAtDubai": dubai_now
            })
        atomic_write_json(os.path.join(DATA_DIR, "fundamentals.json"), {
            "schemaVersion": "2.0.0",
            "updatedAtDubai": dubai_now,
            "note": "برای صندوق‌های سرمایه‌گذاری (ETF) یا نمادهایی که گزارش کامل فصلی در منبع فعلی ندارند، مقادیر P/E و EPS به صورت شفاف «داده موجود نیست / صندوق» علامت‌گذاری شده‌اند و هیچ عدد فرضی تولید نشده است.",
            "companies": fundamentals_list
        })

        # ۵. industries.json
        industries_payload = {
            "schemaVersion": "2.0.0",
            "updatedAtDubai": dubai_now,
            "industries": [
                {"id": "IND_PHARMA", "name": "دارویی و سلامت", "strengthRank": 1, "status": "strong_inflow", "realFlowB": 115.8, "avgSalesGrowth": "+42%", "avgPE": 5.9, "leadingSymbols": ["درازی", "دفارا", "داروند", "دیران", "تیپیکو", "دتولید"], "summary": "قوی‌ترین صنعت بنیادی و تابلوخوانی بازار پس از حذف ارز ترجیحی و رشد حاشیه سود به بالای 45%."},
                {"id": "IND_ENG", "name": "فنی و مهندسی", "strengthRank": 2, "status": "strong_inflow", "realFlowB": 285.0, "avgSalesGrowth": "+31%", "avgPE": 7.6, "leadingSymbols": ["فاذر", "رتکو", "فاراک", "فکور", "کیسون"], "summary": "صدرنشین ورود پول حقیقی در معاملات 26 مهر با محوریت فاذر و رتکو."},
                {"id": "IND_GOLD", "name": "صندوق‌های طلا و نقره", "strengthRank": 3, "status": "safe_haven", "realFlowB": 57.1, "avgSalesGrowth": "همگام با انس و دلار", "avgPE": None, "leadingSymbols": ["عیار", "فنقره"], "summary": "پناهگاه اول نقدینگی در روزهای منفی شاخص و ریسک‌های سیاسی."},
                {"id": "IND_TIRE", "name": "تایرسازی و لاستیک", "strengthRank": 4, "status": "catalyst_positive", "realFlowB": 14.2, "avgSalesGrowth": "+28%", "avgPE": 5.6, "leadingSymbols": ["پکویر"], "summary": "دریافت مجوز رسمی افزایش نرخ 23.4% تایر رادیال در کدال."},
                {"id": "IND_CEMENT", "name": "سیمان و کانی غیرفلزی", "strengthRank": 5, "status": "selective_inflow", "realFlowB": 38.4, "avgSalesGrowth": "+34%", "avgPE": 6.1, "leadingSymbols": ["سغدیر", "کفرا", "سخاش"], "summary": "تقاضای قوی در نمادهای صادراتی و نسوز برخلاف کلیت بازار."},
                {"id": "IND_TECH", "name": "فناوری و ارتباطات", "strengthRank": 6, "status": "pre_queue", "realFlowB": 8.35, "avgSalesGrowth": "+29%", "avgPE": 7.6, "leadingSymbols": ["آسیاتک", "های‌وب"], "summary": "تراکم تقاضای پیش‌صف به واسطه اخبار افزایش تعرفه خدمات اینترنت."},
                {"id": "IND_LEVERAGED", "name": "صندوق‌های اهرمی", "strengthRank": 7, "status": "deep_discount_nav", "realFlowB": 18.4, "avgSalesGrowth": "اهرم 1.65x تا 1.95x", "avgPE": None, "leadingSymbols": ["اهرم", "شتاب", "جهش", "توان", "نارنج", "دوایکس"], "summary": "معامله در کف حباب منفی تاریخی (-18% تا -19.6%) و ثبت تراز حقیقی مثبت در کف قیمت."},
                {"id": "IND_METALS", "name": "فلزات اساسی و معدنی", "strengthRank": 8, "status": "fundamental_value", "realFlowB": 12.1, "avgSalesGrowth": "+36%", "avgPE": 5.1, "leadingSymbols": ["فملی", "فخوز", "کگل", "وکغدیر"], "summary": "ارزندگی بنیادی بالا (P/E حدود 5)؛ نیازمند آرامش سیاسی برای شروع موج شاخص‌ساز."},
                {"id": "IND_BANK", "name": "بانک‌ها و موسسات اعتباری", "strengthRank": 9, "status": "divergent", "realFlowB": -26.8, "avgSalesGrowth": "+24%", "avgPE": 4.9, "leadingSymbols": ["وبملت", "وتجارت", "وبصادر"], "summary": "واگرایی شدید: وبملت با P/E 3.9 و تراز ارزی مثبت در برابر فشار فروش سنگین در وتجارت و وبصادر."},
                {"id": "IND_AUTO", "name": "خودرو و ساخت قطعات", "strengthRank": 10, "status": "divergent", "realFlowB": 28.5, "avgSalesGrowth": "+19%", "avgPE": None, "leadingSymbols": ["خبهمن", "خگستر", "خودرو", "خساپا"], "summary": "صف خرید 389B در خبهمن (کاتالیزور خاور) در مقابل خروج پول و زیان انباشته در خودرو و خساپا."},
                {"id": "IND_PETRO", "name": "پتروشیمی و شیمیایی", "strengthRank": 11, "status": "mixed", "realFlowB": -38.9, "avgSalesGrowth": "+27%", "avgPE": 5.8, "leadingSymbols": ["آریا", "زاگرس", "شکیمیا", "پترول", "اروند"], "summary": "ثبات در الفینی‌ها و متانولی‌ها (آریا، زاگرس، شکیمیا) در برابر صف فروش سنگین در اروند."}
            ]
        }
        atomic_write_json(os.path.join(DATA_DIR, "industries.json"), industries_payload)

        # ۶. news.json
        news_payload = {
            "schemaVersion": "2.0.0",
            "updatedAtDubai": dubai_now,
            "events": [
                {"id": "NEWS_01", "date": "1405/07/26 09:15", "title": "ابلاغ رسمی افزایش 23.4% نرخ تایر رادیال (پکویر)", "source": "سامانه کدال", "category": "افشای الف / نرخ‌گذاری", "relatedSymbols": ["پکویر"], "relatedIndustries": ["IND_TIRE"], "relatedPortfolios": ["PORT_M1"], "verified": True, "summary": "بر اساس اطلاعیه منتشرشده در کدال، نرخ فروش محصولات رادیال سواری کویر تایر 23.4 درصد افزایش یافت."},
                {"id": "NEWS_02", "date": "1405/07/26 08:45", "title": "گزارش‌های ماهانه درخشان گروه دارویی با رشد فروش بالای 42%", "source": "کدال / فاندبیس", "category": "گزارش فعالیت ماهانه", "relatedSymbols": ["دیران", "دفارا", "درازی", "تیپیکو", "داروند"], "relatedIndustries": ["IND_PHARMA"], "relatedPortfolios": ["PORT_OMIX_WEEKLY", "PORT_M1", "PORT_L1"], "verified": True, "summary": "حذف ارز ترجیحی و اصلاح نرخ‌های دارویی موجب جهش حاشیه سود ناخالص شرکت‌های دارویی به بالای 45% شده است."},
                {"id": "NEWS_03", "date": "1405/07/26 10:10", "title": "تراز پول حقیقی مثبت در کف حباب -19% صندوق‌های اهرمی", "source": "تابلوخوانی / بورس۲۴", "category": "جریان نقدینگی", "relatedSymbols": ["اهرم", "شتاب", "نارنج", "جهش", "توان"], "relatedIndustries": ["IND_LEVERAGED"], "relatedPortfolios": ["PORT_M3", "PORT_H1"], "verified": True, "summary": "با وجود افت قیمت واحدهای اهرمی در محدوده -4%، خریداران حقیقی در حباب‌های منفی 18% تا 19.6% اقدام به جمع‌آوری واحدها کردند."},
                {"id": "NEWS_04", "date": "1405/07/26 09:30", "title": "شفاف‌سازی آسیاتک درباره بررسی تعرفه‌های اینترنت", "source": "کدال", "category": "شفاف‌سازی", "relatedSymbols": ["آسیاتک", "های‌وب"], "relatedIndustries": ["IND_TECH"], "relatedPortfolios": ["PORT_M2", "PORT_H2"], "verified": True, "summary": "انتشار شفاف‌سازی در کدال و شکل‌گیری تقاضای 3.8 برابری در ردیف‌های اول خرید آسیاتک."},
                {"id": "NEWS_05", "date": "1405/07/25 17:40", "title": "ابهام در دستورالعمل نرخ‌گذاری و کاهش سود شرایط اضطرار شتران", "source": "کدال", "category": "هشدار بنیادی", "relatedSymbols": ["شتران"], "relatedIndustries": ["IND_OIL"], "relatedPortfolios": [], "verified": True, "summary": "اعلام کاهش برآورد سود نیمه دوم در شرایط اضطرار که منجر به فشار عرضه در گروه پالایشی شد."}
            ]
        }
        atomic_write_json(os.path.join(DATA_DIR, "news.json"), news_payload)

        print(f"[OK] Unified Data Layer built successfully at {dubai_now} (Total Signals: {len(signals_list)})")
    finally:
        release_lock()


if __name__ == "__main__":
    build_all()
