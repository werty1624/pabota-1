import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLineEdit, QPushButton, QListWidget, 
                             QComboBox, QLabel, QListWidgetItem, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt

class TaskFlow(QWidget):
    def __init__(self):
        super().__init__()
        # Список для хранения задач
        self.tasks = []
        self.filename = "tasks.json"
        
        self.initUI()
        self.load_data()
        self.update_list()

    def initUI(self):
        self.setWindowTitle('TaskFlow — Менеджер задач')
        self.resize(650, 450)

        # Основной Layout
        main_layout = QVBoxLayout()

        # 1. Верхняя панель (Использование QGridLayout согласно ТЗ)
        top_layout = QGridLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText('Введите название новой задачи')
        
        self.add_button = QPushButton('Добавить задачу')
        self.add_button.clicked.connect(self.add_task)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Поиск задач')
        # Автоматическая фильтрация при вводе текста
        self.search_input.textChanged.connect(self.update_list) 
        
        top_layout.addWidget(self.task_input, 0, 0)
        top_layout.addWidget(self.add_button, 0, 1)
        top_layout.addWidget(self.search_input, 1, 0, 1, 2)

        # 2. Центральная часть и Правая панель
        center_layout = QHBoxLayout()
        
        self.task_list_widget = QListWidget()
        center_layout.addWidget(self.task_list_widget)
        
        right_panel = QVBoxLayout()
        self.btn_done = QPushButton('Выполнено')
        self.btn_done.clicked.connect(self.toggle_done)
        
        self.btn_edit = QPushButton('Редактировать')
        self.btn_edit.clicked.connect(self.edit_task)
        
        self.btn_delete = QPushButton('Удалить')
        self.btn_delete.clicked.connect(self.delete_task)
        
        right_panel.addWidget(self.btn_done)
        right_panel.addWidget(self.btn_edit)
        right_panel.addWidget(self.btn_delete)
        right_panel.addStretch()  # Чтобы кнопки не расползались по высоте
        
        center_layout.addLayout(right_panel)

        # 3. Нижняя панель
        bottom_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['Все задачи', 'Только выполненные', 'Только невыполненные'])
        # Обновление списка при смене фильтра
        self.filter_combo.currentIndexChanged.connect(self.update_list) 
        
        self.count_label = QLabel('Количество задач: 0')
        
        bottom_layout.addWidget(self.filter_combo)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.count_label)

        # Сборка окон
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)

    def load_data(self):
        """Загрузка данных из JSON при запуске"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_data(self):
        """Автоматическое сохранение задач в JSON"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def add_task(self):
        """Добавление новой задачи"""
        title = self.task_input.text().strip()
        if title:  # Проверка на пустое поле
            self.tasks.append({"title": title, "done": False})
            self.task_input.clear()
            self.save_data()
            self.update_list()

    def update_list(self):
        """Обновление списка виджетов с учетом фильтрации и поиска"""
        self.task_list_widget.clear()
        search_text = self.search_input.text().lower()
        filter_idx = self.filter_combo.currentIndex()
        
        count = 0
        for idx, task in enumerate(self.tasks):
            # Проверка фильтров
            if filter_idx == 1 and not task['done']:
                continue
            if filter_idx == 2 and task['done']:
                continue
                
            # Проверка поиска
            if search_text and search_text not in task['title'].lower():
                continue
                
            # Формирование текста задачи
            status_text = "Выполнено" if task['done'] else "Не выполнено"
            item_text = f"[{status_text}] {task['title']}"
            
            item = QListWidgetItem(item_text)
            # Привязываем скрытый идентификатор к элементу
            item.setData(Qt.UserRole, idx) 
            
            # Меняем цвет у выполненных задач для наглядности
            if task['done']:
                item.setForeground(Qt.gray)
                
            self.task_list_widget.addItem(item)
            count += 1
            
        self.count_label.setText(f'Отображается задач: {count}')

    def get_selected_task_index(self):
        """Вспомогательный метод для получения исходного ID задачи"""
        selected_items = self.task_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите задачу из списка!")
            return None
        return selected_items[0].data(Qt.UserRole)

    def toggle_done(self):
        """Изменение статуса задачи (Выполнено/Не выполнено)"""
        idx = self.get_selected_task_index()
        if idx is not None:
            self.tasks[idx]['done'] = not self.tasks[idx]['done']
            self.save_data()
            self.update_list()

    def edit_task(self):
        """Редактирование названия задачи"""
        idx = self.get_selected_task_index()
        if idx is not None:
            current_title = self.tasks[idx]['title']
            new_title, ok = QInputDialog.getText(self, "Редактирование", "Новое название:", text=current_title)
            if ok and new_title.strip():
                self.tasks[idx]['title'] = new_title.strip()
                self.save_data()
                self.update_list()

    def delete_task(self):
        """Удаление задачи из списка"""
        idx = self.get_selected_task_index()
        if idx is not None:
            reply = QMessageBox.question(self, "Удаление", "Удалить выбранную задачу?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.tasks[idx]
                self.save_data()
                self.update_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskFlow()
    window.show()
    sys.exit(app.exec_())