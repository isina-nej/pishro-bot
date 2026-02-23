from aiogram.fsm.state import State, StatesGroup


class AuthFSM(StatesGroup):
    """States for authentication flow."""
    waiting_phone_verify = State()


class TransactionFSM(StatesGroup):
    """States for transaction recording flow."""
    waiting_investor_selection = State()
    waiting_transaction_type = State()
    waiting_amount_input = State()
    waiting_date_input = State()
    waiting_description_input = State()
    waiting_confirmation = State()


class ValuationFSM(StatesGroup):
    """States for portfolio valuation update flow."""
    waiting_investor_selection = State()
    waiting_update_mode = State()  # Absolute value or percentage
    waiting_value_input = State()
    waiting_reason_input = State()
    waiting_confirmation = State()


class SearchFSM(StatesGroup):
    """States for investor search flow."""
    waiting_search_query = State()
    waiting_selection = State()


class UserManagementFSM(StatesGroup):
    """States for user management (admin)."""
    waiting_action = State()
    waiting_user_input = State()
    waiting_role_input = State()
    waiting_confirmation = State()


class SettingsFSM(StatesGroup):
    """States for user settings."""
    waiting_setting_choice = State()
    waiting_setting_value = State()
