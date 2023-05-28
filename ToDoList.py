import sys
from PyQt6.QtWidgets import QSizePolicy, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QComboBox, QMessageBox
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView
import json


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")

        # Create the main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the input field and button layout
        input_layout = QHBoxLayout()
        input_label = QLabel("Task:")
        self.input_field = QLineEdit()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)
        self.input_field.setFocus()
        self.input_field.setPlaceholderText("Enter a task")

        # Create the priority selection layout
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("Low")
        self.priority_combo.addItem("Medium")
        self.priority_combo.addItem("High")
        # Set the foreground color of each item in the combo box to match their corresponding priority levels
        self.priority_combo.setItemData(0, QColor("green"), Qt.ItemDataRole.ForegroundRole)
        self.priority_combo.setItemData(1, QColor("yellow"), Qt.ItemDataRole.ForegroundRole)
        self.priority_combo.setItemData(2, QColor("red"), Qt.ItemDataRole.ForegroundRole)
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)

        # Add a legend explaining the priority levels
        legend_label = QLabel("Priority Legend:  Low = Green, Medium = Yellow, High = Red")
        layout.addWidget(legend_label)

        # Create the task list widget
        self.task_list = QListWidget()
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.task_list.setSizePolicy(size_policy)
        self.task_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        layout.addWidget(self.task_list)

        # Create the button layout
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Create the "Add Task" button
        add_button = QPushButton("Add Task")
        add_button.setToolTip("Add a new task to the list")
        add_button.clicked.connect(self.add_task)
        button_layout.addWidget(add_button)
        self.input_field.returnPressed.connect(self.add_task)

        # Create the "Mark as Done" button
        done_button = QPushButton("Mark Task as Done")
        done_button.setToolTip("Mark the selected task(s) as done")
        done_button.clicked.connect(self.mark_as_done)
        button_layout.addWidget(done_button)

        # Create the "Delete Task" button
        delete_button = QPushButton("Delete Task")
        delete_button.setToolTip("Delete the selected task(s) from the list")
        delete_button.clicked.connect(self.delete_task)
        button_layout.addWidget(delete_button)

        # Load tasks from file, if it exists
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    item = QListWidgetItem(task["text"])
                    item.setToolTip(f"Priority: {task['priority']}")
                    if task["priority"] == "Low":
                        item.setForeground(QColor("green"))
                    elif task["priority"] == "Medium":
                        item.setForeground(QColor("yellow"))
                    elif task["priority"] == "High":
                        item.setForeground(QColor("red"))
                    if task["done"]:
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Checked)
                    self.task_list.addItem(item)
        except FileNotFoundError:
            pass



        # Add the filtering checkboxes
        self.show_done_checkbox = QtWidgets.QCheckBox("Show Done Tasks")
        self.show_high_priority_checkbox = QtWidgets.QCheckBox("Show High Priority Tasks Only")
        button_layout.addWidget(self.show_done_checkbox)
        button_layout.addWidget(self.show_high_priority_checkbox)
        self.show_done_checkbox.setChecked(True)
        # Connect the checkboxes to the filter_tasks slot
        self.show_done_checkbox.stateChanged.connect(self.filter_tasks)
        self.show_high_priority_checkbox.stateChanged.connect(self.filter_tasks)

    def filter_tasks(self):
        show_done = self.show_done_checkbox.isChecked()
        show_high_priority = self.show_high_priority_checkbox.isChecked()

        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            done = item.checkState() == Qt.CheckState.Checked
            priority = item.toolTip().split(": ")[1]

            # Apply the "Show Done Tasks" filter
            if not show_done and done:
                item.setHidden(True)
                continue

            # Apply the "Show High Priority Tasks Only" filter
            if show_high_priority and priority != "High":
                item.setHidden(True)
                continue

            # If the task meets all filters, show it
            item.setHidden(False)

    def add_task(self):
        # Get the text from the input field
        text = self.input_field.text()
        if text == "":
            return

        # Get the priority from the combo box
        priority = self.priority_combo.currentText()

        # Create a new item and add it to the list
        item = QListWidgetItem(text)
        item.setToolTip(f"Priority: {priority}")
        if priority == "Low":
            item.setForeground(QColor("green"))
        elif priority == "Medium":
            item.setForeground(QColor("yellow"))
        elif priority == "High":
            item.setForeground(QColor("red"))
        self.task_list.addItem(item)

        # Clear the input field and set focus to it
        self.input_field.clear()
        self.input_field.setFocus()

    def mark_as_done(self):
        # Get the list of selected items
        selected = self.task_list.selectedItems()
        for item in selected:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
        self.task_list.clearSelection()

    def delete_task(self):
        # Get the list of selected items
        selected = self.task_list.selectedItems()
        for item in selected:
            self.task_list.takeItem(self.task_list.row(item))
        self.task_list.clearSelection()

    def closeEvent(self, event):
        # Save the tasks and their states to a file
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task = {"text": item.text(), "priority": item.toolTip().split(": ")[1], "done": item.checkState() == Qt.CheckState.Checked}
            tasks.append(task)
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

        # Close the window
        event.accept()



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()


