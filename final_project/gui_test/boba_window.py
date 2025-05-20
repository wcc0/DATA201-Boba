from PyQt5 import uic
from PyQt5.QtGui import QWindow, QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl
from employee_window import EmployeeDialog
from manager_window import ManagerDialog
from data201 import make_connection

class BobaWindow(QWindow):
    """
    The main application window.
    """
    
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        self.db_connection = make_connection('bobashop.ini')
        
        # Load custom font
        self.load_custom_font()
        
        self.ui = uic.loadUi('boba_window.ui')
        self.ui.show();
        
        # Apply custom font to widgets
        self.apply_custom_font_to_widgets()
        
        # Employee dialog.
        self._employee_dialog = EmployeeDialog(self.db_connection)
        self.ui.employee_button.clicked.connect(self.show_operations_portal) 
        
        # Manager dialog.
        self._manager_dialog = ManagerDialog()
        self.ui.manager_button.clicked.connect(self._show_manager_dialog)
    
    def load_custom_font(self):
        """
        Load a custom font into the application.
        """
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont("Comfortaa-VariableFont_wght.ttf")  # Path to your custom font
        if font_id != -1:
            custom_font_family = font_db.applicationFontFamilies(font_id)[0]
            custom_font = QFont(custom_font_family)
            QApplication.setFont(custom_font)  # Set the font for the entire application
        else:
            print("Font loading failed!")
    
    def apply_custom_font_to_widgets(self):
        """
        Apply the custom font to all widgets on the main window.
        """
        custom_font = QApplication.font()  # Get the currently set font

        # Apply the font to all widgets
        for widget in self.ui.findChildren(QWidget):
            widget.setFont(custom_font)
        
    def show_operations_portal(self):
        self.operations_window = EmployeeDialog(self.db_connection)
        self.operations_window.show()

    def _show_manager_dialog(self):
        """
        Show the manager dialog.
        """
        self._manager_dialog.show_dialog()
