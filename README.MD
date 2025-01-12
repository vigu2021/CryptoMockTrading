## **CryptoMockTrading**

CryptoMockTrading is a fun project that simulates cryptocurrency trading. It allows users to trade mock cryptocurrencies, view their portfolio, and analyze price movements using interactive charts.

### **Features**
- Mock trading with buy and sell functionality.
- Portfolio view to track balances and holdings.
- Interactive candlestick charts with volume data.
- Automated background tasks using APScheduler.

### **Technologies Used**
- **Frontend**: HTML, CSS (Bootstrap)
- **Backend**: Python, Django
- **Database**: SQLite
- **Visualization**: Plotly
- **API**: Binance API (for fetching mock data)
- **Task Scheduler**: APScheduler (for periodic updates)

### **Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/vigu2021/CryptoMockTrading.git
   cd CryptoMockTrading
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```
5. Visit:
   ```
   http://127.0.0.1:8000/
   ```

### **Just for Fun**
This project was created for learning and experimenting with Django and data visualization. Feel free to explore, break, and rebuild it!
