from PyQt5 import uic
from PyQt5.QtGui import QWindow
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
        
        self.ui = uic.loadUi('boba_window.ui')
        self.ui.show();
        
        # Employee dialog.
        self._employee_dialog = EmployeeDialog(self.db_connection)
        self.ui.employee_button.clicked.connect(self.show_operations_portal) 
        
        # Manager dialog.
        self._manager_dialog = ManagerDialog()
        self.ui.manager_button.clicked.connect(self._show_manager_dialog)

    def show_operations_portal(self):
        self.operations_window = EmployeeDialog(self.db_connection)
        self.operations_window.show()

    def _show_manager_dialog(self):
        """
        Show the manager dialog.
        """
        self._manager_dialog.show_dialog()
