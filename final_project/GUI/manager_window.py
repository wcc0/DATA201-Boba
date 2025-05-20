import sys
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QApplication, QRadioButton, QWidget, QTableWidgetItem, QHeaderView, QVBoxLayout
from data201 import make_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ManagerDialog(QDialog):
    """
    The manager dialog
    """
    
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('manager_window.ui')

        # Page 1
        # Populate the popular_list drop down menu 
        self.add_items_to_popular_list()
        
        self.ui.popular_menu.currentIndexChanged.connect(self.populate_list)

        # Page 2
        # Populate the "from" drop down menu
        self.add_items_to_from_menu()
        self.add_items_to_to_menu()

        self.ui.day_button.toggled.connect(self.update_income_plot)
        self.ui.weekbutton.toggled.connect(self.update_income_plot)
        self.ui.month_button.toggled.connect(self.update_income_plot)

        self.setup_income_plot()

        # Page 3
        # Populate the employee pull down menu 
        self.add_items_to_employee_menu()
        self.ui.employee_menu.currentIndexChanged.connect(self._enter_employee_data)


    def setup_income_plot(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self.ui.graphic_layout)
        layout.addWidget(self.canvas)

        self.update_income_plot()

    def update_income_plot(self):
        """
        Update the income plot with data for daily, weekly, or monthly income.
        """
        
        selected_option = None
        if self.ui.day_button.isChecked():
            selected_option = "Day"
        elif self.ui.weekbutton.isChecked():
            selected_option = "Week"
        elif self.ui.month_button.isChecked():
            selected_option = "Month"

        from_date_str = self.ui.from_menu.currentText()
        to_date_str = self.ui.to_menu.currentText()

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
        except ValueError:
            return
        
        if from_date > to_date:
            pirnt('TO date must after FROM date')
            return

        # SQL query to fetch income data based on the selected option
        if selected_option == "Day":
            sql = f"""
            SELECT orders.order_date, SUM(tea.tea_price) AS income
            FROM orders
            JOIN tea
            ON tea.tea_name = orders.tea_name
            AND tea.topping = orders.topping
            WHERE orders.order_date BETWEEN '{from_date.strftime('%Y-%m-%d')}' AND '{to_date.strftime('%Y-%m-%d')}'
            GROUP BY order_date
            ORDER BY order_date;
            """
            x_label = 'Date'
            label_format = lambda row: str(row[0])
        elif selected_option == "Week":
            sql = f"""
            SELECT WEEK(orders.order_date) AS week, 
                    MIN(orders.order_date) AS week_start,
                    MAX(orders.order_date) AS week_end,
                    SUM(tea.tea_price) AS income
            FROM orders
            JOIN tea
            ON tea.tea_name = orders.tea_name
            AND tea.topping = orders.topping
            WHERE orders.order_date BETWEEN '{from_date.strftime('%Y-%m-%d')}' AND '{to_date.strftime('%Y-%m-%d')}'
            GROUP BY WEEK(order_date)
            ORDER BY week;
            """
            x_label = ''
            label_format = lambda row: f"Week of {row[1].strftime('%m-%d')}"
        elif selected_option == "Month":
            sql = f"""
            SELECT MONTH(orders.order_date) AS month, SUM(tea.tea_price) AS income
            FROM orders
            JOIN tea
            ON tea.tea_name = orders.tea_name
            AND tea.topping = orders.topping
            WHERE orders.order_date BETWEEN '{from_date.strftime('%Y-%m-%d')}' AND '{to_date.strftime('%Y-%m-%d')}'
            GROUP BY MONTH(order_date)
            ORDER BY month;
            """
            x_label = 'Month'
            label_format = lambda row:str(row[0])
        else:
            print("Invalid selection.")
            return
        
        # Execute the SQL query and fetch the data
        conn = make_connection(config_file='groupfour_db.ini')
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Prepare the data for plotting
        labels = [label_format(row) for row in rows]
        income = [row[-1] for row in rows]

        self.figure.clear()

        # Plot the data
        ax = self.figure.add_subplot(111)
        # ax.clear()  # Clear any previous plot

        ax.bar(labels, income, label="Income", color="#fcdeba", edgecolor = "gray")
        ax.set_title(f"{selected_option} Income from {from_date_str} to {to_date_str}")
        ax.set_xlabel(x_label)
        ax.set_ylabel("Income (k/$)")
        # ax.set_xticklabels(labels)
        ax.tick_params(axis = 'x')
        ax.tick_params(axis = 'y')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if selected_option == 'Month':
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels)
        elif selected_option == 'Day':
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation = 45, fontsize = 5)
        elif selected_option == 'Week':
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize = 7)           

        # Refresh the canvas
        self.canvas.draw()



    def add_items_to_popular_list(self):
        self.ui.popular_menu.addItem("Drink", "Drink")
        self.ui.popular_menu.addItem("Topping", "Topping")
    

    def add_items_to_from_menu(self):
        conn = make_connection(config_file='groupfour_db.ini')
        cursor = conn.cursor()
        
        sql = """
            SELECT DISTINCT order_date FROM orders
            ORDER BY order_date;
        """
        cursor.execute(sql)

        # Add items to the from_menu.
        for row in cursor.fetchall():
            self.ui.from_menu.addItem(str(row[0]))  

        cursor.close()
        conn.close()

        # Connect a slot to update the to_menu when the from_menu selection changes
        self.ui.from_menu.currentIndexChanged.connect(self.update_to_menu)

    def add_items_to_to_menu(self):
        # Get the selected from_date
        from_date_str = self.ui.from_menu.currentText()  # Get selected date from from_menu

        if not from_date_str:
            return  # If no from_date is selected, don't update to_menu

        from_date = datetime.strptime(from_date_str, '%Y-%m-%d')

        conn = make_connection(config_file='groupfour_db.ini')
        cursor = conn.cursor()
        
        # SQL query to get dates that are after the selected from_date
        sql = """
            SELECT DISTINCT order_date FROM orders
            WHERE order_date > %s
            ORDER BY order_date;
        """
        cursor.execute(sql, (from_date.strftime('%Y-%m-%d'),))

        # Clear the to_menu before adding new items
        self.ui.to_menu.clear()

        # Add valid items to the to_menu (dates after from_date)
        for row in cursor.fetchall():
            self.ui.to_menu.addItem(str(row[0]))  

        cursor.close()
        conn.close()

    def update_to_menu(self):
        """
        This function will be called when the from_menu selection changes.
        It will update the to_menu to show only dates after the selected from_date.
        """
        self.add_items_to_to_menu()


    def add_items_to_employee_menu(self):
        conn = make_connection(config_file = 'groupfour_db.ini')
        cursor = conn.cursor()
        
        sql = """
            SELECT emp_name FROM employee
            ORDER BY emp_name;
            """
        generator = cursor.execute(sql, multi=True)

        for result in generator:
            rows = cursor.fetchall()

            # Set the menu items to the teachers' names.
            for row in rows:
                name = row[0] 
                self.ui.employee_menu.addItem(name, row)     

        cursor.close()
        conn.close()   

    
    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()

    def populate_list(self): 
        option = self.ui.popular_menu.currentData()
        print(f"Selected option: {option}")  # Debugging output
    
        sql = ""
        if option == "Drink":
            
            self.ui.popular_table.clear()
            col = ['  Drink Name  ', '   Total Sales   ']
            self.ui.popular_table.setHorizontalHeaderLabels(col) 
            
            sql = """
            SELECT tea_name, COUNT(*) AS sales_count
            FROM groupfour_db.orders
            GROUP BY tea_name
            ORDER BY sales_count DESC
            LIMIT 10;
            """
        elif option == "Topping":

            self.ui.popular_table.clear()
            col = ['  Topping Name  ', '   Total Sales   ']
            self.ui.popular_table.setHorizontalHeaderLabels(col) 
            
            sql = """
            SELECT topping, COUNT(*) AS sales_count
            FROM groupfour_db.orders
            GROUP BY topping
            ORDER BY sales_count DESC
            LIMIT 10;
            """
        else:
            print("Invalid selection.")
            return
    
        # Fetch data
        try:
            conn = make_connection(config_file='groupfour_db.ini')
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            print(f"Query results: {rows}")  # Debugging output
            
            # Populate the table 
            self.ui.popular_table.clearContents()
            row_index = 0
            for row in rows:
                column_index = 0
                for data in row:
                    item = QTableWidgetItem(str(data))
                    self.ui.popular_table.setItem(row_index, column_index, item)
                    column_index += 1
                row_index += 1
            
            self._adjust_column_widths()
    
        except Exception as e:
            print(f"Error fetching data: {e}")

            
    def _adjust_column_widths(self):
        """
        Adjust the column widths of the class table to fit the contents.
        """
        header = self.ui.popular_table.horizontalHeader();
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
  

    def _enter_employee_data(self):
        """
        Enter employee data into the dashboard.
        """
        name = self.ui.employee_menu.currentText()
        if not name:
            print("No employee selected.")
            return

        # For the Employee Info table 
        try:
            conn = make_connection(config_file='groupfour_db.ini')
            cursor = conn.cursor()
            
            sql = """
            SELECT emp_name, emp_id, store_id, emp_dob, phone_num,
            CONCAT(street_num, ' ', street_name, ' ', city, ' ', zip) AS emp_add
            FROM employee
            JOIN employee_phone_num USING (emp_id)
            WHERE emp_name = %s;
            """
            cursor.execute(sql, (name,))
            row = cursor.fetchone()
    
            if row:
                print(f"Query result: {row}")  # Debugging output
                
                self.ui.name_label.setText(row[0])  # emp_name
                self.ui.empid_label.setText(str(row[1]))  # emp_id
                self.ui.store_label.setText(str(row[2]))  # store_id
                self.ui.num_label.setText(str(row[4]))
                
                # Convert date to string
                dob_str = row[3].strftime("%Y-%m-%d") if row[3] else "N/A"
                self.ui.dob_label.setText(dob_str)  # emp_dob
                
                self.ui.add_label.setText(row[5])  # emp_add
            else:
                print(f"No data found for employee: {name}")
    
        except Exception as e:
            print(f"Error in _enter_employee_data: {e}")
    
        finally:
            cursor.close()
            conn.close()
    
        # For the Vehicle Info table 
        try:
            conn = make_connection(config_file='groupfour_db.ini')
            cursor = conn.cursor()
            
            sql = """
            SELECT v.make, v.model, v.v_year, v.v_plate
            FROM vehicle v 
            JOIN employee e 
            ON v.emp_id = e.emp_id
            WHERE emp_name = %s;
            """
            cursor.execute(sql, (name,))
            row = cursor.fetchone()
    
            if row:
                print(f"Query result: {row}")  # Debugging output
                
                self.ui.make_label.setText(row[0])  
                self.ui.model_label.setText(str(row[1]))  
                self.ui.year_label.setText(str(row[2]))  
                self.ui.plate_label.setText(row[3])  
            else:
                print(f"No data found for employee: {name}")
    
        except Exception as e:
            print(f"Error in _enter_employee_data: {e}")
    
        finally:
            cursor.close()
            conn.close()