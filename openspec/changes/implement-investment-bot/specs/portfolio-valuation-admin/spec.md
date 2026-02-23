## ADDED Requirements

### Requirement: Admin Can Update Portfolio Valuation
The system SHALL allow admin (Dr. X) to override/update the current value of an investor's portfolio regardless of transaction history. This is used for periodic holding contracts where value is manually assessed.

#### Scenario: Admin updates investor's portfolio value
- **WHEN** admin clicks "بروزرسانی سود و دارایی" (Update Profit/Asset Value)
- **THEN** system prompts: "سرمایه‌گذار؟" (Select Investor?)
- **WHEN** admin searches and selects investor
- **THEN** system displays current portfolio:
  - سرمایه‌گذار: احمد علی
  - نوع قرارداد: هولد پی‌ریودی متغیر
  - ارزش فعلی: 1,500,000,000 تومان
  - "ویرایش ارزش" (Edit Value) or "ویرایش درصد سود" (Edit Profit Percentage)
- **WHEN** admin clicks "ویرایش ارزش"
- **THEN** system prompts: "ارزش جدید دارایی؟" (New asset value?)
- **WHEN** admin enters "1,620,000,000"
- **THEN** system shows review:
  - ارزش قدیم: 1,500,000,000 تومان
  - ارزش جدید: 1,620,000,000 تومان
  - تغییر: +120,000,000 تومان (+8%)
  - تاریخ بروزرسانی: فروردین 23, 1402
- **WHEN** admin confirms "تایید"
- **THEN** value updated; investor notified: "دارایی شما بروزرسانی شد: 1,620,000,000 تومان"

#### Scenario: Update profit percentage instead of absolute value
- **WHEN** admin chooses "درصد سود" (Profit Percentage) mode
- **THEN** system asks: "درصد سود فعلی؟ (مثال: 25 برای 25%)" (Profit % ? e.g., 25 for 25%)
- **WHEN** admin enters "32"
- **THEN** system calculates: Initial_Capital × (1 + 32%) = New_Value
- **WHEN** admin confirms
- **THEN** final calculated value is set in database

### Requirement: Valuation Update Notification to Investor
When admin updates an investor's valuation, investor SHALL receive immediate notification showing old value, new value, and change amount.

#### Scenario: Investor receives valuation update notification
- **WHEN** admin updates investor's portfolio value
- **THEN** investor receives Telegram message:
  - "🔔 دارایی شما بروزرسانی شد"
  - "ارزش قدیم: 1,500,000,000 تومان"
  - "ارزش جدید: 1,620,000,000 تومان"
  - "تغییر: +120,000,000 تومان"
  - "تاریخ: فروردین 23, 1402 ساعت 14:32"

### Requirement: Admin Can Override Entire Portfolio State
Admin SHALL be able to set multiple investor valuations in batch (future) or individually correct portfolio state if data corruption occurs.

#### Scenario: Admin corrects investor portfolio after data error
- **WHEN** data corruption discovered (wrong balance calculated)
- **WHEN** admin accesses "تصحیح دستی دارایی" (Manual Asset Correction)
- **THEN** system allows admin to set exact:
  - Initial capital
  - Any interim deposits/withdrawals
  - Current profit value
- **WHEN** admin saves
- **THEN** portfolio recalculated and investor notified

### Requirement: Audit Trail for Valuation Changes
System SHALL record all valuation updates with timestamp, old value, new value, admin who made change, and reason (optional).

#### Scenario: Admin notes reason for valuation change
- **WHEN** admin updating valuation, system optionally asks: "دلیل تغییر؟ (اختیاری)" (Reason for change? Optional)
- **WHEN** admin enters "سود فروردین محاسبه‌شده توسط بورس" (April dividend calculated from exchange)
- **THEN** reason stored with valuation record in audit table
- **WHEN** future admin checks audit log: "بروزرسانی seriosis: admin Dr_X | ارزش قدیم: 1.5B | ارزش جدید: 1.62B | دلیل: سود فروردین..."

### Requirement: Periodic Batch Valuation Updates
Admin SHALL be able to update valuations for multiple investors at once (batch update) during monthly/quarterly reviews.

#### Scenario: Admin uploads batch valuation file
- **WHEN** admin clicks "بروزرسانی دسته‌ای" (Batch Update)
- **THEN** system provides CSV template:
  ```
  phone_number, new_value, date
  09121234567, 1620000000, 23/12/1402
  09129876543, 2100000000, 23/12/1402
  ```
- **WHEN** admin fills template and uploads
- **THEN** system validates entries, shows preview of all changes
- **WHEN** admin confirms
- **THEN** all valuations updated atomically; all affected investors notified

### Requirement: Admin Cannot Accidentally Delete Valuations
Admin updates SHALL always be additive (new record) not destructive (overwrite); valuation history preserved.

#### Scenario: Valuation history accessible
- **WHEN** admin views investor's valuation audit trail
- **THEN** system shows:
  - فروردین 23, 1402 14:32 | 1,620,000,000 | توسط Dr_X | دلیل: سود فروردین
  - فروردین 1, 1402 10:00 | 1,500,000,000 | توسط Dr_X | دلیل: ارزش‌گذاری اولیه
  - (all previous valuations visible)

### Requirement: Dividend Calculation Strategy Support
System SHALL support both automatic and manual dividend calculation based on contract type.

#### Scenario: Fixed-rate contract auto-calculates dividend
- **WHEN** investor has 8% monthly fixed contract and 4 months have passed
- **THEN** system calculates: Dividend = Initial_Capital × 8% × 4 months
- **WHEN** admin updates valuation, system pre-fills calculated profit
- **WHEN** admin modifies value, calculation overridden

#### Scenario: Variable holding contract requires manual valuation
- **WHEN** investor has variable holding contract
- **THEN** system requires admin to manually enter valuation (no auto-calculation)
- **WHEN** admin enters profit %, system calculates final asset value

### Requirement: Admin Dashboard Shows Pending Reviews
Admin SHALL see a dashboard showing which investor valuations are over 30 days old and needing review.

#### Scenario: Old valuation flagged for review
- **WHEN** admin opens "لیست سرمایه‌گذاران" (Investor List)
- **THEN** system displays list with age of last valuation:
  - ✅ احمد | آخرین بروزرسانی: 2 روز پیش
  - ⚠️ علی | آخرین بروزرسانی: 35 روز پیش (needs updating)
  - 🔴 محمد | آخرین بروزرسانی: 65 روز پیش (urgent)
