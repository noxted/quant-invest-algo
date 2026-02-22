# Dashboard Setup Instructions

## Backend: FastAPI
```bash
pip install -r requirements.txt
python backend_api.py
# Server: http://localhost:8000
```

## Frontend: React + Tauri
```bash
npm install
npm install -D @tauri-apps/cli
npm run dev  # Development
npm run build  # Build desktop app
```

## API Endpoints
- GET /api/portfolio - Portfolio summary
- GET /api/trades - Trade history
- GET /api/positions - Current positions
- GET /api/indicators - Macro indicators
- GET /api/performance - Performance metrics
- GET /api/regime - Economic regime
- WebSocket /ws/portfolio - Real-time updates

## Sprint 1 Status
- [x] FastAPI backend
- [x] Tauri config
- [x] Python dependencies
- [ ] React Overview page
- [ ] Portfolio charts

## Next Steps
1. Create React components
2. Integrate Recharts visualizations
3. Connect to backend API
4. Add WebSocket real-time updates
5. Package as desktop app

Backend: ✅ Complete | Frontend: ⏳ Starting | Integration: 🔄 In Progress
