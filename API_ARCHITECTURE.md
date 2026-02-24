# 🚀 Pishro Architecture - Backend API + Bot

## 📊 **نیاز سازنده:**

```
پروژه قدیم:  Bot ← Handlers ← Database
│
پروژه جدید:
          ┌─────────────────────────────────┐
          │    FastAPI Backend (main_api)   │
          │   /api/v1/users                 │
          │   /api/v1/investments           │
          │   /api/v1/transactions          │
          └──────────────┬──────────────────┘
                         │ HTTP Client
                    ┌────┴────┐
                    │          │
              ┌─────▼──┐   ┌──▼───────┐
              │  Bot   │   │ Website  │
              │TeleBot │   │ (React)  │
              └────────┘   └──────────┘
                         ▲
                         │
              ┌─────────────────────┐
              │  Mobile App (RN)    │
              │  Desktop App        │
              └─────────────────────┘
              
    همه استفاده می‌کنند از: API Endpoints
```

---

## 🔧 **نصب Dependencies**

```bash
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate

# اضافهٔ httpx برای HTTP client
pip install httpx

# بقیه الاکنون نصب است
```

---

## 🚀 **استفاده:**

### **روش 1: API + Bot جدا**

```bash
# Terminal 1: شروع API
source venv/bin/activate
python3 main_api.py

# شروع می‌شود: http://localhost:8000
# Docs: http://localhost:8000/docs
```

```bash
# Terminal 2: شروع Bot
source venv/bin/activate
python3 run_bot.py

# Bot استفاده می‌کند از API: localhost:8000
```

### **روش 2: هر دو بندهم**

```bash
# نسخهٔ جدید run_servers.sh با API
bash run_servers.sh
# گزینهٔ جدید برای "API + Bot + Webhook"
```

---

## 📡 **API Endpoints**

### **Users**
```
GET    /api/v1/users                    # همهٔ کاربران
GET    /api/v1/users/{user_id}         # کاربر خاص
GET    /api/v1/users/telegram/{id}     # با Telegram ID
GET    /api/v1/users/phone/{phone}     # با شماره
GET    /api/v1/users/{user_id}/stats   # آمار کاربر
POST   /api/v1/users                    # ایجاد کاربر
PUT    /api/v1/users/{user_id}         # ویرایش کاربر
DELETE /api/v1/users/{user_id}         # حذف کاربر
```

### **Investments**
```
GET    /api/v1/investments              # همهٔ سرمایه‌گذاری‌ها
GET    /api/v1/investments/{id}        # سرمایهٔ خاص
GET    /api/v1/investments/{id}/details # تفاصیل کامل
POST   /api/v1/investments              # ایجاد سرمایهٔ جدید
PUT    /api/v1/investments/{id}        # ویرایش سرمایه
DELETE /api/v1/investments/{id}        # حذف سرمایه
```

### **Transactions**
```
GET    /api/v1/transactions             # همهٔ تراکنش‌ها
GET    /api/v1/transactions/{id}       # تراکنش خاص
POST   /api/v1/transactions             # ایجاد تراکنش
DELETE /api/v1/transactions/{id}       # حذف تراکنش
```

---

## 💻 **مثال‌های استفاده:**

### **Python Client**
```python
from app.services.api_client import api_client

# دریافت کاربر
user = await api_client.get_user(1)

# ایجاد سرمایهٔ جدید
inv = await api_client.create_investment(
    investor_id=1,
    investment_type="fixed_rate",
    initial_amount=1_000_000,
    rate=12.5
)

# دریافت آمار
stats = await api_client.get_user_stats(1)
```

### **cURL**
```bash
# دریافت کاربر
curl -X GET "http://localhost:8000/api/v1/users/1"

# ایجاد سرمایهٔ جدید
curl -X POST "http://localhost:8000/api/v1/investments" \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 1,
    "investment_type": "fixed_rate",
    "initial_amount": 1000000,
    "rate": 12.5
  }'

# دریافت آمار
curl -X GET "http://localhost:8000/api/v1/users/1/stats"
```

### **JavaScript/React**
```javascript
const API_URL = "http://localhost:8000";

// دریافت کاربر
async function getUser(userId) {
  const res = await fetch(`${API_URL}/api/v1/users/${userId}`);
  return res.json();
}

// ایجاد سرمایهٔ جدید
async function createInvestment(data) {
  const res = await fetch(`${API_URL}/api/v1/investments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}
```

---

## 📁 **ساختار فایل‌های جدید**

```
pishro-bot/
├── app/api/                       # ✨ جدید - API Layer
│   ├── schemas.py                 # Pydantic models
│   ├── users.py                   # User endpoints
│   ├── investments.py             # Investment endpoints
│   └── transactions.py            # Transaction endpoints
├── app/services/
│   └── api_client.py              # ✨ جدید - Bot ← API Client
├── main_api.py                    # ✨ جدید - FastAPI Server
├── run_bot.py                     # Bot uses API Client
└── ...
```

---

## 🔄 **Bot Handler Example (جدید)**

```python
# app/handlers/investor.py

from app.services.api_client import api_client

@router.callback_query(F.data == "my_investments")
async def show_investments(query: types.CallbackQuery):
    """Show user's investments using API."""
    telegram_id = query.from_user.id
    
    try:
        # دریافت اطلاعات از API
        user = await api_client.get_user_by_telegram(telegram_id)
        investments = await api_client.get_user_investments(user['id'])
        
        # ساختن پیام
        text = f"💰 سرمایه‌گذاری‌های شما:\n\n"
        for inv in investments:
            text += f"• {inv['description']}\n"
            text += f"  مبلغ: {inv['initial_amount']:,} ریال\n"
            text += f"  بازدهی: {inv['roi_percentage']:.2f}%\n\n"
        
        await query.message.edit_text(text)
    except Exception as e:
        await query.message.answer(f"❌ خطا: {e}")
```

---

## 🎯 **مزایا:**

✅ **Separation of Concerns** - Backend جدا، Bot جدا
✅ **Scalability** - می‌توانی بیش از یک Bot اضافه کنی
✅ **Reusability** - API می‌تواند برای Website، Mobile، etc استفاده شود
✅ **Maintainability** - تغییرات Backend رو می‌تونی بدون تغییر Bot انجام بدی
✅ **Testing** - آسان‌تر تست کنی
✅ **Documentation** - Swagger Docs خودکار در /docs

---

## 📝 **نکات:**

1. Bot requests می‌فرستد به API بجای مستقیم Database
2. API endpoints تمام Logic ها رو handle می‌کنند
3. ربات تنها User Interface است
4. دیگر برنامه‌ها می‌تونن از همین API استفاده کنند

**Result: Truly Dynamic System!** 🎉

