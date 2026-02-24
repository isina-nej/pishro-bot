# 🚀 Pishro Bot - سیستم مدیریت مکمل

## ✨ **ویژگی‌های جدید**

### 1️⃣ **Webhook Server + Dashboard**
```
🌐 Webhook Server (FastAPI)
   └─ پورت: 8000
   └─ Dashboard: http://localhost:8000
   └─ API: RESTful Endpoints

📊 Dashboard آنلاین
   └─ مشاهدهٔ لاگ‌های Real-Time
   └─ کنترل Bot (شروع/متوقف)
   └─ آمار و نمودار
   └─ دانلود لاگ‌های کامل
```

### 2️⃣ **Ngrok Integration**
```
🔗 Expose local server to internet
   └─ برای استفادهٔ Webhook بدون VPS
   └─ URL عمومی برای Telegram
```

### 3️⃣ **Terminal Dashboard**
```
🎯 مشاهدهٔ لاگ‌های رنگی
⚐ وضعیت فرآیندها
📝 دستورات سریع
```

---

## 📋 **دستورات استفاده**

### **گزینهٔ 1: یک درجا (All-in-One)**

```bash
# شروع Polling Bot + Webhook Dashboard
cd /home/sina/Documents/project/pishro-bot
bash run_servers.sh
```

سپس شماره `2` را انتخاب کنید.

**خروجی:**
```
🤖 درحال شروع Bot...
✅ بات شروع شد! (PID: 6920)

🌐 درحال شروع Webhook Server...
✅ Webhook Server شروع شد (PID: 6925)

🎉 هر دو سرور در حال اجرا هستند!
   • Bot: Polling Mode
   • Dashboard: http://localhost:8000
```

---

### **گزینهٔ 2: Webhook + Ngrok**

```bash
# نیاز به نصب Ngrok (یک بار)
# Ubuntu: sudo apt install ngrok
# MacOS: brew install ngrok

cd /home/sina/Documents/project/pishro-bot
bash setup_webhook_ngrok.sh
```

**نتیجه:**
```
✅ Webhook Server شروع شد
✨ Ngrok اتصال برقرار کرد
🌍 آدرس عمومی: https://xxxx-xx-xxx-xxx.ngrok.io
```

این آدرس را کپی کنید و در تنظیمات Telegram Webhook استفاده کنید.

---

### **گزینهٔ 3: مشاهدهٔ Dashboard**

```bash
cd /home/sina/Documents/project/pishro-bot
bash dashboard.sh
```

یا در مرورگر:
```
http://localhost:8000
```

---

### **گزینهٔ 4: مشاهدهٔ لاگ‌ها**

```bash
# پوسته‌ای
./dashboard.sh

# بصورت پیوسته
tail -f logs/bot.log

# جستجوی خاص
grep "ERROR" logs/bot.log
```

---

### **گزینهٔ 5: متوقف کردن**

```bash
# متوقف کردن همه
bash run_servers.sh
# انتخاب: 5

# یا دستی
pkill -f "run_bot.py"
pkill -f "webhook_server.py"
pkill -f "ngrok"
```

---

## 🎯 **سناریو‌های مختلف**

### **سناریو 1: تنها Polling (ساده)**
```bash
bash start_bot.sh
tail -f logs/bot.log
```

### **سناریو 2: Polling + Web Dashboard**
```bash
bash run_servers.sh
# انتخاب: 2

# سپس مرورگر:
# http://localhost:8000
```

### **سناریو 3: Webhook برای تولید محصول**
```bash
# 1. Setup Ngrok
bash setup_webhook_ngrok.sh

# 2. Update Telegram Bot Settings
# Using Bot API: setWebhookInfo

# 3. Monitor via Dashboard
# http://localhost:8000
```

### **سناریو 4: Hybrid (Polling + Webhook)**
```bash
# شروع Polling
bash start_bot.sh

# در ترمینال دوم، شروع Webhook
python3 webhook_server.py

# مشاهدهٔ هر دو
bash dashboard.sh
```

---

## 📊 **Dashboard ویژگی‌ها**

### **صفحهٔ اصلی**
```
╔════════════════════════════════════════════════════════════════╗
║  🤖 Pishro Bot Dashboard                                      ║
║                                                                ║
║  Status: ✓ Active         Time: 16:30:45                     ║
║                                                                ║
║  [▶️ Start] [⏹️ Stop] [🔄 Refresh]                             ║
╚════════════════════════════════════════════════════════════════╝

📋 Live Logs (100+ entries)
├─ 16:30:22 - INFO - Starting bot...
├─ 16:30:23 - INFO - Database initialized
├─ 16:30:25 - INFO - Bot ready to receive updates
└─ ...
```

