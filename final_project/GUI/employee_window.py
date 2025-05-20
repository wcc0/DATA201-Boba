import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QMessageBox, QComboBox, QDateEdit, QDialog, QTableWidgetItem, QHeaderView)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from mysql.connector import MySQLConnection
from data201 import make_connection, dataframe_query


class EmployeeDialog(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Operations Portal")
        self.setGeometry(150, 150, 400, 400)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Customer Name:"))
        self.cus_name_input = QLineEdit()
        layout.addWidget(self.cus_name_input)

        layout.addWidget(QLabel("Payment Method:"))
        self.pay_name_dropdown = QComboBox()
        self.pay_name_dropdown.addItems(["Credit Card", "Cash", "Debit Card", "PayPal", "Apple Pay", "Venmo"])
        layout.addWidget(self.pay_name_dropdown)

        layout.addWidget(QLabel("Tea:"))
        self.tea_dropdown = QComboBox()
        self.load_tea_dropdown()
        self.tea_dropdown.currentIndexChanged.connect(self.calculate_price)
        layout.addWidget(self.tea_dropdown)

        layout.addWidget(QLabel("Topping:"))
        self.topping_dropdown = QComboBox()
        self.load_topping_dropdown()
        self.topping_dropdown.currentIndexChanged.connect(self.calculate_price)
        layout.addWidget(self.topping_dropdown)

        layout.addWidget(QLabel("Employee ID:"))
        self.emp_id_input = QLineEdit()
        layout.addWidget(self.emp_id_input)

        layout.addWidget(QLabel("Order Date:"))
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.order_date_input)

        layout.addWidget(QLabel("Total Price:"))
        self.total_price_label = QLabel("0.00")
        layout.addWidget(self.total_price_label)

        add_order_btn = QPushButton("Add Order")
        add_order_btn.clicked.connect(self.add_order)
        layout.addWidget(add_order_btn)

        self.setLayout(layout)

    def load_tea_dropdown(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT tea_id, tea_name, tea_price FROM Tea")
        teas = cursor.fetchall()
        for tea in teas:
            self.tea_dropdown.addItem(f"{tea[1]} - ${tea[2]}", (tea[0], tea[2]))
        cursor.close()

    def load_topping_dropdown(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT topping_id, topping_name, topping_price FROM Topping")
        toppings = cursor.fetchall()
        for topping in toppings:
            self.topping_dropdown.addItem(f"{topping[1]} - ${topping[2]}", (topping[0], topping[2]))
        cursor.close()

    def calculate_price(self):
        try:
            tea_data = self.tea_dropdown.currentData()
            topping_data = self.topping_dropdown.currentData()

            if tea_data and topping_data:
                tea_price = tea_data[1]
                topping_price = topping_data[1]
                total_price = tea_price + topping_price
                self.total_price_label.setText(f"{total_price:.2f}")
            else:
                self.total_price_label.setText("0.00")

        except Exception as e:
            self.total_price_label.setText("0.00")

    def add_order(self):
        try:
            cus_name = self.cus_name_input.text()
            pay_name = self.pay_name_dropdown.currentText()
            tea_data = self.tea_dropdown.currentData()
            topping_data = self.topping_dropdown.currentData()
            emp_id = self.emp_id_input.text()
            order_date = self.order_date_input.text()

            if not tea_data or not topping_data:
                raise Exception("Please select both a tea and a topping.")

            tea_id = tea_data[0]
            tea_price = tea_data[1]
            topping_id = topping_data[0]
            topping_price = topping_data[1]

            total_price = tea_price + topping_price

            cursor = self.db_connection.cursor()
            cursor.execute("BEGIN")
            
            # Insert the new customer and retrieve the generated cus_id
            cursor.execute("INSERT INTO Customer (cus_name, pay_name) VALUES (%s, %s)", (cus_name, pay_name))
            cus_id = cursor.lastrowid

            cursor.execute("INSERT INTO Orders (cus_id, order_date, emp_id, total_price) VALUES (%s, %s, %s, %s)", 
                           (cus_id, order_date, emp_id, total_price))
            order_id = cursor.lastrowid

            cursor.execute("INSERT INTO OrderDetails (order_id, tea_id, topping_id) VALUES (%s, %s, %s)", 
                           (order_id, tea_id, topping_id))
            self.db_connection.commit()

            cursor.close()

            QMessageBox.information(self, "Success", "Order added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add order: {e}")



