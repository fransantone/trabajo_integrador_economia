from PySide6.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from model_demanda import DemandModel
from view_demanda import MainWindow


class DemandController:
    """Controlador para la aplicación de análisis de demanda"""
    def __init__(self):
        self.model = DemandModel()
        self.view = MainWindow()
        
        # Canvas de matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.figure.patch.set_facecolor('#1a1a1a')
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        self._setup_connections()
        self._initialize_view()
    
    def _setup_connections(self):
        """Conecta las señales de la vista con los métodos del controlador"""
        self.view.load_api_btn.clicked.connect(self._on_load_api)
        self.view.apply_manual_btn.clicked.connect(self._on_apply_manual)
        self.view.calculate_btn.clicked.connect(self._on_calculate_regression)
        
        self.view.viz_both.toggled.connect(self._on_visualization_changed)
        self.view.viz_linear.toggled.connect(self._on_visualization_changed)
        self.view.viz_log.toggled.connect(self._on_visualization_changed)
    
    def _initialize_view(self):
        """Inicializa la vista con datos del modelo"""
        self.view.graph_layout.addWidget(self.canvas)
        
        self._plot_empty()
    
    def _on_load_api(self):
        """Maneja el evento de cargar datos desde API"""
        source = self.view.api_combo.currentText()
        try:
            prices, quantities = self.model.fetch_api_data(source)
            self.model.update_data(prices, quantities)
            self._plot_data()
            self._show_info(f"Datos de {source} cargados correctamente")
        except Exception as e:
            self._show_error(f"Error al cargar datos: {str(e)}")
    
    def _on_apply_manual(self):
        """Maneja el evento de aplicar datos manuales"""
        prices_text = self.view.prices_input.text().strip()
        quantities_text = self.view.quantities_input.text().strip()
        
        if not prices_text or not quantities_text:
            self._show_error("Por favor ingrese valores de precio y cantidad")
            return
        
        try:
            # Parsear valores separados por comas
            prices = np.array([float(x.strip()) for x in prices_text.split(',')])
            quantities = np.array([float(x.strip()) for x in quantities_text.split(',')])
            
            if len(prices) != len(quantities):
                self._show_error("La cantidad de precios y cantidades debe ser igual")
                return
            
            if len(prices) < 2:
                self._show_error("Se necesitan al menos 2 puntos de datos")
                return
            
            self.model.update_data(prices, quantities)
            self._plot_data()
            self._show_info("Datos manuales aplicados correctamente")
            
        except ValueError as e:
            self._show_error(f"Error al procesar los datos: {str(e)}")
    
    def _on_calculate_regression(self):
        """Maneja el evento de calcular regresión"""
        if len(self.model.prices) == 0 or len(self.model.quantities) == 0:
            self._show_error("Por favor cargue datos antes de calcular la regresión")
            return
        
        try:
            # Calcular regresiones
            slope, intercept, r2_linear, p_value = self.model.calculate_linear_regression()
            a, b, r2_log, elasticity = self.model.calculate_log_regression()
            
            # Redibujar gráfico con regresiones
            self._plot_regression()
            
        except Exception as e:
            self._show_error(f"Error al calcular regresión: {str(e)}")
    
    def _on_visualization_changed(self):
        """Maneja el cambio en las opciones de visualización"""
        # Solo redibujar si ya se calculó la regresión
        if self.model.linear_slope is not None:
            self._plot_regression()
    
    def _plot_empty(self):
        """Dibuja un gráfico vacío"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.set_facecolor('#1a1a1a')
        ax.spines['bottom'].set_color('#666666')
        ax.spines['top'].set_color('#666666')
        ax.spines['left'].set_color('#666666')
        ax.spines['right'].set_color('#666666')
        ax.tick_params(colors='#cccccc')
        ax.xaxis.label.set_color('#cccccc')
        ax.yaxis.label.set_color('#cccccc')
        
        ax.set_xlabel('Precio de Acción ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Volumen de Transacciones (miles)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2, color='#666666')
        
        self.canvas.draw()
    
    def _plot_data(self):
        """Dibuja solo los datos sin regresión"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.set_facecolor('#1a1a1a')
        ax.spines['bottom'].set_color('#666666')
        ax.spines['top'].set_color('#666666')
        ax.spines['left'].set_color('#666666')
        ax.spines['right'].set_color('#666666')
        ax.tick_params(colors='#cccccc')
        ax.xaxis.label.set_color('#cccccc')
        ax.yaxis.label.set_color('#cccccc')
        
        # Datos originales
        ax.scatter(self.model.prices, self.model.quantities, 
                  color='#9966CC', s=100, alpha=0.8, 
                  label='Datos observados', zorder=3)
        
        ax.set_xlabel('Precio de Acción ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Volumen de Transacciones (miles)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2, color='#666666')
        ax.legend(facecolor='#2d2d2d', edgecolor='#666666', labelcolor='#cccccc')
        
        self.canvas.draw()
    
    def _plot_regression(self):
        """Dibuja los datos con las líneas de regresión según el modo seleccionado"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.set_facecolor('#1a1a1a')
        ax.spines['bottom'].set_color('#666666')
        ax.spines['top'].set_color('#666666')
        ax.spines['left'].set_color('#666666')
        ax.spines['right'].set_color('#666666')
        ax.tick_params(colors='#cccccc')
        ax.xaxis.label.set_color('#cccccc')
        ax.yaxis.label.set_color('#cccccc')
        
        # Datos originales
        ax.scatter(self.model.prices, self.model.quantities, 
                  color='#9966CC', s=100, alpha=0.8, 
                  label='Datos observados', zorder=3)
        
        # Generar puntos para las líneas de regresión
        price_range = np.linspace(self.model.prices.min(), 
                                 self.model.prices.max(), 100)
        
        viz_mode = self.view.get_visualization_mode()
        
        if viz_mode in ["linear", "both"]:
            # Regresión lineal
            linear_pred = self.model.linear_intercept + self.model.linear_slope * price_range
            ax.plot(price_range, linear_pred, 
                   color='#4CAF50', linewidth=2, 
                   label=f'Lineal (R²={self.model.linear_r_squared:.3f})', 
                   zorder=2)
        
        if viz_mode in ["log", "both"]:
            # Regresión logarítmica
            log_pred = self.model.log_a * (price_range ** self.model.log_b)
            ax.plot(price_range, log_pred, 
                   color='#FF6B6B', linewidth=2, linestyle='--',
                   label=f'Logarítmica (R²={self.model.log_r_squared:.3f})', 
                   zorder=2)
        
        ax.set_xlabel('Precio de Acción ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Volumen de Transacciones (miles)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2, color='#666666')
        ax.legend(loc='best', facecolor='#2d2d2d', edgecolor='#666666', labelcolor='#cccccc')
        
        self.canvas.draw()
    
    def _show_info(self, message: str):
        """Muestra un mensaje informativo"""
        msg = QMessageBox(self.view)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Información")
        msg.exec()
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error"""
        msg = QMessageBox(self.view)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()
    
    def show(self):
        """Muestra la ventana principal"""
        self.view.show()
