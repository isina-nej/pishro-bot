## ADDED Requirements

### Requirement: Display Portfolio Balance Summary
The system SHALL display an investor's complete financial position including initial capital, current value, deposits/withdrawals, and calculated profit/loss. All amounts displayed in Toman currency with delimiter formatting (e.g., 1,000,000,000).

#### Scenario: Investor views portfolio status
- **WHEN** investor clicks "وضعیت سرمایه من" (My Status) button
- **THEN** system displays:
  - Initial Capital: 1,000,000,000 تومان
  - Current Deposits: 500,000,000 تومان
  - Current Withdrawals: (200,000,000) تومان
  - Profit/Dividend: 320,000,000 تومان
  - **Total Current Value: 1,620,000,000 تومان**
  - Last Updated: فروردین 23, 1402 (Jalali date)

#### Scenario: Portfolio with single deposit only
- **WHEN** new investor (just enrolled) requests status
- **THEN** system shows:
  - Initial Capital: 1,000,000,000 تومان
  - Current Deposits: 0
  - Current Withdrawals: 0
  - Profit/Dividend: 0
  - **Total Current Value: 1,000,000,000 تومان**

#### Scenario: Multiple portfolio updates accumulate correctly
- **WHEN** investor has 5+ transactions over months (deposits, dividends added)
- **THEN** system sums all transactions correctly and displays accurate total value (verified via database)

### Requirement: Display Profit Calculation Based on Contract Type
The system SHALL calculate and display profit differently for two contract types: fixed-rate (8% monthly) and periodic holding (variable). The display SHALL indicate which type applies.

#### Scenario: Fixed-rate investor profit display
- **WHEN** investor with 8% monthly fixed contract views status
- **THEN** system displays:
  - "نوع قرارداد: درآمد ثابت 8% ماهانه" (Contract: Fixed 8% Monthly)
  - Profit calculated as: Principal × 8% × Months Held
  - Example: 1B invested for 4 months = 320M profit

#### Scenario: Variable holding contract profit display
- **WHEN** investor with variable periodic holding views status
- **THEN** system displays:
  - "نوع قرارداد: هولد پی‌ریودی متغیر" (Contract: Variable Periodic Holding)
  - Profit value: Last value set by admin (not auto-calculated)
  - Example: "قیمت فعلی دارایی: 1,620,000,000 تومان" (Current Asset Value: 1,620,000,000)

### Requirement: Show Transaction Metadata
Portfolio status view SHALL include metadata about last update timestamp and transaction count to provide confidence in data freshness.

#### Scenario: Last update timestamp displayed
- **WHEN** investor views status
- **THEN** display shows: "آخرین بروزرسانی: فروردین 23, 1402 ساعت 14:32" (Last Updated: ...)

#### Scenario: Transaction count indicator
- **WHEN** investor portfolio has 8 recorded transactions
- **THEN** status view shows: "تعداد تراکنش‌ها: 8" (Transaction Count: 8)

### Requirement: Fast Response Time
Portfolio status query response SHALL complete in under 1 second to ensure responsive UX.

#### Scenario: Status query on slow network
- **WHEN** investor on 3G network requests portfolio status
- **THEN** response received in <1 second (queries optimized with DB indexes)

### Requirement: Format Numbers with Locale Awareness
All monetary amounts SHALL display with comma separators and Toman suffix (تومان) according to Persian locale conventions.

#### Scenario: Large numbers formatted correctly
- **WHEN** investor balance is 2,500,000,000 Toman
- **THEN** display shows: "2,500,000,000 تومان" (not "2500000000")

#### Scenario: Small numbers formatted
- **WHEN** investor balance is 999,999 Toman
- **WHEN** display shows: "999,999 تومان"
