## ADDED Requirements

### Requirement: Investor Receives Transaction Notifications
When accountant adds a transaction to investor's portfolio, investor SHALL immediately receive a Telegram notification with transaction details.

#### Scenario: Investor notified of deposit
- **WHEN** accountant records deposit of 500M for investor
- **THEN** investor receives Telegram message within 2 seconds:
  - "₠ تراکنش جدید"
  - "نوع: واریز سرمایه"
  - "مبلغ: 500,000,000 تومان"
  - "تاریخ: فروردین 23, 1402"
  - "توضیح: بخش دوم هولد"
  - "موجودی جدید: 1,620,000,000 تومان"
  - [دیدن جزئیات] (View Details) button

#### Scenario: Investor alerted to withdrawal
- **WHEN** accountant records withdrawal
- **THEN** investor receives similar notification with "نوع: برداشت"
- **AND** amount shown as red/negative: "(100,000,000)"

#### Scenario: Dividend payment notification
- **WHEN** accountant records dividend payment
- **THEN** investor receives:
  - "💰 سود ماهانه منتقل شد"
  - "مبلغ سود: 80,000,000 تومان"
  - "موجودی جدید: 1,700,000,000 تومان"

### Requirement: Investor Receives Valuation Update Notifications
When admin updates investor's portfolio valuation, investor SHALL receive detailed notification of value change.

#### Scenario: Investor notified of valor valuation increase
- **WHEN** admin updates investor's asset value from 1.5B to 1.62B
- **THEN** investor receives:
  - "🔔 دارایی شما بروزرسانی شد"
  - "ارزش قدیم: 1,500,000,000 تومان"
  - "ارزش جدید: 1,620,000,000 تومان"
  - "تغییر: +120,000,000 تومان (+8%)"
  - "تاریخ: فروردین 23, 1402 ساعت 14:32"

#### Scenario: Investor notified of valuation decrease
- **WHEN** admin updates investor's asset value downward
- **THEN** notification shows decrease with red/negative icon:
  - "📉 دارایی شما تغییر کرد"
  - "تغییر: (50,000,000) تومان (-3%)"

### Requirement: Push Notification Delivery Guarantee
Bot SHALL reattempt notification delivery if initial Telegram API call fails, with exponential backoff (max 3 attempts).

#### Scenario: Failed notification retry
- **WHEN** first notification attempt fails (Telegram API timeout)
- **THEN** system waits 5 seconds and retries
- **IF** still fails, waits 30 seconds and retries once more
- **IF** still fails, logs error and alerts admin; investor notified next time they open bot

#### Scenario: Successful notification after retry
- **WHEN** first Telegram API call fails
- **THEN** second attempt succeeds
- **AND** investor receives notification without knowing about retry

### Requirement: Mute/Unmute Notifications
Investor SHALL be able to disable/enable notifications temporarily or permanently.

#### Scenario: Investor mutes notifications
- **WHEN** investor clicks main menu → "تنظیمات" (Settings) → "مدیریت اطلاع‌رسانی" (Notification Preferences)
- **THEN** system shows options:
  - ✅ اطلاع تراکنش‌ها (Notify on transactions) - enabled by default
  - ✅ اطلاع بروزرسانی دارایی (Notify on valuations) - enabled by default
  - Both can be toggled on/off
- **WHEN** investor disables transaction notifications
- **THEN** future transactions not notified; investor can still check manually in bot

#### Scenario: Re-enable notifications
- **WHEN** investor re-checks notification preferences and enables
- **THEN** next transaction/update notification send normally

### Requirement: Notification Does Not Reveal Other Investors' Data
Notification SHALL only show affected investor's own data; no information about other investors visible.

#### Scenario: Message contains only personal data
- **WHEN** investor receives transaction notification
- **THEN** message shows only:
  - Their own balance changes
  - Their own portfolio value
  - Not other investors' names, amounts, or transactions

### Requirement: Batch Notification Delivery for Admin Actions
When admin does batch updates, system SHALL queue notifications and send within 30 seconds (not instantly for each entry) to avoid spam.

#### Scenario: Batch update notification throttling
- **WHEN** admin updates valuations for 5 investors via batch import
- **THEN** system:
  - Processes all 5 updates immediately in DB
  - Queues notifications for all 5 investors
  - Sends all 5 notifications over 30 seconds (1 per 6 sec)
- **AND** each investor receives their own message (not grouped)

### Requirement: Notification Includes Action Buttons
Notifications include inline buttons to quickly view full details or ack receipt.

#### Scenario: Check Details button in notification
- **WHEN** investor receives transaction notification
- **THEN** message includes inline button: [📊 دیدن وضعیت من] (View My Status)
- **WHEN** investor clicks button
- **THEN** bot shows full portfolio status without requiring menu navigation

#### Scenario: Notification with archive option
- **WHEN** investor receives old notification (more than 7 days old)
- **THEN** message may be removed from notification queue; investor can still view history in "تاریخچه تراکنش‌ها"

### Requirement: Failed Notification is Logged for Admin Investigation
If notification fails after retries, system logs event for admin to manually follow up.

#### Scenario: Notification failure logged
- **WHEN** investor's Telegram account is banned/suspended by Telegram
- **THEN** bot cannot send notification; system logs:
  - investor_id: X
  - transaction_id: TXN-YZ
  - error: "user blocked bot" or "account suspended"
  - timestamp: 2024-04-13 14:32
- **AND** admin can query admin panel to see "failed notifications" list for investigation
