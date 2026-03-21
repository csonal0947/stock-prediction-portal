# Stock Prediction Portal

A full-stack web application for live market data, stock metrics, and Indian bond yields, inspired by Moneycontrol.

## Features
- Live prices for commodities (Gold, Silver, Crude Oil) in INR
- Live currency rates (USD/INR, EUR/INR, GBP/INR)
- Indian government bond yields (10Y, 5Y, 2Y)
- Auto-refresh and error handling
- User authentication and registration
- Modern React frontend (Vite)
- Django REST backend with proxy endpoints (no CORS/API key exposure)

## Project Structure

```
Stock-prediction-portal/
├── backend-drf/           # Django backend
│   ├── api/               # Django app for API
│   ├── stock_prediction_main/ # Django project settings
│   ├── manage.py
│   └── ...
├── frontend-react/        # React frontend (Vite)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
└── env/                   # Python virtual environment
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm 9+
- Git

### Backend Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/csonal0947/stock-prediction-portal.git
   cd stock-prediction-portal/backend-drf
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv ../env
   source ../env/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```sh
   python manage.py migrate
   ```
5. Start the backend server:
   ```sh
   python manage.py runserver
   ```

### Frontend Setup
1. Open a new terminal and navigate to the frontend:
   ```sh
   cd ../frontend-react
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the frontend dev server:
   ```sh
   npm run dev
   ```

### Access the App
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/market-data/

## Environment Variables
- Copy `.env.example` to `.env` and set any required secrets (API keys, etc.)

## Deployment
- For production, use Gunicorn/Uvicorn for backend and serve frontend build with Nginx or similar.

## License
MIT

## Author
- GitHub: https://github.com/csonal0947
