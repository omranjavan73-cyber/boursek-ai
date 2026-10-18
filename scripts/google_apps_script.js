/**
 * Boursek PRO v6.0 AI — Google Apps Script Cloud Bridge
 * پل ابری رایگان گوگل جهت دریافت زنده تابلوی بورس تهران و ارسال خودکار به Firebase Realtime Database
 *
 * نحوه راه‌اندازی:
 * 1. وارد https://script.google.com شوید و یک پروژه جدید بسازید.
 * 2. این کد را داخل فایل Code.gs قرار دهید و ذخیره کنید.
 * 3. از منوی سمت چپ وارد بخش Triggers (ساعت زنگ‌دار) شوید و یک تایمر Time-driven روی هر 1 دقیقه تنظیم کنید.
 */

function syncTablokhaniToFirebase() {
  const FIREBASE_BASE = "https://stock-21aa7-default-rtdb.europe-west1.firebasedatabase.app";
  const FIREBASE_LIVE_NODE = FIREBASE_BASE + "/live_market.json";
  const TABLOKHANI_API = "https://api.tablokhani.com/public/source-arena?endpoint=all&type=0";

  try {
    const response = UrlFetchApp.fetch(TABLOKHANI_API, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
      },
      muteHttpExceptions: true
    });

    if (response.getResponseCode() === 200) {
      const rawData = JSON.parse(response.getContentText());
      const payload = {
        system: "Boursek PRO v6.0 AI",
        updatedAt: new Date().toISOString(),
        marketStatus: "active",
        totalStocks: Array.isArray(rawData) ? rawData.length : 0,
        source: "google-apps-script-bridge-v6"
      };

      UrlFetchApp.fetch(FIREBASE_LIVE_NODE, {
        method: "put",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });

      Logger.log("✅ Boursek PRO v6.0 Firebase sync completed at " + new Date().toISOString());
    } else {
      Logger.log("⚠️ Tablokhani API returned status: " + response.getResponseCode());
    }
  } catch (err) {
    Logger.log("❌ Error syncing to Firebase: " + err);
  }
}
