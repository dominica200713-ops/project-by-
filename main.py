import tkinter as tk
from tkinter import messagebox, ttk


# часть софьи

# блок 1. запись об одном расходе


class Expense:
    def __init__(self, day, amount, category):
        # сохраняем день, сумму и категорию расхода
        self.day = day
        self.amount = amount
        self.category = category


# блок 2. узел бинарного дерева


class TreeNode:
    def __init__(self, day, expense):
        # ключом узла служит день месяца
        self.day = day

        # в одном узле хранятся все расходы за этот день
        self.expenses = [expense]

        # ссылки на левую и правую ветви дерева
        self.left = None
        self.right = None


# блок 3. бинарное дерево расходов


class ExpenseTree:
    def __init__(self):
        # сначала дерево пустое
        self.root = None

    def add(self, expense):
        # запускаем рекурсивное добавление от корня
        self.root = self._add_recursive(self.root, expense)

    def _add_recursive(self, node, expense):
        # создаем новый узел для нового дня
        if node is None:
            return TreeNode(expense.day, expense)

        # меньший день добавляем в левую ветвь
        if expense.day < node.day:
            node.left = self._add_recursive(node.left, expense)

        # больший день добавляем в правую ветвь
        elif expense.day > node.day:
            node.right = self._add_recursive(node.right, expense)

        # расход за существующий день добавляем в список узла
        else:
            node.expenses.append(expense)
        return node

    def get_in_order(self):
        # создаем список для результата обхода
        result = []

        # запускаем рекурсивный обход дерева
        self._walk_recursive(self.root, result)
        return result

    def _walk_recursive(self, node, result):
        # пустая ветвь завершает текущий вызов
        if node is None:
            return

        # обходим левую ветвь, узел и правую ветвь
        self._walk_recursive(node.left, result)
        result.append((node.day, node.expenses))
        self._walk_recursive(node.right, result)


# блок 4. основная логика бюджетного помощника


class Budget:
    def __init__(self):
        # создаем массив расходов по 31 дню месяца
        self.daily_expenses = [0.0] * 31

        # создаем общий список всех расходов
        self.expenses = []

        # создаем стек для отмены последнего расхода
        self.undo_stack = []

        # создаем массив префиксных сумм с нулевым элементом
        self.prefix = [0.0] * 32

        # создаем бинарное дерево расходов
        self.tree = ExpenseTree()

    def add_expense(self, day, amount, category):
        # создаем объект нового расхода
        expense = Expense(day, amount, category)

        # добавляем расход в общий список
        self.expenses.append(expense)

        # добавляем расход в стек
        self.undo_stack.append(expense)

        # увеличиваем сумму расходов нужного дня
        self.daily_expenses[day - 1] += amount

        # добавляем расход в бинарное дерево
        self.tree.add(expense)

        # обновляем префиксные суммы
        self.build_prefix()
        return expense

    def undo_last(self):
        # проверяем, есть ли расход для отмены
        if not self.undo_stack:
            return None

        # берем последний расход из стека
        expense = self.undo_stack.pop()

        # удаляем расход из общего списка
        self.expenses.remove(expense)

        # вычитаем сумму из нужного дня
        self.daily_expenses[expense.day - 1] -= expense.amount
        if abs(self.daily_expenses[expense.day - 1]) < 0.000001:
            self.daily_expenses[expense.day - 1] = 0.0

        # пересоздаем дерево после удаления расхода
        self.tree = ExpenseTree()
        for saved_expense in self.expenses:
            self.tree.add(saved_expense)

        # обновляем префиксные суммы после отмены
        self.build_prefix()
        return expense

    def build_prefix(self):
        # первый элемент нужен для удобной формулы периода
        self.prefix[0] = 0.0

        # считаем накопленную сумму от первого дня
        for index in range(31):
            self.prefix[index + 1] = (
                self.prefix[index] + self.daily_expenses[index]
            )

    def period_sum(self, start_day, end_day):
        # считаем сумму за период по двум элементам массива
        # формула работает за o(1)
        return self.prefix[end_day] - self.prefix[start_day - 1]

    def find_max_day(self):
        # готовим переменные для линейного поиска
        has_expenses = False
        best_day = 0
        best_amount = 0.0

        # просматриваем каждый день только один раз
        for index in range(31):
            current_amount = self.daily_expenses[index]
            if current_amount > 0:
                if not has_expenses or current_amount > best_amount:
                    has_expenses = True
                    best_day = index + 1
                    best_amount = current_amount

        # сообщаем об отсутствии расходов
        if not has_expenses:
            return None
        return best_day, best_amount

    def categories_by_amount(self):
        # создаем словарь сумм по категориям
        totals = {}

        # собираем общую сумму каждой категории
        for expense in self.expenses:
            if expense.category not in totals:
                totals[expense.category] = 0.0
            totals[expense.category] += expense.amount

        # переносим категории в список для сортировки
        categories = []
        for category in totals:
            categories.append([category, totals[category]])

        # сортируем категории вставками по убыванию суммы
        for index in range(1, len(categories)):
            current = categories[index]
            position = index - 1

            # сдвигаем меньшие суммы вправо
            while position >= 0 and categories[position][1] < current[1]:
                categories[position + 1] = categories[position]
                position -= 1

            # вставляем текущую категорию на нужное место
            categories[position + 1] = current
        return categories


