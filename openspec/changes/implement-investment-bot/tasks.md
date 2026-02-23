## 1. Project Setup & Dependencies

- [ ] 1.1 Create Python project structure (pyproject.toml, requirements.txt)
- [ ] 1.2 Install core dependencies: aiogram 3.x, SQLAlchemy, asyncpg, psycopg2
- [ ] 1.3 Install utility packages: jdatetime (Jalali dates), python-dotenv, pydantic, aiohttp
- [ ] 1.4 Set up .env template for Telegram token, database URL, admin credentials
- [ ] 1.5 Create main bot application file (main.py) with asyncio runner
- [ ] 1.6 Configure logging (structured logging to file + console)

## 2. Database Setup

- [ ] 2.1 Design PostgreSQL schema (users, investments, transactions, valuations tables)
- [ ] 2.2 Create SQLAlchemy models for Users, Investments, Transactions, Valuations
- [ ] 2.3 Set up database connection pool with asyncpg
- [ ] 2.4 Create migration system (Alembic) for schema versioning
- [ ] 2.5 Write initial migration script with all tables, indexes, foreign keys
- [ ] 2.6 Create database initialization script (seed admin/accountant accounts for testing)
- [ ] 2.7 Implement connection error handling and retry logic

## 3. Bot Infrastructure & FSM

- [ ] 3.1 Create aiogram Dispatcher and FSM context storage setup
- [ ] 3.2 Define FSM states for multi-step flows (TransactionFSM, ValuationFSM, etc.)
- [ ] 3.3 Set up webhook or polling for Telegram message receiving
- [ ] 3.4 Create middleware for logging all incoming messages and callback queries
- [ ] 3.5 Implement rate limiting middleware to prevent abuse
- [ ] 3.6 Set up error handler for unexpected exceptions (log + respond to user)

## 4. Authentication & Authorization

- [ ] 4.1 Create authenticate() middleware function for Telegram ID verification
- [ ] 4.2 Implement phone number input flow on first /start
- [ ] 4.3 Create phone matching logic against users table
- [ ] 4.4 Implement role-based access control decorator (@require_role)
- [ ] 4.5 Create /start command handler with verification flow
- [ ] 4.6 Implement session management (per-user state tracking)
- [ ] 4.7 Create access denied error handler for unauthorized users

## 5. User & Role Management (Admin)

- [ ] 5.1 Create admin command: "مدیریت کاربران" (Manage Users)
- [ ] 5.2 Implement add user functionality (phone + name + role)
- [ ] 5.3 Implement remove user functionality
- [ ] 5.4 Implement change user role functionality
- [ ] 5.5 Create list all users view (paginated)
- [ ] 5.6 Implement user verification/unverification
- [ ] 5.7 Create users audit log viewer

## 6. Portfolio Status View (Investor)

- [ ] 6.1 Create portfolio calculation logic (sum all transactions + valuations)
- [ ] 6.2 Format monetary amounts with commas and تومان suffix
- [ ] 6.3 Convert Gregorian dates to Jalali format for display
- [ ] 6.4 Implement "وضعیت سرمایه من" handler for investors
- [ ] 6.5 Create portfolio display template with contract type indicator
- [ ] 6.6 Add last update timestamp to portfolio view
- [ ] 6.7 Implement portfolio refresh (< 1 second response time)
- [ ] 6.8 Handle edge cases (new investor with no transactions, multiple contracts)

## 7. Transaction Ledger View (Investor)

- [ ] 7.1 Create transaction history query (ordered by date DESC)
- [ ] 7.2 Implement transaction type emoji indicators (➕ ➖ 💰 🔴)
- [ ] 7.3 Create "تاریخچه تراکنش‌ها" handler for investors
- [ ] 7.4 Implement pagination for transaction lists (10 per page)
- [ ] 7.5 Create transaction detail expansion view
- [ ] 7.6 Add filter functionality (optional: by transaction type)
- [ ] 7.7 Implement export to text file functionality

## 8. Transaction Recording (Accountant)

- [ ] 8.1 Create investor search interface (search-and-select)
- [ ] 8.2 Implement search by name (partial matching)
- [ ] 8.3 Implement search by phone number (exact + partial)
- [ ] 8.4 Create transaction type selection buttons (deposit, withdrawal, dividend, cancellation)
- [ ] 8.5 Implement FSM for transaction entry (user → type → amount → date → description)
- [ ] 8.6 Create amount input validation (positive numbers, overflow checks)
- [ ] 8.7 Implement amount confirmation screen with summary review
- [ ] 8.8 Create database insertion logic for transaction record
- [ ] 8.9 Implement "ثبت تراکنش جدید" handler for accountants
- [ ] 8.10 Create edit transaction functionality (retrieve → modify → confirm)
- [ ] 8.11 Add validation: withdrawal doesn't exceed current balance (warning if over)
- [ ] 8.12 Create balance display after transaction (notifications to investor)

