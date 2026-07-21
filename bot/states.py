from aiogram.fsm.state import State, StatesGroup


class AddTransaction(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()
    waiting_for_worker = State()
    waiting_for_amount = State()
    waiting_for_comment = State()
    waiting_for_checking = State()
    waiting_for_report = State()