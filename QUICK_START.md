# ⚡ **شروع سریع - Quick Start Guide**

> تقریبا **۲ دقیقه** برای داشتن ربات کاملا کاری!

## 🎯 **5 مرحله ساده**

### **۱. فعلسازی محیط**
```bash
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate
```

### **۲. تایید .env**
```bash
# باید این خط وجود داشته باشد:
nano .env
# BOT_TOKEN=8463718353:AAFd2V1NWZ1NXXX... (داخل)
```

### **۳. شروع ربات + Webhook**
```bash
bash run_servers.sh
# رقم 2 انتخاب کن (Bot + Webhook)
```

### **۴. باز کردن داشبورد**
```
مرورگر: http://localhost:8000
```

### **۵. تست با تلگرام**
```
عکس ربات: @PishroBot_Support
/start کن و تست کن!
```

---

## 🎮 دستورات سریع

| دستور | نتیجه |
|-------|-------|
| `bash start_bot.sh` | تنها ربات |
| `bash run_servers.sh` → 2 | ربات + Dashboard |
| `bash setup_webhook_ngrok.sh` | Webhook عمومی |
| `bash stop_bot.sh` | متوقف کردن |
| `bash dashboard.sh` | مشاهدهٔ لاگ‌ها |

---

## 🔧 مشکلات معمول

### ❌ `BOT_TOKEN` پیدا نشد
```bash
echo "BOT_TOKEN=8463718353:AAFd2V1NWZ1NXXX" >> .env
```

### ❌ Port 8000 اشغال است
```bash
lsof -i :8000
kill -9 <PID>
```

### ❌ دیتابیس Lock شده
```bash
rm pishro_bot.db-wal pishro_bot.db-shm
bash start_bot.sh
```

---

## 🌟 Dashboard دسترسی

```
🌐 Web Dashboard:     http://localhost:8000
📡 Webhook Server:    http://localhost:8000/webhook/telegram
🏥 Health Check:      http://localhost:8000/health
📝 API Logs:          http://localhost:8000/api/logs
```

---

## 📊 Dashboard ویژگی‌ها

✅ **Real-Time Logs Viewer**
✅ **Bot Start/Stop Control**  
✅ **Log Download & Clear**
✅ **Process Status Monitor**
✅ **Error Count Tracker**

---

## 🎓 بعدی چه؟

1. ✅ **Basic Mode**: `bash start_bot.sh` → تمام!
2. 🎯 **Advanced Mode**: `bash run_servers.sh` → Dashboard فعل!
3. 🚀 **Production Mode**: `bash setup_webhook_ngrok.sh` → Online!

---

## 💡 نکات سریع

- 🟢 ربات **polling mode** اجرا می‌شود (به سرور نیاز ندارد)
- 🔵 Webhook **اختیاری** است (برای Production)
- 🟡 Ngrok URL هر ۲ ساعت **تغییر می‌کند** (اگر free)
- 🟣 لاگ‌ها در `logs/` ذخیره می‌شوند

---

## 🚀 معمول ترین سناریوهای استفاده

### **سناریو ۱: تنها تست (۵۰ ثانیه)**
```bash
bash start_bot.sh
tail -f logs/bot.log
# عالی! ربات اجرا است 🎉
```

### **سناریو ۲: تست کامل (۲ دقیقه)**
```bash
bash run_servers.sh
# انتخاب: 2
# مرورگر: http://localhost:8000
# تمام! ✨
```

### **سناریو ۳: تولید محصول (۳ دقیقه)**
```bash
bash setup_webhook_ngrok.sh
# کپی URL و استفاده در Telegram
# Dashboard: http://localhost:8000
# کامل! 🚀
```

---

**حالا دارید آن را انجام دهید!** 🎉

```bash
cd /home/sina/Documents/project/pishro-bot
bash run_servers.sh
```

