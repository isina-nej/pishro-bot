## ADDED Requirements

### Requirement: User Registration and Phone Verification
The system SHALL verify a new user by matching their Telegram ID with a pre-registered phone number in the database. On first login, the user SHALL enter their phone number, which SHALL be matched against registered phone numbers. If matched, the user is activated; if not, access denied.

#### Scenario: Successful registration with matching phone
- **WHEN** unregistered user sends /start command
- **THEN** bot asks for phone number via inline keyboard with input request
- **WHEN** user enters phone matching registered record
- **THEN** system marks user as verified and shows main menu; subsequent logins no longer require phone verification

#### Scenario: Registration attempt with non-matching phone
- **WHEN** unregistered user enters non-matching phone number
- **THEN** system rejects access and displays "شما دسترسی ندارید" (You don't have access)

#### Scenario: Verified user returns for new session
- **WHEN** verified user sends /start command in new chat session
- **THEN** system recognizes Telegram ID, skips phone verification, and shows main menu immediately

### Requirement: Role-Based Access Control
The system SHALL enforce three distinct user roles (Investor, Accountant, Admin) and restrict menu options and data access based on assigned role. Only authorized users can access their role's features.

#### Scenario: Investor role gets limited menu
- **WHEN** investor user selects main menu
- **THEN** system displays only: "وضعیت سرمایه من" (My Status), "تاریخچه تراکنش‌ها" (Transaction History), "تماس با پشتیبانی" (Support)

#### Scenario: Accountant role gets transaction management
- **WHEN** accountant user selects main menu
- **THEN** system displays: "ثبت تراکنش جدید" (Record Transaction), "جستجو سرمایه‌گذار" (Search Investor), "تاریخچه تراکنش‌ها" (Transaction History)

#### Scenario: Admin can see all features
- **WHEN** admin user selects main menu
- **THEN** system displays all options: investor view + accountant options + "بروزرسانی سود" (Update Valuations), "مدیریت کاربران" (User Management)

#### Scenario: Unauthorized feature access attempt
- **WHEN** investor tries to directly access accountant feature via callback query
- **THEN** system rejects request and displays "شما دسترسی ندارید" (No Access)

### Requirement: Telegram ID & Phone Number Mapping
The system SHALL maintain a secure mapping between Telegram IDs and phone numbers in the database to prevent user spoofing and enable phone-based backup verification.

#### Scenario: Admin pre-registers phone before user first login
- **WHEN** admin imports investor list with phone numbers via database migration
- **THEN** system stores mapping; investor can access on first /start with phone verification

#### Scenario: System prevents duplicate Telegram IDs
- **WHEN** two different people attempt to use same Telegram account (same Telegram ID)
- **THEN** system allows only first registered user; denies second login

### Requirement: Session Invalidation on Role Change
The system SHALL invalidate existing user sessions if admin changes a user's role, requiring re-authentication on next interaction.

#### Scenario: Admin revokes investor access
- **WHEN** active investor session exists and admin removes investor from users table
- **THEN** next /start command triggers "access denied" flow

## MODIFIED Requirements

(None - authentication is new capability)
