"""FastAPI Backend for Dashboard - Integrates with Quantitative Investment Algorithm"""
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path to import algorithm modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from orchestrator import Orchestrator
except ImportError:
    print("Warning: Could not import orchestrator module. Using mock data.")
    Orchestrator = None

app = FastAPI(title="Quant Invest Dashboard API", version="1.0.0")

# Enable CORS for local app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator_instance: Optional[object] = None
active_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator_instance
    if Orchestrator:
        try:
            orchestrator_instance = Orchestrator()
            print("Orchestrator initialized successfully")
        except Exception as e:
            print(f"Error initializing orchestrator: {e}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "algorithm_ready": orchestrator_instance is not None
    }


@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio summary and metrics"""
    try:
        if not orchestrator_instance:
            return mock_portfolio_data()

        portfolio = orchestrator_instance.get_portfolio_summary()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trades")
async def get_trades(limit: int = 100, profile: Optional[str] = None):
    """Get trade history with justifications"""
    try:
        if not orchestrator_instance:
            return {"trades": mock_trades_data()[:limit]}

        trades = orchestrator_instance.get_decision_history()
        return {"trades": [d.to_dict() for d in trades[:limit]]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions")
async def get_positions(profile: Optional[str] = None):
    """Get current positions by asset class"""
    try:
        if not orchestrator_instance:
            return {"positions": mock_positions_data()}

        return {"positions": mock_positions_data()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/indicators")
async def get_indicators():
    """Get macroeconomic indicators (SELIC, IPCA, PIB, etc)"""
    try:
        return {"indicators": mock_indicators_data()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_performance(period_days: Optional[int] = 365):
    """Get performance metrics (Sharpe, Sortino, Calmar, VaR, Drawdown)"""
    try:
        return {"performance": mock_performance_data()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/regime")
async def get_regime():
    """Get current economic regime detected by algorithm"""
    try:
        if orchestrator_instance:
            return orchestrator_instance.get_current_regime()
        return {"regime": "intermediate", "confidence": 0.75}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/portfolio")
async def websocket_portfolio(websocket: WebSocket):
    """WebSocket endpoint for real-time portfolio updates"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(5)
            portfolio_data = await get_portfolio()
            await websocket.send_json(portfolio_data)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


# Mock data functions for development/testing
def mock_portfolio_data() -> Dict:
    return {
        "total_balance": 50000.00,
        "invested": 48500.00,
        "cash": 1500.00,
        "profitability_pct": 12.5,
        "vpl": 6250.00,
        "max_drawdown": -8.3,
        "allocation": {
            "fixed_income": 30,
            "real_estate": 25,
            "stocks": 30,
            "tech": 15
        },
        "timestamp": datetime.now().isoformat()
    }


def mock_trades_data() -> List[Dict]:
    base_date = datetime.now() - timedelta(days=90)
    trades = []
    for i in range(10):
        trade_date = base_date + timedelta(days=i*9)
        trades.append({
            "id": f"TRADE_{i+1:03d}",
            "date": trade_date.isoformat(),
            "amount": 5000 + (i * 500),
            "profile": ["conservative", "intermediate", "aggressive"][i % 3],
            "allocation": {
                "fixed_income": 35 - i,
                "real_estate": 25,
                "stocks": 25 + i,
                "tech": 15
            },
            "justification": f"SELIC em alta, IPCA controlado. Regime: intermediate. Aumentando exposure em renda variavel.",
            "signals": ["selic_rising", "inflation_stable", "risk_intermediate"]
        })
    return trades


def mock_positions_data() -> List[Dict]:
    return [
        {"asset": "LCI/LCA", "quantity": 10000, "price": 1.0, "total": 10000, "pct": 20.7},
        {"asset": "FII", "quantity": 500, "price": 100, "total": 50000, "pct": 20.7},
        {"asset": "VALE3", "quantity": 100, "price": 65, "total": 6500, "pct": 13.5},
        {"asset": "TECH ETF", "quantity": 250, "price": 45, "total": 11250, "pct": 23.3},
        {"asset": "CRYPTO (BTC)", "quantity": 0.05, "price": 35000, "total": 1750, "pct": 3.6},
    ]


def mock_indicators_data() -> Dict:
    return {
        "selic": {"value": 10.5, "change": 0.5, "date": datetime.now().isoformat()},
        "ipca": {"value": 4.2, "change": -0.1, "date": datetime.now().isoformat()},
        "pib": {"value": 2.1, "change": 0.3, "date": datetime.now().isoformat()},
        "usd_brl": {"value": 5.15, "change": 0.02, "date": datetime.now().isoformat()},
        "vix": {"value": 16.5, "change": -1.2, "date": datetime.now().isoformat()},
    }


def mock_performance_data() -> Dict:
    return {
        "sharpe_ratio": 1.85,
        "sortino_ratio": 2.45,
        "calmar_ratio": 1.5,
        "var_95": -2.1,
        "max_drawdown": -8.3,
        "annual_return": 15.2,
        "volatility": 8.2,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
