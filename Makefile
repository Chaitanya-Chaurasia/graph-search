.PHONY: dev backend frontend install

# Start both backend and frontend
dev:
	$(MAKE) backend & $(MAKE) frontend & wait

# Backend: FastAPI via uv
backend:
	cd backend && PYTHONPATH=.. uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend: Next.js dev server
frontend:
	cd frontend && npm run dev

# Install all dependencies
install:
	cd backend && uv sync
	cd frontend && npm install
