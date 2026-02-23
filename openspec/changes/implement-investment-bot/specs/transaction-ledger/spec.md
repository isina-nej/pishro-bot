## ADDED Requirements

### Requirement: Investor Can View Complete Transaction History
The system SHALL display a chronological list of all financial transactions for an investor including deposits, withdrawals, dividends, and any contract cancellations. Each entry SHALL include date (Jalali), amount, transaction type, and description.

#### Scenario: View transaction history with multiple entries
- **WHEN** investor clicks "تاریخچه تراکنش‌ها" (Transaction History)
- **THEN** system displays list in reverse chronological order:
  - فروردین 23, 1402 | ➕ واریز سرمایه | +500,000,000 | توضیح: بخش دوم هولد
  - فروردین 1, 1402 | ➕ سود ماهانه | +80,000,000 | فروردین سود
  - اسفند 30, 1401 | ➖ برداشت | -100,000,000 | نیاز شخصی
  - اسفند 15, 1401 | ➕ سود ماهانه | +80,000,000 | اسفند سود
  - اسفند 1, 1401 | ➕ واریز اولیه | +1,000,000,000 | سرمایه اولیه

#### Scenario: Empty transaction history for new investor
- **WHEN** newly registered investor with no transactions views history
- **THEN** system displays: "هیچ تراکنشی ثبت نشده است" (No transactions recorded)

#### Scenario: Pagination for large transaction list
- **WHEN** investor has 50+ transactions
- **THEN** system displays first 10 entries with "بعدی" (Next) and "قبلی" (Previous) navigation buttons
- **WHEN** investor clicks "بعدی"
- **THEN** next 10 entries displayed

### Requirement: Transaction Type Indicators
Each transaction entry SHALL clearly indicate its type (deposit, withdrawal, dividend, contract cancellation) via visual emoji or Persian text labels.

#### Scenario: Deposit transaction indicated
- **WHEN** transaction is recorded as "increase" type
- **THEN** display shows: "➕ واریز سرمایه" with green color (if supported)
- **WHEN** amount: "500,000,000 تومان" is displayed in green

#### Scenario: Withdrawal transaction indicated
- **WHEN** transaction is recorded as "decrease" type
- **THEN** display shows: "➖ برداشت" with red color
- **WHEN** amount: "(100,000,000) تومان" shown in red/parentheses

#### Scenario: Dividend payment indicated
- **WHEN** transaction is recorded with type "dividend"
- **THEN** display shows: "💰 سود ماهانه" with description of month

#### Scenario: Contract cancellation indicated
- **WHEN** transaction is recorded as "cancellation"
- **THEN** display shows: "🔴 فسخ قرارداد" with full remaining balance returned

### Requirement: Jalali Date Display
All transaction dates SHALL be displayed in Jalali (Persian) calendar format (e.g., فروردین 23, 1402) to match user expectations.

#### Scenario: Gregorian date converted to Jalali
- **WHEN** transaction stored in database as Gregorian (2023-04-13)
- **THEN** displayed to user as "فروردین 23, 1402"

#### Scenario: Ancient transaction date formatted correctly
- **WHEN** transaction from over 1 year ago (e.g., 1400-01-01)
- **THEN** displayed as "فروردین 1, 1400" without time component

### Requirement: Transaction Details Expansion
Investor can tap/click on a transaction entry to view additional metadata (accountant notes, reference number, any attachments).

#### Scenario: Expand transaction for details
- **WHEN** investor clicks on transaction entry
- **THEN** system displays expanded view:
  - تاریخ: فروردین 23, 1402
  - مبلغ: 500,000,000 تومان
  - نوع: واریز سرمایه
  - توضیح: بخش دوم هولد ۳ ماهه
  - ثبت شده توسط: حسابدار_1 (accountant username)
  - آیدی تراکنش: TXN-2024-001234

#### Scenario: Return to list from expanded view
- **WHEN** investor viewing expanded transaction details presses "بازگشت" (Back)
- **THEN** system returns to transaction list

### Requirement: Filter Transactions by Type (Future)
System SHALL support filtering transaction history by type (deposits only, withdrawals only, dividends, cancellations) via inline buttons.

#### Scenario: Filter to show only deposits
- **WHEN** investor clicks "فیلتر" (Filter) → "فقط واریزها"
- **THEN** list shows only deposit transactions; "حذف فیلتر" button available

### Requirement: Export Transaction History
System SHALL provide option to export transaction history as text file (txt format) or PDF for record-keeping.

#### Scenario: Export as text file
- **WHEN** investor clicks "دانلود تاریخچه" (Download History)
- **THEN** bot prepares text file with all transactions and sends to user as Telegram document
- **WHEN** file contains all transactions with dates, amounts, types in plain text format
