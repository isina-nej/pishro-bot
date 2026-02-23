## Context

The investment management company currently manages ~50-60 high-net-worth investors with two types of investment contracts: fixed-rate (8% monthly dividend) and periodic holding with variable returns. Investors repeatedly call the management team to check their portfolio status, creating operational overhead.

The company operates in Iran but needs to provide services via Telegram, which is filtered in Iran. All users access through VPN or proxy. The management team includes an accountant who records transactions and a senior admin (Dr. X) who updates valuations.

Current state: Manual spreadsheet tracking with phone-based inquiries. No self-service capability exists.

## Goals / Non-Goals

**Goals:**

- Enable investors to self-service check portfolio status 24/7 via Telegram
- Provide accountants a secure interface to log financial transactions
- Provide admins granular control over portfolio valuations and dividend calculations
- Reduce phone-based inquiry overhead by >80%
- Maintain complete transaction audit trail with Jalali date tracking
- Ensure data security and prevent unauthorized access to other investors' data
- Achieve 99.9% uptime with async operations handling concurrent requests

**Non-Goals:**

- Automated payment processing (deposits/withdrawals remain manual via bank)
- Integration with exchanges or trading systems for auto-calculated returns
- Hardware wallet shop functionality (separate from this bot)
- SMS/WhatsApp fallback channels
- Multi-language support beyond Persian

## Decisions

### 1. Framework Choice: aiogram 3.x (Async Bot)

**Decision**: Use aiogram 3.x as the Telegram bot framework.

**Rationale**: 
- Best async support for handling concurrent requests from 60+ users without blocking
- Most actively maintained Python Telegram library
- Type-safe with full aiogram typing
- Native support for callback queries and inline keyboards
- Battle-tested in production systems

**Alternatives Considered**:
- python-telegram-bot (pyTelegramBotAPI): Older, simpler, but less performant for concurrent ops
- telethon: Lower-level, overkill for chatbot use case
- Direct HTTP polling: Inefficient and harder to maintain state

### 2. Database: PostgreSQL + SQLAlchemy ORM

**Decision**: Use PostgreSQL for persistence with SQLAlchemy ORM + async driver (asyncpg).

**Rationale**:
- ACID transactions critical for financial data
- Ensures data consistency even during system crashes
- SQLAlchemy provides schema versioning and migration support
- asyncpg is the fastest PostgreSQL driver for Python async code
- Easy to back up and replicate for disaster recovery

**Alternatives Considered**:
- SQLite: Insufficient concurrency; not suitable for multi-user financial system
- Redis: No persistence; would require dual storage (Redis + DB)
- Firebase: No control over data location; may violate Iranian compliance needs

### 3. Database Host Location

**Decision**: PostgreSQL server hosted outside Iran (AWS/DigitalOcean/Hetzner).

**Rationale**:
- Telegram is filtered in Iran; making the bot accessible requires proxy infrastructure
- Keeping DB in Iran creates latency issues across VPN tunnels
- International hosting provides better reliability and backup options

**Risks**: Data residency compliance if investors are in Iran; recommend legal review.

### 4. User Authentication: Telegram ID + Phone Number Verification

**Decision**: Authenticate users via Telegram ID coupled with phone number verification on first login.

**Rationale**:
- Telegram ID is immutable and unique
- Phone number adds extra verification layer
- Prevents account takeover via SIM hijacking alone
- Simple UX: no password management
- Admin pre-registers phone numbers in system before user first access

**Alternatives Considered**:
- Password-based auth: Weak UX for users who may be non-technical; higher support burden
- Telegram auth payload only: Sufficient but no secondary verification

### 5. Role-Based Access Control (RBAC)

**Decision**: Three fixed roles with explicit permissions: Investor, Accountant, Admin.

**Rationale**:
- Clear separation of concerns
- Prevent accountant from viewing other investors' data
- Enable admin to override valuations without exposing raw manipulation to accountants
- Easy to audit: each role has distinct message handlers

**Roles & Permissions**:
- **Investor**: View own portfolio only; see transaction history; receive notifications
- **Accountant**: View all portfolios; create/edit/delete transaction records; cannot change valuations
- **Admin**: Full control; update valuations, override values, manage users

### 6. State Management: Finite State Machine (FSM)

**Decision**: Use aiogram's FSM (finite state machine) for multi-step flows (e.g., recording a transaction).

**Rationale**:
- Prevents message ordering bugs in async flows
- Clear state transitions: reduces race conditions
- Example states: awaiting_user_selection → awaiting_transaction_type → awaiting_amount → awaiting_date → confirming

