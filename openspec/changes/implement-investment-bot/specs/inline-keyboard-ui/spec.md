## ADDED Requirements

### Requirement: Main Menu with Role-Specific Options
System SHALL display a hierarchical main menu adapted to user role, using inline keyboard buttons instead of requiring text input.

#### Scenario: Investor main menu display
- **WHEN** investor clicks /start or requests main menu
- **THEN** system displays:
  ```
  سلام! خوش آمدید
  چه کاری می‌تونم برای شما کنم؟
  
  [وضعیت سرمایه من]
  [تاریخچه تراکنش‌ها]
  [تنظیمات]
  [تماس با پشتیبانی]
  ```

#### Scenario: Accountant main menu display
- **WHEN** accountant clicks /start
- **THEN** menu shows:
  ```
  سلام حسابدار!
  
  [ثبت تراکنش جدید]
  [جستجو سرمایه‌گذار]
  [ویرایش تراکنش]
  [تاریخچه تراکنش‌ها]
  [خروج]
  ```

#### Scenario: Admin main menu display
- **WHEN** admin clicks /start
- **THEN** menu shows all options plus admin-specific:
  ```
  سلام دکتر!
  
  [بروزرسانی سود و دارایی]
  [مدیریت کاربران]
  [گزارشات]
  [تنظیمات سیستم]
  [خروج]
  ```

### Requirement: Callback Query Routing for Button Actions
Each inline button SHALL trigger a callback query routed to appropriate handler function.

#### Scenario: Portfolio status button handler
- **WHEN** investor clicks "وضعیت سرمایه من"
- **THEN** callback routed to: `handlers.investor_portfolio_status`
- **AND** returns portfolio display without user needing to type anything

#### Scenario: Nested menu navigation via buttons
- **WHEN** admin clicks "مدیریت کاربران" → submenu appears:
  ```
  [اضافه کردن کاربر جدید]
  [حذف کاربر]
  [تغییر نقش]
  [بازگشت]
  ```

### Requirement: Transaction Type Selection via Inline Pills
When recording transactions, system presents transaction types as inline buttons instead of numbered list.

#### Scenario: Transaction type selection
- **WHEN** accountant clicks "ثبت تراکنش جدید"
- **THEN** system asks investor selection, then shows:
  ```
  نوع تراکنش را انتخاب کنید:
  
  [➕ واریز][➖ برداشت]
  [💰 سود][🔴 فسخ قرارداد]
  ```
- **WHEN** accountant clicks "➕ واریز"
- **THEN** flow moves to amount input

### Requirement: Numeric Input Validation with Inline Guidance
For amounts and dates, system provides inline guidance (examples, allowed formats) and validates input.

#### Scenario: Amount input with example
- **WHEN** system asks for transaction amount
- **THEN** message shows:
  ```
  مبلغ تراکنش را وارد کنید:
  (مثال: 500000000 یا 5.5e8)
  
  [پاک کردن] [بازگشت]
  ```
- **WHEN** user enters invalid input (e.g., "five million")
- **THEN** system rejects and re-prompts with error

#### Scenario: Jalali date picker interface
- **WHEN** system asks for transaction date
- **THEN** displays month/day selection:
  ```
  سال: 1402
  [◀ 1401][1402][1403 ▶]
  
  ماه: فروردین
  [◀]][فروردین][اردیبهشت][خرداد]...[اسفند][▶]
  
  روز: 23
  [◀ ۲۲][۲۳][۲۴ ▶]
  
  [تایید][بازگشت]
  ```

### Requirement: Confirmation Screen Before Final Commit
Before saving transactions, system shows comprehensive review via inline-formatted text (not button-based).

#### Scenario: Transaction confirmation review
- **WHEN** accountant completes transaction input and clicks confirm
- **THEN** system shows review modal:
  ```
  📋 بررسی ثبت تراکنش
  ━━━━━━━━━━━━━━━━━━━━━━
  سرمایه‌گذار: احمد علی
  شماره تماس: 09121234567
  ━━━━━━━━━━━━━━━━━━━━━━
  نوع تراکنش: ➕ واریز سرمایه
  مبلغ: 500,000,000 تومان
  تاریخ: فروردین 23, 1402
  توضیح: بخش دوم هولد
  ━━━━━━━━━━━━━━━━━━━━━━
  موجودی فعلی: 1,120,000,000
  موجودی بعد از تراکنش: 1,620,000,000
  
  [✅ تایید و ثبت][❌ لغو و ویرایش]
  ```

### Requirement: Pagination for Long Lists
When displaying lists (investors, transactions, history) exceeding 5-10 items, include Previous/Next navigation buttons.

#### Scenario: Transaction history pagination
- **WHEN** investor has 25 transactions and requests history
- **THEN** system displays first 10:
  ```
  📜 تاریخچه تراکنش‌ها
  ━━━━━━━━━━━━━━━━━━
  1. فروردین 23 | واریز | +500M | بخش دوم هولد
  2. فروردین 1  | سود  | +80M  | سود فروردین
  ...
  10. فروردین 1 | واریز | +1B   | سرمایه اولیه
  
  صفحه 1 از 3
  [◀ قبلی][بعدی ▶]
  ```
- **WHEN** investor clicks "بعدی"
- **THEN** next 10 items displayed with updated page indicator

### Requirement: Search Interface with Inline Suggestions
When searching for investors by name/phone, present results as clickable buttons.

#### Scenario: Investor search by name
- **WHEN** accountant clicks "جستجو سرمایه‌گذار" and enters "علی"
- **THEN** system displays matching results as buttons:
  ```
  نتایج جستجو برای "علی":
  
  [👤 علی احمدی | 09121234567]
  [👤 علی محمدی | 09129876543]
  [👤 علی رضائی | 09125551234]
  
  [جستجوی جدید][بازگشت]
  ```

#### Scenario: Single match auto-selects
- **WHEN** search returns only one exact match
- **THEN** system auto-selects investor and proceeds to transaction entry (no extra button click needed)

### Requirement: Back/Cancel Navigation in All Workflows
Every multi-step flow includes a "بازگشت" (Back) and "لغو" (Cancel) button at each step.

#### Scenario: User cancels mid-transaction
- **WHEN** accountant recording transaction is at "amount" step
- **WHEN** accountant clicks "لغو"
- **THEN** entire transaction form aborted; returns to main menu
- **AND** no partial data saved

### Requirement: Inline Emojis for Visual Clarity  
Transaction types and status indicators use consistent emoji to improve visual scanning.

#### Scenario: Visual transaction type indicators
- **WHEN** displaying transactions
- **THEN** consistent emoji used:
  - ➕ for deposits
  - ➖ for withdrawals
  - 💰 for dividends
  - 🔴 for cancellations
  - ✅ for confirmed
  - ⏳ for pending

### Requirement: Responsive Button Layout
Buttons SHALL arrange adaptively based on text length; avoid overflow or truncation.

#### Scenario: Long button text wrapped
- **WHEN** button label is long (e.g., "بروزرسانی سود و دارایی برای ماه فروردین")
- **THEN** Telegram auto-wraps text within button; readable on mobile
- **NO truncation** like "بروزرسانی سود و دا..."

### Requirement: Disable Buttons During Processing
Buttons are disabled while processing to prevent double-clicks and race conditions.

#### Scenario: Button disabled during transaction confirmation
- **WHEN** accountant clicks "تایید و ثبت"
- **THEN** both buttons greyed out/disabled: "درحال پردازش..."
- **WHEN** database save completes
- **THEN** button re-enabled with "✅ تراکنش ثبت شد" confirmation message