### **Sidebar**
```
📊 آمار
  • Total Logs: 247
  • Errors: 2
  • Warnings: 5

🎮 کنترل
  • [🗑️ Clear Logs]
  • [⬇️ Download]
  • [🔄 Auto Refresh: ON]
```

---

## 🔧 **تنطیم‌های پیشرفتهٔ**

### **تغییر پورت Webhook**
```python
# در webhook_server.py
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,  # تغییر این
        log_level="info"
    )
```

### **فعال‌کردن HTTPS برای Webhook**
```bash
# نصب mkcert برای SSL
sudo apt install mkcert

# ایجاد سرتیفیکت
mkcert localhost
mkcert -install

# استفاده در Webhook
uvicorn webhook_server:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### **استفادهٔ Domain سفارشی**
```bash
# با Ngrok
ngrok http 8000 -subdomain=pishro-webhook

# خروجی:
# https://pishro-webhook.ngrok.io
```

---

## 📱 **مدیریت لاگ‌ها**

### **دیدن لاگ‌های Real-Time**
```bash
tail -f logs/bot.log

# با رنگ‌ها (grep)
tail -f logs/bot.log | grep -E "ERROR|INFO|WARNING"
```

### **جستجو در لاگ‌ها**
```bash
# خطاهای امروز
grep "$(date +%Y-%m-%d)" logs/bot.log | grep "ERROR"

# لاگ‌های خاص
grep "telegram" logs/bot.log

# شمار
wc -l logs/bot.log
```

### **پاک‌کردن لاگ‌های قدیمی**
```bash
# از Dashboard
# یا دستی:
> logs/bot.log
```

### **بکاپ لاگ‌ها**
```bash
cp logs/bot.log logs/bot.log.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 🐛 **رفع مشاکل**

### **مشکل: Port 8000 در حال استفاده است**
```bash
# پیدا کردنِ فرآیند
lsof -i :8000

# تغییر پورت
python3 webhook_server.py --port=8001
```

### **مشکل: Bot نمی‌کند جواب**
```bash
# بررسی Status
ps aux | grep run_bot.py

# چک کردن لاگ‌ها
tail -50 logs/bot.log

# باز شروع
bash start_bot.sh
```

### **مشکل: Webhook دریافت نمی‌کند**
```bash
# بررسی Ngrok
tail logs/ngrok.log

# بررسی Firewall
sudo ufw allow 8000

# تست از Terminal
curl http://localhost:8000/health
```

---

## 📈 **نکات مهم**

✅ **بهترین روش‌ها:**
- از `run_servers.sh` برای شروع استفاده کنید
- Dashboard را باز نگاه دارید برای نظارت
- لاگ‌ها را منظم بررسی کنید
- از Ngrok برای Public URL استفاده کنید

⚠️ **احتیاط:**
- پورت 8000 را در Firewall باز کنید
- شماره‌های حساس را در .env نگاه دارید
- لاگ‌های حاوی توکن را حذف کنید

---

## 🔗 **فایل‌های مربوطه**

```
📂 Project Root
├─ run_servers.sh          ← مدیر سرور‌ها (MAIN)
├─ setup_webhook_ngrok.sh  ← Webhook + Ngrok
├─ dashboard.sh            ← Terminal Dashboard
├─ webhook_server.py       ← FastAPI Server
├─ start_bot.sh            ← شروع Bot
├─ stop_bot.sh             ← متوقف Bot
└─ logs/
   ├─ bot.log              ← لاگ‌های Bot
   ├─ webhook.log          ← لاگ‌های Webhook
   └─ ngrok.log            ← لاگ‌های Ngrok
```

---

## 🎯 **برای شروع سریع**

```bash
cd /home/sina/Documents/project/pishro-bot

# گزینهٔ 1: تنها Bot
bash start_bot.sh

# گزینهٔ 2: Bot + Dashboard
bash run_servers.sh
# انتخاب: 2

# گزینهٔ 3: مشاهدهٔ لاگ‌ها
bash dashboard.sh
```

**بس! تمام آماده است!** 🎉

---

**پرسش‌های بیشتر:** 📞 support@pishro.ir
**توثیق:** https://github.com/pishro-bot/docs

