## ADDED Requirements

### Requirement: Search Investors by Name
System SHALL allow accountant and admin to search for investors by full name (supports partial matching) and display results as selectable buttons.

#### Scenario: Search by partial name
- **WHEN** accountant clicks "جستجو سرمایه‌گذار"
- **THEN** system shows input prompt: "نام سرمایه‌گذار را وارد کنید:" (Enter investor name)
- **WHEN** accountant types "احمد"
- **THEN** system searches databases and returns all investors with "احمد" in name:
  ```
  نتایج جستجو برای "احمد":
  
  [👤 احمد علی | 09121234567]
  [👤 محمد احمدی | 09129876543]
  
  [جستجوی جدید زدن][بازگشت]
  ```

#### Scenario: Case-insensitive search
- **WHEN** accountant types "احمد" (uppercase)
- **THEN** system matches results (search case-insensitive for Persian text)

#### Scenario: Diacritic-insensitive search (optional)
- **WHEN** accountant types "احیاد" (variation of ahmad)
- **THEN** system still returns matches (handles Persian character variations)

### Requirement: Search Investors by Phone Number
System SHALL support searching by exact or partial phone number.

#### Scenario: Search by full phone
- **WHEN** accountant enters "09121234567"
- **THEN** system returns exact match:
  ```
  نتایج جستجو برای "09121234567":
  
  [👤 احمد علی | 09121234567]
  ```

#### Scenario: Search by partial phone
- **WHEN** accountant enters "0912123"
- **THEN** system returns all numbers starting with this prefix:
  ```
  نتایج جستجو برای "0912123":
  
  [👤 احمد علی | 09121234567]
  [👤 علی رضائی | 09121239999]
  ```

#### Scenario: Invalid phone format accepted gracefully
- **WHEN** accountant enters "912 1234567" (spaces)
- **THEN** system normalizes to "09121234567" and searches (whitespace ignored)

### Requirement: Select Investor from Search Results
Each search result is a clickable inline button that selects the investor.

#### Scenario: Click investor to select
- **WHEN** search results displayed and accountant clicks "👤 احمد علی"
- **THEN** investor selected and flow continues (e.g., transaction entry)
- **AND** investor's information loaded into context for subsequent steps

#### Scenario: Back to search after accidental click
- **WHEN** accountant clicks wrong investor by mistake
- **THEN** system shows confirmation:
  ```
  سرمایه‌گذار انتخاب‌شده: احمد علی
  [✅ تایید][❌ انتخاب مجدد]
  ```

### Requirement: Search Result Limit and Pagination
If search returns many results (>10), paginate with Previous/Next buttons.

#### Scenario: Many search results paginated
- **WHEN** search for "علی" returns 20 matches
- **THEN** display first 10:
  ```
  نتایج جستجو برای "علی" (20 نتیجه):
  
  [👤 علی احمدی...]
  [👤 علی محمدی...]
  ... (8 more)
  
  صفحه 1 از 2
  [◀ قبلی][بعدی ▶]
  ```

#### Scenario: Navigate to next page
- **WHEN** accountant clicks "بعدی"
- **THEN** next 10 results displayed

### Requirement: No Results Handling
If search returns no matches, inform user clearly and allow retry.

#### Scenario: Search returns no results
- **WHEN** accountant searches "xyz" (no matching investor)
- **THEN** system displays:
  ```
  ❌ نتیجه‌ای برای "xyz" یافت نشد
  
  احتمالات:
  - نام درست وارد شده است
  - سرمایه‌گذار وجود ندارد
  - نام‌های فارسی را بدون فاصله بنویسید
  
  [جستجوی جدید][بازگشت]
  ```

### Requirement: Display Selected Investor Details in Confirmation
After searching and selecting, show investor summary before proceeding.

#### Scenario: Investor summary before transaction
- **WHEN** accountant selects investor "احمد علی"
- **THEN** system displays:
  ```
  ✅ سرمایه‌گذار انتخاب‌شده:
  ━━━━━━━━━━━━━━━━━━━
  نام: احمد علی
  شماره تماس: 09121234567
  نوع قرارداد: درآمد ثابت 8% ماهانه
  موجودی فعلی: 1,120,000,000 تومان
  ━━━━━━━━━━━━━━━━━━━
  
  [✅ ادامه][❌ انتخاب دوباره]
  ```

### Requirement: Search with Exact Phone Pre-filling
If accountant/admin enters phone before searching, system pre-fills investor from phone lookup.

#### Scenario: Direct phone lookup (alternative flow)
- **WHEN** admin enters phone in "مدیریت کاربران" → "شماره تماس: 09121234567"
- **THEN** system auto-populates:
  ```
  سرمایه‌گذار: احمد علی
  نام: احمد علی
  [ادامه]
  ```

### Requirement: Search Cache for Performance
Recently searched investors cached to enable quick re-access without database query.

#### Scenario: Repeat search is instant
- **WHEN** accountant searched "احمد" 1 minute ago and searches again
- **THEN** results returned from cache (<100ms) without database hit
- **WHEN** results change in meantime (investor deleted), cache invalidated on next /start

### Requirement: Audit Log of Search Queries (Optional)
System logs all search queries by accountant/admin for audit purposes (privacy/compliance).

#### Scenario: Search audit trail
- **WHEN** accountant searches for investor
- **THEN** system logs:
  ```
  audit_log:
  - who: accountant_1 (telegram_id: 555555555)
  - action: search
  - query: "احمد"
  - timestamp: 2024-04-13 14:32
  - results_count: 2
  ```
- **NOTE**: Useful for detecting unauthorized searches for privacy compliance

### Requirement: Autocomplete During Input (Optional Enhancement)
As accountant types name/phone, system suggests matching investors (live autocomplete).

#### Scenario: Live autocomplete as typing
- **WHEN** accountant types names in search box:
  - After "احمد" + typing "ع" → shows "احمدعلی", "احمدعباس", etc. below input
  - Accountant can tap suggestion to confirm immediately

#### Scenario: Autocomplete disabled for privacy
- **WHEN** privacy setting enabled
- **THEN** autocomplete turned off; user must complete input before results shown