**Trade-off**: Slight complexity in code structure; offset by robustness

### 7. Transaction Input Validation

**Decision**: Heavy client-side validation with confirmation step before database commit.

**Rationale**:
- Protects against typos (e.g., extra zero causing wrong investor balance)
- Shows investor updated balance for 24 hours after change so they can alert admins
- Confirmation flow: amount → date → review summary → confirm

**Mitigation for data errors**: Future "edit transaction" feature allows post-correction.

### 8. Notification Architecture

**Decision**: Bot sends direct push notifications via Telegram message (callback handler on edit).

**Rationale**:
- No external notification service needed
- Telegram guarantees delivery to user
- Simple API: just send message to investor's Telegram ID

**Limitation**: No SMS fallback (out of scope).

### 9. Jalali Date Input / Display

**Decision**: Use `jalali` or `jdatetime` Python library for all date operations.

**Rationale**:
- All data entered/displayed in Jalali dates (Iranian calendar)
- Database stores Gregorian internally for calculation; convert at UI boundaries
- Prevents confusion for users familiar only with Persian calendar

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Typo in transaction amount (e.g., extra zero) | High | Investor sees wrong balance, triggers distrust | **Mitigation**: Confirmation step with summary shown to user before commit. Also, accountant/admin can edit transactions; investor notified immediately. |
| Investor account compromised (Telegram account hacked) | Medium | Attacker sees investor's full financial data | **Mitigation**: Regular password hygiene reminders; Telegram's 2FA recommended. Consider added PIN for sensitive views later. |
| Database corruption / crash | Low | Data loss or inconsistency | **Mitigation**: Automated daily backups to S3; replicated PostgreSQL standby. RPO: 1 day. |
| Telegram bot token leaked | Low | Attacker can hijack bot messages | **Mitigation**: Token stored in environment variable; rotated every 6 months. Log all API calls for audit trail. |
| High concurrent load (all 60 users check balance at once) | Very Low (UI doesn't encourage surge requests) | Async queue fills; delayed responses | **Mitigation**: Async dispatch queue; horizontal scaling of bot replicas possible (stateless bot design). |
| Investor in Iran can't access Telegram bot due to filtering | Medium (regional risk) | User abandonment | **Note**: Known constraint; users must use VPN/Proxy. Document clearly in onboarding. |

## Migration Plan

### Phase 1: Staging Deployment (Week 1-2)
- Deploy bot to staging environment with test database
- Invite 5-10 beta testers (mix of investor, accountant, admin personas)
- Test transaction flows, notifications, edge cases
- Collect feedback on UX

### Phase 2: Soft Launch (Week 3)
- Deploy to production
- Invite just the accountant and admin to use; no investors yet
- Validate transaction flows, data integrity
- Load test with synthetic transactions

### Phase 3: Investor Rollout (Week 4+)
- Roll out in waves: batch of 10-15 investors every 2-3 days
- Monitor support tickets for issues
- Fix bugs quickly with hotfix releases
- Gradual ramp to full 60-user base over 2-3 weeks

### Rollback Plan
If critical issue discovered post-launch:
1. Kill bot webhook (stop accepting messages)
2. Restore database from backup
3. Deploy previous stable bot version
4. Notify users of issue + ETA for fix

Data rollback SLA: <15 minutes.

## Open Questions

1. **Dividend calculation automaticity**: Should the system auto-add 8% monthly dividend each month, or does admin manually input it?
   - Currently assumed: admin manually inputs via "Update Valuation" feature
   - Alternative: Cron job auto-applies monthly sums (more automation; less control)

2. **Mid-month deposit logic**: If investor deposits mid-month, how is that month's dividend calculated?
   - Currently assumed: admin manually computes the pro-rata dividend and inputs final balance
   - Alternative: System auto-calculates pro-rata (complex formula)

3. **Edit/Delete Transaction UX**: Can accountant/admin delete/edit a transaction after it's recorded?
   - Currently assumed: Yes; full edit capability with audit trail (new transaction record for audit)
   - Alternative: No deletion; only adds new records (append-only audit log)

4. **Multiple Admin Support**: Will there be multiple admins or just Dr. X?
   - Currently assumed: Just one admin + one accountant
   - Alternative: Support multiple admins with concurrent edits (needs conflict resolution)

5. **Performance SLA**: What's acceptable response time for investor to see balance update?
   - Currently assumed: <1 second (achievable with PostgreSQL on fast infra)
   - Alternative: <5 seconds (relaxed SLA for cheaper hosting)
