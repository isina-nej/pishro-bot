## Why

Investors (~50-60 people) currently contact us repeatedly via phone to ask about their investment status, dividends, and account history. This creates significant operational overhead for the management team. We need a self-service platform that allows investors to instantly check their portfolio status without manual intervention, while providing secure admin/accountant panels for managing transactions and valuations in real-time.

## What Changes

- **New Telegram Bot Application**: A complete Telegram bot with aiogram 3.x framework supporting async operations
- **Role-Based Access Control**: Three distinct user levels with different capabilities:
  - Investors: View portfolio and transaction history
  - Accountants: Record financial transactions
  - Admins: Update valuations and override portfolio values
- **Investment Portfolio Management**: Track two types of investment contracts:
  - Fixed-rate (8% monthly dividend)
  - Periodic holding with variable returns
- **Transaction Ledger System**: Complete history of all portfolio changes (deposits, withdrawals, cancellations) with Jalali dates
- **Real-time Notifications**: Investors receive instant notifications when admins update their portfolio
- **PostgreSQL Database**: Secure, transactional storage for all financial data
- **Admin Management Interfaces**: Inline keyboard-based UI for intuitive data entry and updates

## Capabilities

### New Capabilities

- `user-authentication`: Verify users via Telegram ID and phone number; implement role-based access control (Investor/Accountant/Admin)
- `portfolio-status-view`: Display investor's current balance, initial capital, transaction history, and calculated dividends
- `transaction-ledger`: Record deposits, withdrawals, and contract cancellations with Jalali date tracking
- `transaction-management-admin`: Accountant interface for adding/editing transaction records
- `portfolio-valuation-admin`: Admin interface for updating portfolio values and dividend percentages
- `investor-notifications`: Push notifications to investors when their portfolio is modified
- `database-schema`: PostgreSQL schema with Users, Investments, Transactions, and Valuations tables
- `inline-keyboard-ui`: Responsive Telegram UI using inline keyboards for all interactions
- `search-and-select`: User lookup by name/phone number for accountants and admins

### Modified Capabilities

(None - this is a new system)

## Impact

- **New Dependencies**: aiogram 3.x, SQLAlchemy, PostgreSQL driver (psycopg2), python-telegram-bot utilities
- **Infrastructure**: Requires PostgreSQL database hosted outside Iran (due to Telegram filtering)
- **Deployment**: Python 3.11+ server with persistent bot token and database credentials
- **No Integration with Existing Systems**: Hardware wallet shop handled separately; this is standalone investment tracking
- **User Data**: Sensitive financial data requires encryption and strict access control
