from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import timedelta


from core.models import User, Worker, Category, Transaction
from core.analytics import get_expense_summary, get_income_summary, format_categories, get_worker_summary
from bot.states import AddTransaction

from bot.configuration import ADMIN_URL


router = Router()

def get_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Добавить 📝", callback_data="add_transaction")
    kb.button(text="Отчет 📊", callback_data="get_report")
    return kb.as_markup()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Отменено", reply_markup=get_main_keyboard())
    await callback.answer()  


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного процесса для отмены.")
        return
    
    await state.clear()
    await message.answer("Отменено", reply_markup=get_main_keyboard())


@router.message(Command("start"))
async def start_command(message:Message):
    await User.objects.aget_or_create(
        user_id=message.from_user.id,
        defaults={"name": message.from_user.full_name},
    )
    await message.answer("Money, money, don't be funny", reply_markup=get_main_keyboard())


@router.message(Command("admin"))
async def admin_link(message: Message):
    await message.answer(f"Админ панель: {ADMIN_URL}")


@router.callback_query(F.data == "add_transaction")
async def add_transaction(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Доход ➕", callback_data="type_income")
    kb.button(text="Расход ➖", callback_data="type_expense")
    kb.button(text="Отмена ❌", callback_data="cancel")

    await state.set_state(AddTransaction.waiting_for_type)
    await callback.message.edit_text("Выберите тип операции:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(AddTransaction.waiting_for_type, F.data.startswith("type_"))
async def process_type(callback: CallbackQuery, state: FSMContext):
    transaction_type = callback.data.removeprefix("type_")
    await state.update_data(type=transaction_type)

    await state.set_state(AddTransaction.waiting_for_category)
    
    kb = InlineKeyboardBuilder()
    
    categories = [cat async for cat in Category.objects.filter(type=transaction_type)]
    for category in categories:
        kb.button(text=category.name, callback_data=f"category_{category.id}")
    
    kb.button(text="Отмена ❌", callback_data="cancel")
    kb.adjust(2)

    await callback.message.edit_text("Введите категорию:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(AddTransaction.waiting_for_category, F.data.startswith("category_"))
async def category_process(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.removeprefix("category_")
    category = await Category.objects.aget(id=category_id)
    await state.update_data(category=category.id)

    if category.name == "Зарплата":
        workers = [w async for w in Worker.objects.all()]
        kb = InlineKeyboardBuilder()
        for worker in workers:
            kb.button(text=worker.name, callback_data=f"worker_{worker.id}")
        kb.button(text="Отмена ❌", callback_data="cancel")
        kb.adjust(3)

        await state.set_state(AddTransaction.waiting_for_worker)
        await callback.message.edit_text("Выберите сотрудника:", reply_markup=kb.as_markup())
        await callback.answer()
        return

    await state.set_state(AddTransaction.waiting_for_amount)
    await callback.message.edit_text("Укажите сумму:")
    await callback.answer()


@router.callback_query(AddTransaction.waiting_for_worker, F.data.startswith("worker_"))
async def worker_process(callback: CallbackQuery, state: FSMContext):
    worker_id = callback.data.removeprefix("worker_")
    worker = await Worker.objects.aget(id=worker_id)

    await state.update_data(worker=worker.id)
    await state.set_state(AddTransaction.waiting_for_amount)
    await callback.message.edit_text("Введите сумму:")
    await callback.answer()


@router.message(AddTransaction.waiting_for_amount)
async def amount_process(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Ошибка, используйте числа")
        return
    
    await state.update_data(amount=amount)
    await state.set_state(AddTransaction.waiting_for_comment)
    await message.answer("Добавьте комментарий")


@router.message(AddTransaction.waiting_for_comment)
async def comment_process(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(AddTransaction.waiting_for_checking)

    data = await state.get_data()
    category = await Category.objects.aget(id=data["category"])

    worker_line = ""
    if data.get("worker"):
        worker = await Worker.objects.aget(id=data["worker"])
        worker_line = f"Сотрудник: {worker.name}\n"

    summary = (
        f"Тип: {category.get_type_display()}\n"
        f"Категория: {category.name}\n"
        f"{worker_line}"
        f"Сумма: {data['amount']}\n"
        f"Комментарий: {data['comment']}\n\n"
        f"Всё верно?"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="OK", callback_data="ok")
    kb.button(text="Отмена", callback_data="cancel")

    await message.answer(summary, reply_markup=kb.as_markup())


@router.callback_query(AddTransaction.waiting_for_checking, F.data == "ok")
async def check_process(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await User.objects.aget(user_id=callback.from_user.id)

    worker = None
    if data.get("worker"):
        worker = await Worker.objects.aget(id=data["worker"])

    await Transaction.objects.acreate(
        user=user,
        category_id=data["category"],
        worker=worker,
        amount=data["amount"],
        comment=data.get("comment"),
    )

    await state.clear()
    await callback.message.edit_text("Записано ✅", reply_markup=get_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "get_report")
async def get_report(callback: CallbackQuery, state: FSMContext):

    kb = InlineKeyboardBuilder()
    kb.button(text="7 дней", callback_data="report_weekly")
    kb.button(text="30 дней", callback_data="report_monthly")

    await state.set_state(AddTransaction.waiting_for_report)
    await callback.message.edit_text("Выберите период отчета", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(AddTransaction.waiting_for_report, F.data.startswith("report_"))
async def report_process(callback: CallbackQuery, state:FSMContext):

    period = callback.data.removeprefix("report_")

    if period == "weekly":
        try:
            expense_report = await get_expense_summary(timedelta(days=7))
            income_report = await get_income_summary(timedelta(days=7)) 
            worker_report = await get_worker_summary(timedelta(days=7))

        except Exception as e:
            print(f"Ошибка при получении отчёта за неделю: {e}")
            await callback.message.edit_text("Ошибка получения данных")
            return
        
    else:
        try:
            expense_report = await get_expense_summary(timedelta(days=30))
            income_report = await get_income_summary(timedelta(days=30)) 
            worker_report = await get_worker_summary(timedelta(days=30))

        except Exception as e:
            print(f"Ошибка при получении отчёта за месяц: {e}")
            await callback.message.edit_text("Ошибка получения данных")
            return
        
    income_categories_text = format_categories(income_report["by_category"])
    expense_categories_text = format_categories(expense_report["by_category"])
    worker_salary_text = format_categories(worker_report)

    report_text = (
        f"Отчёт 📊 за {'7 дней' if period == 'weekly' else '30 дней'}\n\n"
        f"Доход 📈: {income_report['total']:.0f}\n{income_categories_text}\n\n"
        f"Расход 📉: {expense_report['total']:.0f}\n{expense_categories_text}\n\n"
        f"Прибыль 💸: {int(income_report['total']) - int(expense_report['total']):.0f}\n\n"
        f"Зарплата сотрудников: \n{worker_salary_text}\n"
    )
        
    await state.clear()
    await callback.message.edit_text(report_text, reply_markup=get_main_keyboard())
    await callback.answer()














