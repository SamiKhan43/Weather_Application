from dotenv import load_dotenv
import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton,
                            QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap , QIcon
from io import BytesIO
import requests

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.title_label = QLabel("Weather App")
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff;")
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.search_button = QPushButton("Search")

        self.temp_label = QLabel("🌤️")        
        self.temp_label.setAlignment(Qt.AlignHCenter)
        self.temp_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #ffffff;")

        self.city_label = QLabel("Enter a city to start")      
        self.city_label.setAlignment(Qt.AlignHCenter)
        self.city_label.setStyleSheet("font-size: 28px; color: #ffffff;")

        self.icon_label = QLabel("")     
        self.icon_label.setAlignment(Qt.AlignHCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")  

        self.desc_label = QLabel("")       
        self.desc_label.setAlignment(Qt.AlignHCenter)
        self.desc_label.setStyleSheet("font-size: 20px; color: #ffffff;")

        self.min_max_label = QLabel("")
        self.min_max_label.setAlignment(Qt.AlignHCenter)
        self.min_max_label.setStyleSheet("font-size: 16px; color: #ffffff;")

        self.feels_like_label = QLabel("")
        self.feels_like_label.setAlignment(Qt.AlignHCenter)
        self.feels_like_label.setStyleSheet("font-size: 16px; color: #ffffff;")

        self.pressure_label = QLabel("")
        self.pressure_label.setAlignment(Qt.AlignHCenter)
        self.pressure_label.setStyleSheet("font-size: 16px; color: #ffffff;")

        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Weather App")
        icon_path = os.path.join(os.path.dirname(__file__), "weather.svg")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(600, 500)
   
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.city_input)
        search_layout.addWidget(self.search_button)
        search_layout.setSpacing(10)
        self.city_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label) 
        main_layout.addSpacing(20)
        main_layout.addLayout(search_layout)    
        main_layout.addSpacing(30)

        main_layout.addWidget(self.temp_label)
        main_layout.addWidget(self.city_label)
        main_layout.addWidget(self.icon_label)
        main_layout.addWidget(self.desc_label)
        main_layout.addWidget(self.min_max_label)
        main_layout.addWidget(self.feels_like_label)
        main_layout.addWidget(self.pressure_label)
        main_layout.addStretch()
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        self.setLayout(main_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0F4C81; 
            }
            QLineEdit {
                background-color: #ffffff;
                border: none;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit::placeholder {
                color: #999;
            }
            QLabel#tempLabel {
                font-size: 64px;
                font-weight: bold;
                color: #ffffff;
                text-shadow: 1px 1px 5px #000000;
            }
            QPushButton {
                background-color: #98B4D4;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7B93B5;
                font-size: 17px;
            }
            QLabel#cityLabel {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
            }

        """)

        self.search_button.clicked.connect(self.get_weather)

    def get_weather(self):
        load_dotenv()
        API_KEY = os.getenv("WEATHER_API_KEY")
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
      
        try:
            response = requests.get(url,timeout=5)
            response.raise_for_status()   
    
            data = response.json()
            self.display_weather(data)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code

            match status:
                case 400:
                    self.display_error("Bad request – check parameters")
                case 401:
                    self.display_error("Unauthorized – invalid API key")
                case 402:
                    self.display_error("Payment required")
                case 403:
                    self.display_error("Forbidden – access denied")
                case 404:
                    self.display_error("City not found")
                case 429:
                    self.display_error("Too many requests – rate limited")
                case 500:
                    self.display_error("Server error – try later")
                case 503:
                    self.display_error("Service unavailable")
                case _:
                    self.display_error(f"HTTP error {status}")

        except requests.exceptions.Timeout:
            self.display_error("Request timed out – server too slow")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection error – check internet or server down")

        except requests.exceptions.RequestException as e:
            self.display_error(f"Unexpected request error: {e}")

    def display_error(self, message):
        self.temp_label.setText(message)
    
    def clear_ui(self):
        self.city_label.setText("")
        self.desc_label.setText("")
        self.min_max_label.setText("")
        self.feels_like_label.setText("")
        self.pressure_label.setText("")
        
    def display_weather(self, data):
        temperature_k = data["main"]["temp"]
        temperature_c = round(temperature_k - 273.15)
        temperature_f = round((temperature_k * 9/5) - 459.67)
        self.temp_label.setText(f"{temperature_c}°C ")

        city_name = data.get("name")
        country = data.get("sys", {}).get("country", "")
        if city_name:
            self.city_label.setText(f"{city_name}, {country}")
                
        weather = data.get("weather")
        if weather and len(weather) > 0:
            desc = weather[0].get("description", "").title()
            self.desc_label.setText(desc)

        temp_max_k = data["main"].get("temp_max")
        temp_min_k = data["main"].get("temp_min")
        if temp_max_k and temp_min_k:
            temp_max_c = round(temp_max_k - 273.15)
            temp_min_c = round(temp_min_k - 273.15)
            self.min_max_label.setText(f"Max: {temp_max_c}°C  |  Min: {temp_min_c}°C")

        feels_like_k = data["main"].get("feels_like")
        if feels_like_k:
            feels_like_c = round(feels_like_k - 273.15)
            self.feels_like_label.setText(f"Feels Like: {feels_like_c}°C")

        pressure = data["main"].get("pressure")
        if pressure:
            self.pressure_label.setText(f"Pressure: {pressure} hPa")

        icon_code = weather[0].get("icon")

        if icon_code:
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
        try:
            icon_response = requests.get(icon_url)
            icon_response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(icon_response.content)
            self.icon_label.setPixmap(pixmap)
        except requests.exceptions.RequestException:
            self.icon_label.setText("")  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())