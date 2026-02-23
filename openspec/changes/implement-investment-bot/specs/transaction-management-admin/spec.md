## ADDED Requirements

### Requirement: Accountant Can Record New Transactions
The system SHALL allow accountants to create new transaction records for investors including transaction type (deposit/withdrawal/dividend/cancellation), amount, date, and optional description. Transactions SHALL be stored in the database and investor notified.

#### Scenario: Accountant records investor deposit
- **WHEN** accountant clicks "ثبت تراکنش جدید" (Record New Transaction)
- **THEN** system prompts: "کدام سرمایه‌گذار؟" (Which investor?)
- **WHEN** accountant searches and selects investor by name or phone (search-and-select)
- **THEN** system asks: "نوع تراکنش؟" (Transaction Type?)
  - ➕ واریز سرمایه (Deposit)
  - ➖ برداشت (Withdrawal)
  - 💰 سود (Dividend)
  - 🔴 فسخ قرارداد (Cancellation)
- **WHEN** accountant selects "Deposit"
- **THEN** system asks: "مبلغ؟" (Amount?) + numeric input or paste
- **WHEN** accountant enters "500000000"
- **THEN** system asks: "تاریخ تراکنش؟" (Date?) with Jalali date picker
- **WHEN** accountant confirms date (e.g., فروردین 23, 1402)
- **THEN** system asks: "توضیح؟ (Optional)" (Description?)
- **WHEN** accountant enters optional description
- **THEN** system displays review screen showing all entered data
- **WHEN** accountant confirms "تایید" (Confirm)
- **THEN** transaction saved to database; investor notified via Telegram; accountant shown "تراکنش ثبت شد" (Transaction recorded)

#### Scenario: Withdrawal transaction recorded
- **WHEN** accountant selects "Withdrawal"
- **THEN** workflow same as deposit; amount displayed as negative in history

#### Scenario: Dividend payment recorded by accountant
- **WHEN** accountant selects "Dividend" type
- **THEN** system asks for amount and month of dividend
- **WHEN** accountant enters: amount=80000000, month=فروردین 1402
- **THEN** transaction created with auto-description "سود ماهانه فروردین 1402"

### Requirement: Amount Validation and Confirmation
The system SHALL validate that entered amounts are positive numbers and require explicit confirmation before saving to prevent costly typos.

#### Scenario: Invalid amount entry rejected
- **WHEN** accountant enters non-numeric amount (e.g., "five million")
- **THEN** system rejects entry: "لطفاً عدد وارد کنید" (Please enter a number)

#### Scenario: Negative amount prevented
- **WHEN** accountant enters negative amount for deposit (e.g., "-500000000")
- **THEN** system accepts but shows warning: "مبلغ منفی است؛ آیا مطمئن هستید؟" (Negative amount; are you sure?)

#### Scenario: Review before confirmation
- **WHEN** accountant enters amount=5000000000000 (excess zero)
- **THEN** system displays review screen:
  - سرمایه‌گذار: علی احمدی
  - مبلغ: 5,000,000,000,000 تومان (LARGE - stands out)
  - نوع: واریز
  - تاریخ: فروردین 23, 1402
  - "تایید" (Confirm) or "لغو" (Cancel)
- **WHEN** accountant sees excessive amount, clicks "لغو"
- **THEN** flow resets to amount entry step

### Requirement: Accountant Can Edit Previously Recorded Transactions
Accountant SHALL be able to locate a transaction by investor and date, edit its details, and save with audit trail.

#### Scenario: Accountant edits wrong amount
- **WHEN** accountant clicks "ویرایش تراکنش" (Edit Transaction)
- **THEN** system asks: "سرمایه‌گذار؟" (Investor?)
- **WHEN** accountant selects investor
- **THEN** system shows recent transactions for that investor
- **WHEN** accountant selects transaction to edit
- **THEN** system displays editable form with current values
- **WHEN** accountant changes amount from 500M to 700M and clicks "ذخیره"
- **THEN** system creates audit entry (not overwrite); investor notified of "تصحیح تراکنش" (Transaction Correction)

#### Scenario: Accountant cannot delete transaction
- **WHEN** accountant attempts to delete transaction
- **THEN** system does NOT offer delete option; only edit or view allowed

### Requirement: Accountant Cannot Set Valuation
Accountant SHALL NOT have permission to update investor portfolio valuation (reserve for admin).

#### Scenario: Accountant prevented from accessing valuation panel
- **WHEN** accountant tries to access valuation update feature
- **THEN** system displays: "تنها ادمین می‌تواند قیمت دارایی را بروزرسانی کند" (Only admin can update asset values)

### Requirement: Accountant Can Search Investors
Accountant SHALL search for investors by name or phone number to quickly locate the target investor for transaction recording.

#### Scenario: Search investor by name
- **WHEN** accountant clicks "جستجو سرمایه‌گذار" (Search Investor)
- **THEN** system shows search box: "نام یا شماره تماس را وارد کنید" (Enter name or phone)
- **WHEN** accountant types "علی"
- **THEN** system returns all investors with name containing "علی": "علی احمدی", "علی محمدی", etc. as inline buttons
- **WHEN** accountant clicks "علی احمدی"
- **THEN** investor selected and ready for transaction entry

#### Scenario: Search investor by phone
- **WHEN** accountant enters "09121234567"
- **THEN** system returns investor with matching phone: "علی احمدی | 09121234567"
- **WHEN** accountant clicks
- **THEN** investor selected

### Requirement: Transaction Validation Against Current Balance
System SHALL validate that withdrawal amount does not exceed current balance and warn accountant.

#### Scenario: Withdrawal exceeds balance
- **WHEN** investor current balance is 1B and accountant attempts to record withdrawal of 2B
- **THEN** system warns: "موجودی مسائل دارد! موجودی فعلی: 1,000,000,000" (Balance insufficient! Current balance: 1B)
- **WHEN** accountant clicks "ادامه با هشدار" (Continue with Warning)
- **THEN** transaction recorded but investor balance shows negative (flagged in system for admin review)

### Requirement: Accountant Can View Transaction History
Accountant SHALL be able to view all transactions (not just investor's own) to verify previous entries and prevent duplicates.

#### Scenario: Check investor's transaction history before adding
- **WHEN** accountant clicks "تاریخچه تراکنش‌ها" (Transaction History)
- **THEN** system asks to select investor or shows all recent transactions
- **WHEN** accountant selects investor
- **THEN** full transaction history displayed (same as investor sees, but accountant can see everyone's)
