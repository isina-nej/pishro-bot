## ADDED Requirements

### Requirement: Users Table with Role and Verification Status
The system SHALL maintain a Users table storing investor/accountant/admin identity, Telegram ID, phone number, role, verification status, and metadata.

#### Scenario: Create user record on first login
- **WHEN** new investor first sends /start command
- **THEN** system creates record:
  ```sql
  INSERT INTO users (telegram_id, phone_number, name, role, is_verified, created_at)
  VALUES (123456789, '09121234567', 'احمد علی', 'investor', false, NOW());
  ```

#### Scenario: Verify user after phone match
- **WHEN** phone verification succeeds
- **THEN** system updates:
  ```sql
  UPDATE users SET is_verified = true, verified_at = NOW() WHERE telegram_id = 123456789;
  ```

#### Scenario: User table supports multiple roles
- **WHEN** admin account exists
- **THEN** record stored:
  ```sql
  id: 1, telegram_id: 987654321, phone: '09121111111', role: 'admin', is_verified: true
  id: 2, telegram_id: 555555555, phone: '09122222222', role: 'accountant', is_verified: true
  id: 3, telegram_id: 123456789, phone: '09123333333', role: 'investor', is_verified: true
  ```

### Requirement: Investments Table with Contract Type Tracking
System SHALL track each investor's investment contracts including type (fixed-rate or variable holding), start date, initial amount, and current status.

#### Scenario: Store fixed-rate contract
- **WHEN** investor enrolls with 8% monthly fixed contract
- **THEN** record created:
  ```sql
  INSERT INTO investments (user_id, contract_type, initial_amount, start_date, dividend_rate, status)
  VALUES (3, 'fixed_rate', 1000000000, '1401-12-01', 0.08, 'active');
  ```

#### Scenario: Store variable holding contract
- **WHEN** investor has periodic holding with variable returns
- **THEN** record:
  ```sql
  INSERT INTO investments (user_id, contract_type, initial_amount, start_date, holding_period_months, status)
  VALUES (4, 'variable_holding', 2000000000, '1401-10-15', 6, 'active');
  ```

#### Scenario: Support contract status transitions
- **WHEN** investor cancels contract
- **THEN** status updated: `UPDATE investments SET status = 'cancelled', cancelled_date = NOW() WHERE id = X;`

### Requirement: Transactions Table with Full Audit Trail
System SHALL record all financial transactions (deposits, withdrawals, dividends, cancellations) with date, amount, type, description, and recording metadata.

#### Scenario: Record deposit transaction
- **WHEN** accountant records deposit
- **THEN** entry created:
  ```sql
  INSERT INTO transactions (investment_id, type, amount, transaction_date, description, recorded_by, recorded_at)
  VALUES (1, 'deposit', 500000000, '1402-01-23', 'بخش دوم هولد', 1, NOW());
  ```

#### Scenario: Record withdrawal transaction
- **WHEN** accountant records withdrawal
- **THEN** entry:
  ```sql
  INSERT INTO transactions (investment_id, type, amount, transaction_date, description, recorded_by, recorded_at)
  VALUES (1, 'withdrawal', -200000000, '1402-01-15', 'نیاز شخصی', 1, NOW());
  ```

#### Scenario: Record dividend transaction
- **WHEN** monthly dividend accrues
- **THEN** entry:
  ```sql
  INSERT INTO transactions (investment_id, type, amount, transaction_date, description, recorded_by, recorded_at)
  VALUES (1, 'dividend', 80000000, '1402-01-31', 'سود فروردین 1402', 1, NOW());
  ```

#### Scenario: Full transaction history queryable
- **WHEN** investor requests transaction history
- **THEN** query retrieves:
  ```sql
  SELECT * FROM transactions WHERE investment_id = 1 ORDER BY transaction_date DESC;
  ```

### Requirement: Valuations Table for Admin Updates
System SHALL track valuation updates (portfolio value overrides) with timestamp, old value, new value, admin who changed it, and optional reason.

#### Scenario: Record valuation update
- **WHEN** admin updates portfolio value
- **THEN** entry created:
  ```sql
  INSERT INTO valuations (investment_id, old_value, new_value, valuation_date, updated_by, reason)
  VALUES (1, 1500000000, 1620000000, '1402-01-23', 1, 'سود فروردین محاسبه‌شده');
  ```

#### Scenario: Valuation history accessible for audit
- **WHEN** admin views investor's valuation history
- **THEN** query:
  ```sql
  SELECT * FROM valuations WHERE investment_id = 1 ORDER BY valuation_date DESC;
  ```

#### Scenario: Valuation with auto-calculated profit
- **WHEN** admin updates profit percentage instead of absolute value
- **THEN** system calculates new_value and stores both calculated amount and original input

### Requirement: Indexes for Fast Queries
Database schema SHALL include indexes on frequently queried columns (user_id, telegram_id, transaction_date, investment_id).

#### Scenario: Fast user lookup by Telegram ID
- **WHEN** investor sends message and bot needs to authenticate
- **THEN** indexed query:
  ```sql
  SELECT * FROM users WHERE telegram_id = 123456789;
  ```

#### Scenario: Fast transaction history retrieval
- **WHEN** investor requests history
- **THEN** indexed query:
  ```sql
  SELECT * FROM transactions WHERE investment_id = 1 ORDER BY transaction_date DESC LIMIT 10;
  ```

### Requirement: Referential Integrity with Foreign Keys
Database schema SHALL enforce foreign key constraints to ensure data consistency (no orphaned records).

#### Scenario: Cannot record transaction for non-existent investment
- **WHEN** attempt to insert transaction with invalid investment_id
- **THEN** database rejects with constraint violation

#### Scenario: Cascade delete on investment cancellation (optional)
- **WHEN** investment marked as cancelled
- **THEN** historical transactions preserved; soft delete used (flag status, don't remove rows)

### Requirement: Timezone and Date Handling
Database SHALL store all timestamps in UTC; conversion to Jalali dates handled in application layer only.

#### Scenario: Transaction date stored as UTC
- **WHEN** accountant records transaction for Jalali date "فروردین 23, 1402"
- **THEN** database stores:
  ```sql
  transaction_date: 2023-04-13  (UTC Gregorian)
  ```
- **WHEN** displayed to investor, application converts back to "فروردین 23, 1402"

### Requirement: Support for Concurrent Read/Write (Optimistic Locking)
Database schema includes version column to prevent lost updates during concurrent edits.

#### Scenario: Admin safely updates valuation amid investor reads
- **WHEN** investor reading portfolio while admin updates it
- **THEN** no dirty reads; investor sees either old or new value consistently
- **AND** admin update uses version check to prevent overwriting concurrent changes

### Requirement: Encrypted Sensitive Fields (Optional)
Sensitive data (phone numbers, if regulations require) could be stored encrypted; decryption handled at application boundary.

#### Scenario: Phone number encrypted at rest
- **WHEN** phone number stored in database
- **THEN** value encrypted using AES-256
- **WHEN** retrieved by application, auto-decrypted before use
