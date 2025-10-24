from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSplitter, QFrame, QLineEdit, QComboBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
import numpy as np
import os


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación""" 
    # Señales para comunicación con el controlador
    load_api_data = Signal(str)
    apply_manual_data = Signal(str, str)
    calculate_regression = Signal()
    visualization_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análisis Demanda")
        self.setFixedSize(1000, 600)
        self._center_window()
        self.icon = QIcon()
        self.icon.addFile(u"C:/Users/Santo/OneDrive/Documentos/UB/tercero/economia_finanzas/trabajo_final_integrador/assets/icono.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(self.icon)
        
        self.colors = {
            'primary': '#5B2C6F',
            'secondary': '#9966CC',
            'accent': '#C8B3E0',
            'success': '#4CAF50',
            'white': '#FFFFFF',
            'grey': '#D3D3D3',
            'black': '#1a1a1a',
            'input_bg': '#2d2d2d'
        }
        
        self._setup_ui()
        self._apply_styles()
    
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        from PySide6.QtGui import QScreen
        screen = QScreen.availableGeometry(self.screen())
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def _create_left_panel(self) -> QWidget:
        """Crea el panel izquierdo con controles"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        layout.addStretch()
        
        api_frame = QFrame()
        api_frame.setObjectName("sectionFrame")
        api_layout = QVBoxLayout(api_frame)
        api_layout.setSpacing(8)
        api_layout.setContentsMargins(12, 12, 12, 12)
        
        api_row = QHBoxLayout()
        api_row.setSpacing(8)
        self.api_combo = QComboBox()
        self.api_combo.addItems([
            "Apple", "Microsoft", "Google", "Amazon", 
            "Tesla", "Meta", "Netflix", "NVIDIA"
        ])
        self.api_combo.setMinimumHeight(36)
        api_row.addWidget(self.api_combo)
        
        self.load_api_btn = QPushButton("Cargar desde API")
        self.load_api_btn.setMinimumHeight(36)
        api_row.addWidget(self.load_api_btn)
        
        api_layout.addLayout(api_row)
        layout.addWidget(api_frame)
        
        manual_frame = QFrame()
        manual_frame.setObjectName("sectionFrame")
        manual_layout = QVBoxLayout(manual_frame)
        manual_layout.setSpacing(8)
        manual_layout.setContentsMargins(12, 12, 12, 12)
        
        prices_label = QLabel("Precios:")
        prices_label.setFont(QFont("Arial", 10, QFont.Bold))
        prices_label.setStyleSheet(f"color: {self.colors['white']}; padding: 2px 0px;")
        manual_layout.addWidget(prices_label)
        
        self.prices_input = QLineEdit()
        self.prices_input.setPlaceholderText("Ej: 10, 15, 20, 25, 30")
        self.prices_input.setMinimumHeight(34)
        manual_layout.addWidget(self.prices_input)
        
        quantities_label = QLabel("Cantidades demanda:")
        quantities_label.setFont(QFont("Arial", 10, QFont.Bold))
        quantities_label.setStyleSheet(f"color: {self.colors['white']}; padding: 2px 0px; margin-top: 4px;")
        manual_layout.addWidget(quantities_label)
        
        self.quantities_input = QLineEdit()
        self.quantities_input.setPlaceholderText("Ej: 100, 85, 72, 60, 50")
        self.quantities_input.setMinimumHeight(34)
        manual_layout.addWidget(self.quantities_input)
        
        self.apply_manual_btn = QPushButton("Aplicar Datos Manuales")
        self.apply_manual_btn.setMinimumHeight(38)
        manual_layout.addWidget(self.apply_manual_btn)
        
        layout.addWidget(manual_frame)
        
        viz_frame = QFrame()
        viz_frame.setObjectName("sectionFrame")
        viz_layout = QVBoxLayout(viz_frame)
        viz_layout.setSpacing(6)
        viz_layout.setContentsMargins(12, 12, 12, 12)
        
        viz_label = QLabel("Opciones de Visualización:")
        viz_label.setFont(QFont("Arial", 10, QFont.Bold))
        viz_layout.addWidget(viz_label)
        
        self.viz_button_group = QButtonGroup()
        
        self.viz_both = QRadioButton("Ambas regresiones")
        self.viz_both.setChecked(True)
        self.viz_button_group.addButton(self.viz_both)
        viz_layout.addWidget(self.viz_both)
        
        self.viz_linear = QRadioButton("Solo lineal")
        self.viz_button_group.addButton(self.viz_linear)
        viz_layout.addWidget(self.viz_linear)
        
        self.viz_log = QRadioButton("Solo logarítmica")
        self.viz_button_group.addButton(self.viz_log)
        viz_layout.addWidget(self.viz_log)
        
        layout.addWidget(viz_frame)
        
        self.calculate_btn = QPushButton("Calcular Regresión")
        self.calculate_btn.setMinimumHeight(42)
        layout.addWidget(self.calculate_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Crea el panel derecho para el gráfico"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Visualización de Gráfico")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"padding: 15px; color: {self.colors['white']};")
        layout.addWidget(title)
        
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        layout.addWidget(self.graph_container)
        
        return panel
    
    def _apply_styles(self):
        """Aplica estilos CSS a los widgets"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['black']};
            }}
            QFrame {{
                background-color: {self.colors['black']};
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }}
            QFrame#sectionFrame {{
                background-color: #252525;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
                padding: 8px;
            }}
            QLabel {{
                color: {self.colors['white']};
                padding: 3px;
                background-color: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {self.colors['success']};
                color: {self.colors['white']};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
            QLineEdit {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['white']};
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['secondary']};
            }}
            QComboBox {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['white']};
                border: 2px solid {self.colors['secondary']};
                border-radius: 8px;
                padding: 8px 40px 8px 12px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 2px solid {self.colors['accent']};
                background-color: #353535;
            }}
            QComboBox:focus {{
                border: 2px solid {self.colors['accent']};
                background-color: #353535;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 38px;
                border-left: 2px solid {self.colors['secondary']};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['secondary']}, stop:1 {self.colors['primary']});
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox::drop-down:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['accent']}, stop:1 {self.colors['secondary']});
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 9px solid {self.colors['white']};
                margin: 0 auto;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['white']};
                selection-background-color: {self.colors['secondary']};
                selection-color: {self.colors['white']};
                border: 2px solid {self.colors['secondary']};
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px;
                border-radius: 4px;
                min-height: 28px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {self.colors['secondary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {self.colors['secondary']};
                color: {self.colors['white']};
            }}
            QRadioButton {{
                color: {self.colors['white']};
                padding: 4px;
                font-size: 11px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #3d3d3d;
                background-color: {self.colors['input_bg']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {self.colors['secondary']};
                border: 2px solid {self.colors['secondary']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {self.colors['accent']};
            }}
        """)
    
    def get_visualization_mode(self) -> str:
        """Retorna el modo de visualización seleccionado"""
        if self.viz_linear.isChecked():
            return "linear"
        elif self.viz_log.isChecked():
            return "log"
        else:
            return "both"