## 9. Portfolio Valuation (Admin)

- [ ] 9.1 Implement "بروزرسانی سرمایه و سود" handler for admin
- [ ] 9.2 Create investor selection interface (search-and-select)
- [ ] 9.3 Implement absolute value update mode (enter new portfolio value)
- [ ] 9.4 Implement profit percentage mode (calculate new value from %)
- [ ] 9.5 Create valuation confirmation screen with old/new comparison
- [ ] 9.6 Implement valuation database record creation (with reason field)
- [ ] 9.7 Create batch valuation update (CSV import)
- [ ] 9.8 Implement valuation audit log (view change history per investor)
- [ ] 9.9 Create dashboard showing investors needing valuation review (30+ days old)
- [ ] 9.10 Add automatic notification to investor after valuation update

## 10. Notifications (Push to Investor)

- [ ] 10.1 Create notification dispatcher function
- [ ] 10.2 Implement retry logic (exponential backoff, 3 attempts max)
- [ ] 10.3 Create transaction notification template (type, amount, new balance)
- [ ] 10.4 Create valuation update notification template (old/new value, % change)
- [ ] 10.5 Implement notification queueing for batch operations (30-second throttle)
- [ ] 10.6 Create failed notification logging for admin review
- [ ] 10.7 Implement notification preference toggle (investor can mute types)
- [ ] 10.8 Add notification history view (investor can see past notifications)

## 11. User Interface & UX

- [ ] 11.1 Create inline keyboard builder utilities (buttons, confirm/cancel patterns)
- [ ] 11.2 Create main menu handler (role-specific buttons)
- [ ] 11.3 Implement Persian text formatting helpers
- [ ] 11.4 Create Jalali date picker interface (month/day/year buttons)
- [ ] 11.5 Implement number formatting (comma separators, تومان suffix)
- [ ] 11.6 Create confirmation modal template (review before commit)
- [ ] 11.7 Create error message templates (user-friendly Persian messages)
- [ ] 11.8 Implement "بازگشت" (Back) and "لغو" (Cancel) navigation buttons
- [ ] 11.9 Create loading indicator messages ("درحال پردازش...")
- [ ] 11.10 Implement button state management (disable during processing)

## 12. Integration Tests

- [ ] 12.1 Write test for user authentication flow (phone verification)
- [ ] 12.2 Write test for role-based access control (investor vs. accountant vs. admin)
- [ ] 12.3 Test portfolio status calculation with sample transactions
- [ ] 12.4 Test transaction ledger pagination
- [ ] 12.5 Test transaction recording FSM (all paths)
- [ ] 12.6 Test valuation updates and notification delivery
- [ ] 12.7 Test search-and-select with various queries
- [ ] 12.8 Test concurrent updates (investor reads while accountant writes)
- [ ] 12.9 Test Jalali date conversions
- [ ] 12.10 Test error handling (invalid inputs, DB failures, Telegram API errors)

## 13. Deployment & Monitoring

- [ ] 13.1 Build Docker container with Python 3.11+ base image
- [ ] 13.2 Create docker-compose for PostgreSQL + bot services
- [ ] 13.3 Set up environment variables for production (token, DB URL, VPN/proxy settings)
- [ ] 13.4 Configure logging to file (structured JSON logs for analysis)
- [ ] 13.5 Set up health check endpoint (GET /health returns bot status)
- [ ] 13.6 Create systemd service file for bot auto-restart on failure
- [ ] 13.7 Set up database backup script (daily snapshot to S3)
- [ ] 13.8 Implement metrics collection (response times, error rates, user counts)
- [ ] 13.9 Deploy to staging environment and smoke test
- [ ] 13.10 Perform load testing with synthetic user traffic
- [ ] 13.11 Deploy to production with gradual investor rollout plan
- [ ] 13.12 Set up monitoring dashboard (uptime, error tracking, notification delivery)

## 14. Documentation & Handoff

- [ ] 14.1 Write API documentation for database schema
- [ ] 14.2 Write deployment runbook (setup, troubleshooting, rollback)
- [ ] 14.3 Create user guide for investors (how to use bot)
- [ ] 14.4 Create admin/accountant guide (how to manage system)
- [ ] 14.5 Write code comments for complex logic
- [ ] 14.6 Create troubleshooting guide for common issues
- [ ] 14.7 Document all environment variables and configuration
- [ ] 14.8 Create disaster recovery plan (DB restore, bot recovery)
- [ ] 14.9 Prepare handoff presentation for operations team
- [ ] 14.10 Archive all design decisions and rationale

## 15. Post-Launch Support

- [ ] 15.1 Monitor error logs daily for first week
- [ ] 15.2 Implement hot-fix deployment process
- [ ] 15.3 Gather investor feedback via "تماس با پشتیبانی" form
- [ ] 15.4 Plan feature improvements based on usage metrics
- [ ] 15.5 Schedule monthly valuation review reminders for admin
