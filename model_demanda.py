import numpy as np
from scipy import stats
from typing import Tuple, Optional
import requests
from datetime import datetime, timedelta


class DemandModel:
    """Modelo de datos para la función de demanda"""
    
    STOCK_SYMBOLS = {
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Google': 'GOOGL',
        'Amazon': 'AMZN',
        'Tesla': 'TSLA',
        'Meta': 'META',
        'Netflix': 'NFLX',
        'NVIDIA': 'NVDA'
    }
    
    def __init__(self):
        self.prices = np.array([])
        self.quantities = np.array([])
        
        # Resultados de regresión
        self.linear_slope: Optional[float] = None
        self.linear_intercept: Optional[float] = None
        self.linear_r_squared: Optional[float] = None
        self.linear_p_value: Optional[float] = None
        
        self.log_a: Optional[float] = None
        self.log_b: Optional[float] = None
        self.log_r_squared: Optional[float] = None
        self.log_elasticity: Optional[float] = None
    
    def update_data(self, prices: np.ndarray, quantities: np.ndarray):
        """Actualiza los datos de precio y cantidad"""
        self.prices = prices.copy()
        self.quantities = quantities.copy()
        self._reset_results()
    
    def _reset_results(self):
        """Resetea los resultados de regresión"""
        self.linear_slope = None
        self.linear_intercept = None
        self.linear_r_squared = None
        self.linear_p_value = None
        self.log_a = None
        self.log_b = None
        self.log_r_squared = None
        self.log_elasticity = None
    
    def calculate_linear_regression(self) -> Tuple[float, float, float, float]:
        """
        Calcula la regresión lineal: Q = a + b*P
        Returns: (slope, intercept, r_squared, p_value)
        """
        if len(self.prices) < 2 or len(self.quantities) < 2:
            raise ValueError("Se necesitan al menos 2 puntos de datos")
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            self.prices, self.quantities
        )
        
        self.linear_slope = slope
        self.linear_intercept = intercept
        self.linear_r_squared = r_value ** 2
        self.linear_p_value = p_value
        
        return slope, intercept, self.linear_r_squared, p_value
    
    def calculate_log_regression(self) -> Tuple[float, float, float, float]:
        """
        Calcula la regresión logarítmica: Q = a * P^b
        Returns: (a, b, r_squared, elasticity)
        """
        if len(self.prices) < 2 or len(self.quantities) < 2:
            raise ValueError("Se necesitan al menos 2 puntos de datos")
        
        if np.any(self.prices <= 0) or np.any(self.quantities <= 0):
            raise ValueError("Los valores deben ser positivos para regresión logarítmica")
        
        # Transformación logarítmica
        log_prices = np.log(self.prices)
        log_quantities = np.log(self.quantities)
        
        # Regresión lineal en escala logarítmica
        b, log_a, r_value, p_value, std_err = stats.linregress(
            log_prices, log_quantities
        )
        
        a = np.exp(log_a)
        
        self.log_a = a
        self.log_b = b
        self.log_r_squared = r_value ** 2
        self.log_elasticity = b  # En modelo log-log, b es la elasticidad
        
        return a, b, self.log_r_squared, self.log_elasticity
    
    def get_linear_prediction(self, price: float) -> float:
        """Obtiene predicción lineal para un precio dado"""
        if self.linear_slope is None or self.linear_intercept is None:
            raise ValueError("Debe calcular la regresión lineal primero")
        return self.linear_intercept + self.linear_slope * price
    
    def get_log_prediction(self, price: float) -> float:
        """Obtiene predicción logarítmica para un precio dado"""
        if self.log_a is None or self.log_b is None:
            raise ValueError("Debe calcular la regresión logarítmica primero")
        return self.log_a * (price ** self.log_b)
    
    def get_linear_equation(self) -> str:
        """Retorna la ecuación lineal como string"""
        if self.linear_slope is None or self.linear_intercept is None:
            return "No calculada"
        return f"Q = {self.linear_intercept:.2f} + {self.linear_slope:.2f}*P"
    
    def get_log_equation(self) -> str:
        """Retorna la ecuación logarítmica como string"""
        if self.log_a is None or self.log_b is None:
            return "No calculada"
        return f"Q = {self.log_a:.2f} * P^{self.log_b:.2f}"
    
    def load_sample_data(self):
        """Carga datos de ejemplo"""
        self.prices = np.array([100, 90, 80, 70, 60, 50, 40, 30])
        self.quantities = np.array([10, 15, 20, 30, 40, 55, 70, 90])
        self._reset_results()
    
    def fetch_api_data(self, source: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Obtiene datos de una API externa (Yahoo Finance)
        Args:
            source: Fuente de datos ('Apple', 'Microsoft', etc.)
        Returns: (prices, quantities)
        """
        if source not in self.STOCK_SYMBOLS:
            raise ValueError(f"Acción '{source}' no soportada")
        
        symbol = self.STOCK_SYMBOLS[source]
        
        try:
            # Usar Yahoo Finance API (sin necesidad de API key)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Formato de fechas para Yahoo Finance
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': period1,
                'period2': period2,
                'interval': '1d'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data['chart']['result'][0]
            
            # Extraer precios de cierre y volúmenes
            quotes = result['indicators']['quote'][0]
            close_prices = quotes['close']
            volumes = quotes['volume']
            
            # Filtrar valores None y tomar últimos 15 días
            valid_data = [(p, v) for p, v in zip(close_prices, volumes) 
                         if p is not None and v is not None]
            valid_data = valid_data[-15:]  # Últimos 15 días
            
            if len(valid_data) < 5:
                raise ValueError("No hay suficientes datos válidos")
            
            prices = np.array([d[0] for d in valid_data])
            # Normalizar volúmenes a escala más manejable (en miles)
            quantities = np.array([d[1] / 1000 for d in valid_data])
            
            return prices, quantities
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos de {source}: {str(e)}")