# часть доминики

# блок 5. главное окно программы


class BudgetHelperApp:
    def __init__(self, root):
        # сохраняем окно и создаем объект бюджета
        self.root = root
        self.budget = Budget()

        # задаем голубую цветовую гамму
        self.background = "#e8f4ff"
        self.panel = "#d4eaff"
        self.blue = "#1976d2"
        self.dark_blue = "#0d47a1"
        self.text_color = "#15324b"

        # настраиваем размер и заголовок окна
        self.root.title("Бюджетный помощник")
        self.root.geometry("980x700")
        self.root.minsize(900, 620)
        self.root.configure(bg=self.background)

        # создаем стили и элементы интерфейса
        self._configure_styles()
        self._create_interface()

    def _configure_styles(self):
        # настраиваем внешний вид кнопок и таблицы
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Blue.TButton",
            background=self.blue,
            foreground="white",
            font=("Arial", 10, "bold"),
            padding=8,
            borderwidth=0,
        )
        style.map(
            "Blue.TButton",
            background=[("active", self.dark_blue)],
        )
        style.configure(
            "Expense.Treeview",
            rowheight=27,
            font=("Arial", 10),
            fieldbackground="white",
        )
        style.configure(
            "Expense.Treeview.Heading",
            background=self.blue,
            foreground="white",
            font=("Arial", 10, "bold"),
        )

    def _create_interface(self):
        # создаем заголовок программы
        title = tk.Label(
            self.root,
            text="Бюджетный помощник",
            bg=self.background,
            fg=self.dark_blue,
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=(16, 10))

        # создаем общий контейнер для четырех блоков
        main_frame = tk.Frame(self.root, bg=self.background)
        main_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # создаем верхние блоки ввода и анализа
        input_frame = self._create_panel(main_frame, "Добавление расхода")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        query_frame = self._create_panel(main_frame, "Анализ расходов")
        query_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))

        self._create_expense_inputs(input_frame)
        self._create_query_inputs(query_frame)

        # создаем нижние блоки списка и результата
        list_frame = self._create_panel(main_frame, "Список расходов")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        result_frame = self._create_panel(main_frame, "Результат")
        result_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        self._create_expense_list(list_frame)
        self._create_result_box(result_frame)

    def _create_panel(self, parent, title):
        # создаем отдельный подписанный блок интерфейса
        frame = tk.LabelFrame(
            parent,
            text=title,
            bg=self.panel,
            fg=self.dark_blue,
            font=("Arial", 11, "bold"),
            padx=12,
            pady=12,
            relief="groove",
            bd=1,
        )
        return frame

    def _create_labeled_entry(self, parent, label, row, column):
        # создаем подпись над полем
        tk.Label(
            parent,
            text=label,
            bg=self.panel,
            fg=self.text_color,
            font=("Arial", 10),
        ).grid(row=row, column=column, sticky="w", padx=4, pady=4)

        # создаем белое поле ввода
        entry = tk.Entry(
            parent,
            bg="white",
            fg=self.text_color,
            font=("Arial", 10),
            relief="solid",
            bd=1,
        )
        entry.grid(row=row + 1, column=column, sticky="ew", padx=4, pady=(0, 8))
        return entry

    def _create_expense_inputs(self, parent):
        # распределяем ширину полей добавления расхода
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=2)

        # создаем поля дня, суммы и категории
        self.day_entry = self._create_labeled_entry(parent, "День (1–31)", 0, 0)
        self.amount_entry = self._create_labeled_entry(parent, "Сумма, руб.", 0, 1)
        self.category_entry = self._create_labeled_entry(parent, "Категория", 0, 2)

        # создаем кнопки добавления и отмены
        ttk.Button(
            parent,
            text="Добавить расход",
            command=self.add_expense,
            style="Blue.TButton",
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        ttk.Button(
            parent,
            text="Отменить последний расход",
            command=self.undo_last,
            style="Blue.TButton",
        ).grid(row=2, column=2, sticky="ew", padx=4, pady=(4, 0))

    def _create_query_inputs(self, parent):
        # распределяем ширину полей периода
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # создаем поля начала и конца периода
        self.start_entry = self._create_labeled_entry(
            parent, "Начало периода", 0, 0
        )
        self.end_entry = self._create_labeled_entry(parent, "Конец периода", 0, 1)

        # задаем названия и обработчики кнопок анализа
        buttons = [
            ("Посчитать сумму за период", self.calculate_period),
            ("Найти день с максимальным расходом", self.show_max_day),
            ("Показать категории по сумме", self.show_categories),
            ("Показать дерево расходов", self.show_tree),
        ]

        # создаем кнопки анализа в двух столбцах
        for index, (text, command) in enumerate(buttons):
            ttk.Button(
                parent,
                text=text,
                command=command,
                style="Blue.TButton",
            ).grid(
                row=2 + index // 2,
                column=index % 2,
                sticky="ew",
                padx=4,
                pady=4,
            )

    def _create_expense_list(self, parent):
        # растягиваем таблицу по размеру блока
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # создаем таблицу из трех столбцов
        columns = ("day", "amount", "category")
        self.expense_table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Expense.Treeview",
        )
        self.expense_table.heading("day", text="День")
        self.expense_table.heading("amount", text="Сумма")
        self.expense_table.heading("category", text="Категория")
        self.expense_table.column("day", width=55, anchor="center")
        self.expense_table.column("amount", width=100, anchor="e")
        self.expense_table.column("category", width=170, anchor="w")

        # добавляем вертикальную полосу прокрутки
        scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.expense_table.yview
        )
        self.expense_table.configure(yscrollcommand=scrollbar.set)
        self.expense_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_result_box(self, parent):
        # растягиваем поле результата по размеру блока
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # создаем многострочное поле результата
        self.result_text = tk.Text(
            parent,
            wrap="word",
            bg="white",
            fg=self.text_color,
            font=("Arial", 11),
            relief="solid",
            bd=1,
            padx=10,
            pady=10,
            state="disabled",
        )

        # добавляем вертикальную полосу прокрутки
        scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _read_day(self, value, field_name):
        # проверяем, что пользователь ввел целое число
        try:
            day = int(value)
        except ValueError:
            raise ValueError(f'Поле «{field_name}» должно содержать целое число.')

        # проверяем границы дня месяца
        if day < 1 or day > 31:
            raise ValueError(f'Поле «{field_name}» должно быть от 1 до 31.')
        return day

    def _format_amount(self, amount):
        # выводим сумму с двумя знаками после запятой
        return f"{amount:.2f} руб."

    def _show_result(self, text):
        # выводим результат
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def add_expense(self):
        # читаем и проверяем данные нового расхода
        try:
            day = self._read_day(self.day_entry.get().strip(), "День")
            amount_text = self.amount_entry.get().strip().replace(",", ".")
            try:
                amount = float(amount_text)
            except ValueError:
                raise ValueError("Сумма должна быть числом.")
            if amount <= 0:
                raise ValueError("Сумма должна быть положительным числом.")
            category = self.category_entry.get().strip()
            if not category:
                raise ValueError("Категория не должна быть пустой.")
        except ValueError as error:
            messagebox.showerror("Ошибка ввода", str(error))
            return

        # добавляем проверенный расход в бюджет
        expense = self.budget.add_expense(day, amount, category)

        # обновляем таблицу и очищаем поля
        self.update_expense_list()
        self.day_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.day_entry.focus_set()

        # показываем сообщение о добавлении
        self._show_result(
            "Расход добавлен:\n"
            f"день {expense.day}, {self._format_amount(expense.amount)}, "
            f"категория «{expense.category}»."
        )

    def undo_last(self):
        # пытаемся взять последний расход из стека
        expense = self.budget.undo_last()
        if expense is None:
            messagebox.showinfo("Отмена", "Отменять нечего.")
            return

        # обновляем таблицу после отмены
        self.update_expense_list()
        self._show_result(
            "Последний расход отменён:\n"
            f"день {expense.day}, {self._format_amount(expense.amount)}, "
            f"категория «{expense.category}»."
        )

    def calculate_period(self):
        # читаем и проверяем границы периода
        try:
            start_day = self._read_day(
                self.start_entry.get().strip(), "Начало периода"
            )
            end_day = self._read_day(
                self.end_entry.get().strip(), "Конец периода"
            )
            if start_day > end_day:
                raise ValueError(
                    "Начало периода не должно быть больше конца периода."
                )
        except ValueError as error:
            messagebox.showerror("Ошибка ввода", str(error))
            return

        # получаем сумму через массив префиксных сумм
        amount = self.budget.period_sum(start_day, end_day)
        self._show_result(
            f"Расходы с {start_day} по {end_day} день:\n"
            f"{self._format_amount(amount)}"
        )

    def show_max_day(self):
        # запускаем линейный поиск максимального дня
        result = self.budget.find_max_day()
        if result is None:
            self._show_result("Данные о расходах отсутствуют.")
            return

        # выводим найденный день и сумму
        day, amount = result
        self._show_result(
            "День с максимальным расходом:\n"
            f"день {day}\n"
            f"сумма: {self._format_amount(amount)}"
        )

    def show_categories(self):
        # получаем категории после сортировки вставками
        categories = self.budget.categories_by_amount()
        if not categories:
            self._show_result("Данные о расходах отсутствуют.")
            return

        # собираем строки результата
        lines = ["Категории по убыванию суммы трат:", ""]
        for category, amount in categories:
            lines.append(f"{category} — {self._format_amount(amount)}")
        self._show_result("\n".join(lines))

    def show_tree(self):
        # получаем расходы рекурсивным обходом дерева
        nodes = self.budget.tree.get_in_order()
        if not nodes:
            self._show_result("Дерево расходов пусто.")
            return

        # собираем расходы по возрастанию дней
        lines = ["Дерево расходов по возрастанию дней:", ""]
        for day, expenses in nodes:
            lines.append(f"День {day}:")
            for expense in expenses:
                lines.append(
                    f"  • {expense.category}: "
                    f"{self._format_amount(expense.amount)}"
                )
            lines.append("")
        self._show_result("\n".join(lines))

    def update_expense_list(self):
        # удаляем старые строки таблицы
        for item in self.expense_table.get_children():
            self.expense_table.delete(item)

        # добавляем в таблицу актуальные расходы
        for expense in self.budget.expenses:
            self.expense_table.insert(
                "",
                tk.END,
                values=(
                    expense.day,
                    f"{expense.amount:.2f}",
                    expense.category,
                ),
            )


# блок 6. запуск приложения


def main():
    # создаем главное окно
    root = tk.Tk()

    # создаем интерфейс бюджетного помощника
    BudgetHelperApp(root)

    # запускаем цикл обработки событий
    root.mainloop()


# запускаем программу только из файла main.py
if __name__ == "__main__":
    main()
