import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

# Подключение к базе данных PostgreSQL
db = psycopg2.connect(
    host="127.0.0.1",
    user="postgres",
    password="root",
    dbname="ParkingSystem"
)

cursor = db.cursor()

# Функции для работы с базой данных
def register_vehicle(license_plate, vehicle_type):
    try:
        query = "INSERT INTO Vehicles (LicensePlate, VehicleType) VALUES (%s, %s)"
        cursor.execute(query, (license_plate, vehicle_type))
        db.commit()
        messagebox.showinfo("Успех", "Автомобиль зарегистрирован успешно.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

def register_entry(self, vehicle_id, slot_number):
    try:
        cursor.execute("SELECT SlotID FROM ParkingSlots WHERE SlotNumber = %s AND IsOccupied = FALSE", (slot_number,))
        slot = cursor.fetchone()
        if slot:
            slot_id = slot[0]
            entry_time = datetime.now()

            query = "INSERT INTO ParkingTransactions (VehicleID, SlotID, EntryTime) VALUES (%s, %s, %s)"
            cursor.execute(query, (vehicle_id, slot_id, entry_time))

            update_query = "UPDATE ParkingSlots SET IsOccupied = TRUE WHERE SlotID = %s"
            cursor.execute(update_query, (slot_id,))
            db.commit()

            self.update_slots_info()  # Добавляет обновление информации о парковочных местах

            messagebox.showinfo("Успех", f"Автомобиль {vehicle_id} припаркован на месте {slot_number}.")
        else:
            messagebox.showerror("Ошибка", "Свободных мест нет.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

def register_exit(self, vehicle_id):
    try:
        cursor.execute("SELECT TransactionID, SlotID, EntryTime FROM ParkingTransactions WHERE VehicleID = %s AND ExitTime IS NULL", (vehicle_id,))
        transaction = cursor.fetchone()
        if transaction:
            transaction_id, slot_id, entry_time = transaction
            exit_time = datetime.now()
            duration = (exit_time - entry_time).total_seconds() / 3600
            amount = duration * 100  # Цена за час - 100 у.е.

            update_query = "UPDATE ParkingTransactions SET ExitTime = %s, Amount = %s WHERE TransactionID = %s"
            cursor.execute(update_query, (exit_time, amount, transaction_id))

            update_slot_query = "UPDATE ParkingSlots SET IsOccupied = FALSE WHERE SlotID = %s"
            cursor.execute(update_slot_query, (slot_id,))
            db.commit()

            self.update_slots_info()  # Обновляет информацию о парковочных местах

            messagebox.showinfo("Успех", f"Автомобиль {vehicle_id} выехал. Сумма к оплате: {amount:.2f}")
        else:
            messagebox.showerror("Ошибка", "Автомобиль не найден или уже выехал.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")


class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парковочная система")

        self.tab_control = ttk.Notebook(root)

        self.register_vehicle_tab = tk.Frame(self.tab_control)
        self.entry_tab = tk.Frame(self.tab_control)
        self.exit_tab = tk.Frame(self.tab_control)
        self.parking_slots_tab = tk.Frame(self.tab_control)

        self.tab_control.add(self.register_vehicle_tab, text="Регистрация авто")
        self.tab_control.add(self.entry_tab, text="Въезд авто")
        self.tab_control.add(self.exit_tab, text="Выезд авто")
        self.tab_control.add(self.parking_slots_tab, text="Информация о парковке")

        self.tab_control.pack(expand=1, fill="both")

        # Форма регистрации авто
        tk.Label(self.register_vehicle_tab, text="Номер автомобиля:").grid(row=0, column=0, padx=10, pady=10)
        self.license_plate_entry = tk.Entry(self.register_vehicle_tab)
        self.license_plate_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.register_vehicle_tab, text="Тип автомобиля:").grid(row=1, column=0, padx=10, pady=10)
        self.vehicle_type_entry = tk.Entry(self.register_vehicle_tab)
        self.vehicle_type_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.register_vehicle_tab, text="Зарегистрировать", command=self.register_vehicle_click).grid(row=2, column=0, columnspan=2, pady=10)

        # Форма въезда авто
        tk.Label(self.entry_tab, text="ID автомобиля:").grid(row=0, column=0, padx=10, pady=10)
        self.vehicle_id_entry_entry = tk.Entry(self.entry_tab)
        self.vehicle_id_entry_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.entry_tab, text="Номер парковочного места:").grid(row=1, column=0, padx=10, pady=10)
        self.slot_number_entry = tk.Entry(self.entry_tab)
        self.slot_number_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.entry_tab, text="Зарегистрировать въезд", command=self.register_entry_click).grid(row=2, column=0, columnspan=2, pady=10)

        # Форма выезда авто
        tk.Label(self.exit_tab, text="ID автомобиля:").grid(row=0, column=0, padx=10, pady=10)
        self.vehicle_id_exit_entry = tk.Entry(self.exit_tab)
        self.vehicle_id_exit_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(self.exit_tab, text="Зарегистрировать выезд", command=self.register_exit_click).grid(row=1, column=0, columnspan=2, pady=10)

        # Таблица с информацией о парковочных местах
        self.slots_tree = ttk.Treeview(self.parking_slots_tab, columns=("SlotNumber", "Status", "VehicleID", "LicensePlate"), show="headings")
        self.slots_tree.heading("SlotNumber", text="Номер места")
        self.slots_tree.heading("Status", text="Статус")
        self.slots_tree.heading("VehicleID", text="ID автомобиля")
        self.slots_tree.heading("LicensePlate", text="Номер автомобиля")

        self.slots_tree.grid(row=0, column=0, padx=10, pady=10)
        self.update_slots_info()

    def update_slots_info(self):
        # Очистка таблицы
        for row in self.slots_tree.get_children():
            self.slots_tree.delete(row)

        try:
            query = """
                SELECT ps.SlotNumber, ps.IsOccupied, v.VehicleID, v.LicensePlate
                FROM ParkingSlots ps
                LEFT JOIN Vehicles v ON ps.SlotID = v.VehicleID
            """
            cursor.execute(query)
            slots = cursor.fetchall()

            for slot in slots:
                slot_number, is_occupied, vehicle_id, license_plate = slot
                status = "Занято" if is_occupied else "Свободно"
                self.slots_tree.insert("", "end", values=(slot_number, status, vehicle_id, license_plate))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных о парковочных местах: {e}")
    def register_vehicle_click(self):
        license_plate = self.license_plate_entry.get()
        vehicle_type = self.vehicle_type_entry.get()
        if license_plate and vehicle_type:
            register_vehicle(license_plate, vehicle_type)
        else:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")

    def register_entry_click(self):
        vehicle_id = self.vehicle_id_entry_entry.get()
        slot_number = self.slot_number_entry.get()
        if vehicle_id.isdigit() and slot_number:
            register_entry(self, int(vehicle_id), slot_number)
            self.update_slots_info()
        else:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены и ID автомобиля должен быть числом.")

    def register_exit_click(self):
        vehicle_id = self.vehicle_id_exit_entry.get()
        if vehicle_id.isdigit():
            register_exit(self, int(vehicle_id))
            self.update_slots_info()
        else:
            messagebox.showerror("Ошибка", "ID автомобиля должен быть числом.")

        def update_slots_info(self):
            # Очистка таблицы
            for row in self.slots_tree.get_children():
                self.slots_tree.delete(row)

            try:
                query = """
                    SELECT ps.SlotNumber, ps.IsOccupied, v.VehicleID, v.LicensePlate
                    FROM ParkingSlots ps
                    LEFT JOIN Vehicles v ON ps.VehicleID = v.VehicleID
                """
                cursor.execute(query)
                slots = cursor.fetchall()

                for slot in slots:
                    slot_number, is_occupied, vehicle_id, license_plate = slot
                    status = "Занято" if is_occupied else "Свободно"
                    self.slots_tree.insert("", "end", values=(slot_number, status, vehicle_id, license_plate))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении данных о парковочных местах: {e}")

root = tk.Tk()
app = ParkingApp(root)
root.mainloop()

# Закрытие соединения с базой данных при завершении работы
cursor.close()
db.close()



