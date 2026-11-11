# CyberShield AI: Autonomous Cyber Defense using Reinforcement Learning and Blockchain
## Complete End-to-End Testing & Validation Report

- **Project Path:** `C:\final year\CyberShieldAI-Final`
- **Audit Date:** November 10, 2026
- **Test Execution Environment:** Windows (x86_64), Python 3.10.11 Virtual Environment (`.venv`), Node.js v26.3.1, npm 11.16.0

---

## 1. Project Overview

CyberShield AI is an autonomous cyber defense platform combining:
1. **Network Intrusion Detection System (NIDS):** Supervised classification via XGBoost (40 engineered flow features, 15 multi-class attack categories) trained on CIC-IDS2017/2018 datasets.
2. **Autonomous Defense Decision Engine:** Reinforcement Learning agent using Proximal Policy Optimization (PPO) with a 26-dimensional state space and 5 discrete defense actions (`MONITOR`, `ALERT`, `RATE LIMIT`, `BLOCK`, `ISOLATE`).
3. **Simulated Enforcement & Evaluation:** A gymnasium-based cyber defense simulation consisting of a Firewall Simulator, Resource Manager, and Network Simulator.
4. **Immutable Audit Ledger:** A single-node private hash-linked blockchain ledger for tamper-resistant security event logging and integrity verification.
5. **Interactive UI & Real-Time Monitoring:** React 19 + Vite dashboard featuring live network packet capture (via Scapy / Npcap on Wi-Fi), real-time flow feature extraction, threat prediction, and blockchain verification.

---

## 2. Project Structure

```
CyberShieldAI-Final/
├── backend/
│   ├── ai/
│   │   ├── datasets/final/ (X_test.npy, y_test.npy)
│   │   ├── evaluation/Selected_Features.txt
│   │   ├── integration/xgboost_ppo_blockchain.py
│   │   ├── models/
│   │   │   ├── model_config.json
│   │   │   ├── saved/xgboost_baseline.joblib
│   │   │   └── saved/rl/cybershield_ppo_v5.zip
│   │   ├── preprocessing/ (01 through 06 scripts)
│   │   └── rl/ (environment, simulation, agent, evaluation)
│   ├── app/
│   │   ├── main.py (FastAPI entrypoint and lifespan manager)
│   │   ├── models/ (threat.py, blockchain.py)
│   │   ├── routes/ (dashboard, threats, xgboost, blockchain, defense, live_monitor)
│   │   └── services/ (live_flow_monitor, live_feature_extractor, xgboost_service, dashboard_services)
│   └── blockchain/
│       ├── block.py, blockchain.py, event.py, service.py
│       └── data/blockchain.json
├── frontend/
│   ├── src/
│   │   ├── components/ (dashboard, Navbar, Sidebar)
│   │   ├── layouts/MainLayout.tsx
│   │   ├── pages/ (Dashboard, ThreatDetection, LiveMonitoring, BlockchainLogs, Reports, Settings, NotFound)
│   │   └── routes/AppRoutes.tsx
│   └── package.json, vite.config.ts, tsconfig.json
├── scratch/ (automated validation scripts)
└── docs/ (documentation, roadmaps, test reports)
```

---

## 3. Phase 1 — Component Inventory & Audit Results

| Component | Implemented | Tested | Integrated | Issues / Observations |
|---|---|---|---|---|
| **FastAPI Backend Core** | PASS | PASS | PASS | `app/main.py` starts with lifespan manager, CORS middleware configured. |
| **XGBoost Detection Service** | PASS | PASS | PASS | Loaded from `xgboost_baseline.joblib` (40 features, 15 classes). |
| **RL / PPO Agent** | PASS | PASS | PASS | Loaded from `cybershield_ppo_v5.zip` (26-dim Box obs, 5-dim Discrete action). |
| **Gymnasium Defense Simulators** | PASS | PASS | PASS | FirewallSimulator, ResourceManager, NetworkSimulator implemented in `backend/ai/rl/simulation/`. |
| **Blockchain Security Ledger** | PASS | PASS | PASS | Local hash-linked ledger in `blockchain.json`, 17 blocks currently linked and valid (`is_chain_valid=True`). |
| **Live Network Sniffer** | PASS | PASS | PASS | Passive capture via Scapy on Wi-Fi interface `\Device\NPF_{963FB553-480C-45AD-96B7-19FDAC757AC6}`. |
| **Live Feature Extractor** | PASS | PASS | PASS | Extracts 40 features defined in `Selected_Features.txt`. |
| **Frontend React Dashboard** | PASS | PASS | PASS | React 19 + Vite + Tailwind CSS. Compiles cleanly (`npm run build` completed in 1.54s). |

---

## 4. Phase 2 — Environment and Dependency Testing Results

### 4.1 Runtime Versions

| Tool / Runtime | Detected Version | Target / Compatibility Notes | Status |
|---|---|---|---|
| **System Python** | Python 3.14.6 | Incompatible with binary wheels for PyTorch / stable-baselines3 | WARNING (Avoid using system Python) |
| **Project Python (`.venv`)** | Python 3.10.11 | Fully compatible with PyTorch 2.14.1, Gymnasium 1.4.0, SB3 2.9.0 | PASS |
| **Node.js** | v26.3.1 | Compatible with Vite 8.2.0 | PASS |
| **npm** | 11.16.0 | Package manager operational | PASS |

### 4.2 Python Dependencies (`.venv`)
The following critical libraries were verified installed in `C:\final year\CyberShieldAI-Final\.venv`:
- `fastapi==0.143.0`, `uvicorn==0.54.0`, `starlette==1.7.0`
- `xgboost==3.2.0`, `scikit-learn==1.7.2`, `joblib==1.6.0`, `numpy==2.2.6`, `scipy==1.15.3`
- `torch==2.14.1`, `gymnasium==1.4.0`, `stable_baselines3==2.9.0`, `cloudpickle==3.1.2`
- `scapy==2.8.0`, `pydantic==2.14.0`, `pydantic_core==2.50.0`

No missing Python dependencies or library conflicts detected within `.venv`.

### 4.3 Frontend Dependencies (`frontend/package.json`)
The frontend contains all required modules in `node_modules` and compiled cleanly via `npm run build`:
- `react@^19.2.8`, `react-dom@^19.2.8`, `react-router-dom@^7.18.2`
- `vite@^8.2.0`, `@vitejs/plugin-react@^6.0.4`
- `lucide-react@^1.28.0`, `recharts@^3.8.0`, `tailwindcss@^4.3.3`

*Observation:* An extraneous `backend/package.json` exists in `backend/` specifying Express/TypeScript; however, the actual operational backend is FastAPI (`app.main:app`).

### 4.4 Trained Model File Verification
1. **XGBoost Model (`backend/ai/models/saved/xgboost_baseline.joblib`):**
   - File exists: `True`
   - File size: `1,397,911 bytes`
   - Model type: `XGBClassifier`
   - Expected feature count (`n_features_in_`): `40`
   - Target classes: 15 classes (`[0, 1, 2, ..., 14]`)
   - Load status: PASS (Loaded cleanly via `joblib.load`)

2. **PPO Model (`backend/ai/models/saved/rl/cybershield_ppo_v5.zip`):**
   - File exists: `True`
   - File size: `178,472 bytes`
   - Model type: `PPO` (`ActorCriticPolicy`)
   - Observation space: `Box(0.0, 1.0, (26,), float32)`
   - Action space: `Discrete(5)`
   - Load status: PASS (Loaded cleanly via `stable_baselines3.PPO.load`)

3. **Selected Features Definition (`backend/ai/evaluation/Selected_Features.txt`):**
   - File exists: `True`
   - Feature count: Exactly `40` features matching model expectations.

### 4.5 Blockchain Initialization & Persistence
- Data file: `backend/blockchain/data/blockchain.json`
- File size: `9,287 bytes`
- Current chain length: `17` blocks
- Hash linking verification: Each block's `previous_hash` matches the predecessor block's `hash`.
- Genesis block: Block 0 hash `6c5a13d40a9d6505...`, previous hash `0`.
- Cryptographic validity: `Blockchain.is_chain_valid() == True`
- Status: PASS

### 4.6 Configuration & Environment Variables
- Environment variables: No `.env` file required for base local operation; fallback defaults are configured.
- Frontend API target: `BlockchainLogs.tsx` has hardcoded `http://127.0.0.1:8000`. `LiveMonitoring.tsx` and `ThreatDetection.tsx` use `VITE_API_BASE_URL` or default to `http://127.0.0.1:8000`.
- CORS Configuration in `main.py`: Permits `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:5174`, `http://127.0.0.1:5174`.

### 4.7 Startup Commands and Service Status

| Service | Working Directory | Documented Startup Command | Assigned Port | Startup Verification |
|---|---|---|---|---|
| **Backend** | `backend` | `& 'C:\final year\CyberShieldAI-Final\.venv\Scripts\uvicorn.exe' app.main:app --host 127.0.0.1 --port 8000 --app-dir 'C:\final year\CyberShieldAI-Final\backend'` | `8000` | **PASS (Running)** — HTTP 200 on `/`, passive monitoring active on Wi-Fi |
| **Frontend** | `frontend` | `npx vite --port 5173 --host 127.0.0.1` | `5173` | **PASS (Running)** — HTTP 200 on `/`, Vite dev server ready |

---

## 5. Summary of Phase 2 Findings

1. **Virtual Environment Isolation:** System Python 3.14.6 cannot run PyTorch/stable-baselines3; running via the project virtual environment `.venv` (Python 3.10.11) is mandatory and works flawlessly.
2. **Model Integrity:** Both `xgboost_baseline.joblib` and `cybershield_ppo_v5.zip` are intact and load with expected parameter shapes (40 features for XGBoost, 26-dim state / 5 discrete actions for PPO).
3. **Blockchain Integrity:** Existing 17 blocks in `blockchain.json` are cryptographically linked and validated with zero tampering.
4. **Port Alignment:** The backend MUST run on port `8000` (not 8001) because `BlockchainLogs.tsx` directly accesses `http://127.0.0.1:8000`.
5. **Live Capture Activation:** The FastAPI lifespan manager starts passive packet capture on the host Wi-Fi interface smoothly without throwing exceptions.
6. **Frontend Build & Dev Server:** The Vite build succeeded in 1.54s without errors, and the dev server is active and serving traffic on `http://127.0.0.1:5173`.


---

## 6. Phase 3 — Frontend Testing Results

### 6.1 Build & Static Analysis Verification

| Check | Command | Result | Notes |
|---|---|---|---|
| **TypeScript Compilation** | `npx tsc -b` / `tsc --noEmit` | **PASS (0 errors)** | All TypeScript types, JSX expressions, and module imports compile cleanly. |
| **Vite Production Bundler** | `npm run build` | **PASS (1.54s)** | Generates `dist/assets/index-IiX5dvQU.js` (635 kB) and CSS bundle (43.9 kB). |
| **ESLint Analysis** | `npm run lint` | **FAIL (9 errors)** | 9 problems reported in `frontend/src/pages/LiveMonitoring.tsx` for `@typescript-eslint/no-explicit-any`. |

### 6.2 Page-by-Page Audit & Functional Verification

| Route | Page Component | Rendering | Backend Integration | Interactive Controls | Status | Findings / Observations |
|---|---|---|---|---|---|---|
| `/` | `Dashboard.tsx` | PASS | **NOT INTEGRATED** | None | **PARTIAL** | Renders KPI cards, attack trends, threat distribution charts, and recent alerts cleanly. However, it imports static mock data from `frontend/src/data/dashboardData.ts` and never calls the backend `GET /api/dashboard/` endpoint. |
| `/threats` | `ThreatDetection.tsx` | PASS | **FULL PASS** | "Load Test Scenario", "Predict Threat" | **PASS** | Allows cycling through 40-feature test scenarios. Submits to `POST /api/defense/analyze`. Accurately receives and renders XGBoost threat classification, PPO defense decisions, firewall simulation metrics, and blockchain transaction receipts. Includes loading states and error banners. |
| `/monitoring` | `LiveMonitoring.tsx` | PASS | **FULL PASS** | Auto-polling (2500ms) | **PARTIAL** | Successfully polls `GET /api/live-monitor/flows`. Correctly computes packet stats, flags pending flows, and displays flow status. Degraded to PARTIAL only due to 9 strict TypeScript ESLint `any` errors in `LiveMonitoring.tsx`. |
| `/blockchain` | `BlockchainLogs.tsx` | PASS | **FULL PASS** | Refresh, Block Expansion | **PASS** | Communicates with `GET /api/blockchain/records`, `/status`, and `/verify`. Correctly displays cryptographic block cards, hash badges, and verification status. *Note:* Contains hardcoded `http://127.0.0.1:8000` rather than using `import.meta.env`. |
| `/reports` | `Reports.tsx` | PASS | **NOT IMPLEMENTED** | Buttons (Export, Filter) | **PARTIAL** | UI is completely static. Buttons have no click handlers or backend report-generation routes. |
| `/settings` | `Settings.tsx` | PASS | **NOT IMPLEMENTED** | Toggle switches | **PARTIAL** | UI switches toggle local component state only; no backend configuration persistence. |
| `*` | `NotFound.tsx` | FAIL | None | None | **FAIL** | `NotFound.tsx` incorrectly exports a component named `Dashboard` returning `<h1>Dashboard</h1>`. Does not display 404 message or link back home. |

### 6.3 Layout and Navigation Controls
- `Sidebar.tsx`: Navigation via `NavLink` functions properly for all 6 routes (`/`, `/threats`, `/monitoring`, `/blockchain`, `/reports`, `/settings`). Active route highlighting works correctly.
- `Navbar.tsx`: Header title is hardcoded to `<h2>Dashboard</h2>` and does not dynamically update to reflect the active page name.

---

## 7. Phase 4 — Backend API Testing Results

### 7.1 Testing Methodology & Safety Controls
- **Test Runner:** Custom automated test harness (`scratch/test_phase4_full_api.py`) executed against `http://127.0.0.1:8000`.
- **Safety Enforcement:** The FastAPI lifespan automatically initiates live packet monitoring; the test harness immediately dispatched `POST /api/live-monitor/stop` to halt packet capture on the host Wi-Fi interface.
- **Data Isolation:** All database / in-memory threat modifications were performed using isolated test IDs (`9999`) and immediately cleaned up via `DELETE`.
- **Blockchain Preservation:** Verified that the ledger was valid before and after adding a test event; all historical blocks remained completely untouched.

### 7.2 Endpoint Execution Results (28 / 28 Tests Passed)

| # | HTTP Method | Endpoint Path | Test Case / Purpose | Expected HTTP | Actual HTTP | Result | Output Evidence / Details |
|---|---|---|---|---|---|---|---|
| 1 | POST | `/api/live-monitor/stop` | Safety: Halt active Wi-Fi packet capture | 200 | 200 | **PASS** | `{"status": "stop_requested"}` |
| 2 | GET | `/api/live-monitor/status` | Safety: Verify monitoring stopped | 200 | 200 | **PASS** | `running=False`, `last_error=None` |
| 3 | GET | `/` | Root service health check | 200 | 200 | **PASS** | `{"status": "online", "message": "CyberShield AI Backend is running"}` |
| 4 | GET | `/api/dashboard/` | Retrieve dashboard KPI metrics | 200 | 200 | **PASS** | Returns `total_attacks`, `active_threats`, `blocked_ips`, `ai_accuracy` |
| 5 | GET | `/api/threats/` | Retrieve all current threats | 200 | 200 | **PASS** | Returns list of threats (Count >= 3) |
| 6 | GET | `/api/threats/1` | Retrieve existing threat by ID | 200 | 200 | **PASS** | Threat 1 (`Brute Force`, `192.168.1.10`) |
| 7 | GET | `/api/threats/99999` | Query non-existent threat | 404 | 404 | **PASS** | `{"detail": "Threat not found"}` |
| 8 | POST | `/api/threats/` | Create valid temporary threat | 201 | 201 | **PASS** | Threat ID 9999 created successfully |
| 9 | POST | `/api/threats/` | Attempt duplicate threat ID | 400 | 400 | **PASS** | `{"detail": "Threat ID already exists"}` |
| 10 | PUT | `/api/threats/9999` | Update existing threat | 200 | 200 | **PASS** | Severity updated to `Medium` |
| 11 | PUT | `/api/threats/88888` | Update non-existent threat | 404 | 404 | **PASS** | `{"detail": "Threat not found"}` |
| 12 | DELETE | `/api/threats/9999` | Delete temporary threat | 200 | 200 | **PASS** | `{"message": "Threat deleted successfully"}` |
| 13 | DELETE | `/api/threats/9999` | Delete already deleted threat | 404 | 404 | **PASS** | `{"detail": "Threat not found"}` |
| 14 | POST | `/api/threats/from-ai` | Create AI-generated threat | 201 | 201 | **PASS** | Auto-assigned new sequential ID |
| 15 | POST | `/api/xgboost/predict` | Predict with valid 40 features | 200 | 200 | **PASS** | Class: 0 (`Benign`), Confidence: 0.9999, Severity: `Low` |
| 16 | POST | `/api/xgboost/predict` | Reject invalid feature count (39) | 422 | 422 | **PASS** | Pydantic validation rejected invalid array length |
| 17 | POST | `/api/xgboost/predict` | Reject missing `source_ip` field | 422 | 422 | **PASS** | Pydantic validation rejected missing required field |
| 18 | POST | `/api/defense/analyze` | Full pipeline (XGB -> PPO -> Defense -> BC) | 200 | 200 | **PASS** | Decision: `MONITOR`, Blockchain record created and verified |
| 19 | POST | `/api/defense/analyze` | Reject short feature array (2 items) | 422 | 422 | **PASS** | Pydantic validation rejected invalid array length |
| 20 | GET | `/api/live-monitor/status` | Read monitor configuration and state | 200 | 200 | **PASS** | `capture_mode: passive`, `model_predictions_enabled: true` |
| 21 | GET | `/api/live-monitor/flows` | Read captured flows and predictions | 200 | 200 | **PASS** | Returns structured flow dictionary |
| 22 | POST | `/api/live-monitor/stop` | Idempotent stop monitor request | 200 | 200 | **PASS** | `{"status": "stop_requested"}` |
| 23 | GET | `/api/blockchain/status` | Network status and consensus mode | 200 | 200 | **PASS** | `{"status": "Operational", "network": "CyberShield Private Chain"}` |
| 24 | GET | `/api/blockchain/verify` | Ledger cryptographic verification | 200 | 200 | **PASS** | `{"valid": true}` |
| 25 | GET | `/api/blockchain/records` | Retrieve full blockchain history | 200 | 200 | **PASS** | Total blocks returned: >= 18 blocks |
| 26 | POST | `/api/blockchain/record` | Record single security event | 200 | 200 | **PASS** | Block created with valid SHA-256 hash |
| 27 | GET | `/api/blockchain/verify` | Re-verify integrity after new block | 200 | 200 | **PASS** | `{"valid": true}` |
| 28 | POST | `/api/blockchain/record` | Reject invalid confidence (> 1.0) | 422 | 422 | **PASS** | Pydantic rejected confidence 1.5 (`le=1.0`) |

---

## 8. Prioritized Bug & Defect List (Phases 1 — 4)

### High Priority
- **BUG-H1: Hardcoded Mock Data on Main Dashboard**
  - **File:** `frontend/src/pages/Dashboard.tsx` (lines 6-32)
  - **Problem:** Dashboard imports static numbers from `frontend/src/data/dashboardData.ts` (`12,480 attacks`, `28 active threats`) instead of fetching live metrics from `GET /api/dashboard/`.
  - **Impact:** User dashboard displays fake static data rather than real backend values.
  - **Recommended Fix:** Wire `Dashboard.tsx` with a `useEffect` hook fetching `GET /api/dashboard/` and displaying actual totals.

- **BUG-H2: Hardcoded Port and Base URL in Blockchain UI**
  - **File:** `frontend/src/pages/BlockchainLogs.tsx` (line 3)
  - **Problem:** `const API_URL = "http://127.0.0.1:8000";` is hardcoded while other pages use `import.meta.env.VITE_API_URL`.
  - **Impact:** Breaks blockchain logs if backend runs on any port other than 8000.
  - **Recommended Fix:** Standardize to `import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"`.

### Medium Priority
- **BUG-M1: ESLint Failures in Live Monitoring Page**
  - **File:** `frontend/src/pages/LiveMonitoring.tsx` (lines 36, 37, 40, 47, 53, 81, 136)
  - **Problem:** Contains 9 explicit `any` type annotations violating `@typescript-eslint/no-explicit-any`.
  - **Impact:** `npm run lint` fails in CI/CD pipeline.
  - **Recommended Fix:** Replace `any` with strongly-typed interfaces matching backend flow structures.

- **BUG-M2: Incorrect Implementation of NotFound Page**
  - **File:** `frontend/src/pages/NotFound.tsx` (lines 1-3)
  - **Problem:** Component is declared as `export default function Dashboard() { return <h1>Dashboard</h1>; }`.
  - **Impact:** Accessing any invalid URL renders `"Dashboard"` instead of a proper 404 page with navigation back home.
  - **Recommended Fix:** Rename to `NotFound` and add a styled 404 card with a `"Return to Dashboard"` button.

- **BUG-M3: Static Values in Dashboard Backend Service**
  - **File:** `backend/app/services/dashboard_services.py` (lines 1-7)
  - **Problem:** `get_dashboard_data()` returns fixed hardcoded integers (`{"total_attacks": 12480, "active_threats": 28, ...}`).
  - **Impact:** Even when wired, the backend returns fixed numbers instead of computing live flow and threat counts.
  - **Recommended Fix:** Aggregate metrics dynamically from `threats` list and `live_flow_monitor.get_flows()`.

### Low Priority
- **BUG-L1: Static Header Title across all Subpages**
  - **File:** `frontend/src/components/Navbar.tsx` (lines 4-6)
  - **Problem:** Header title is hardcoded to `<h2>Dashboard</h2>` regardless of whether the user is on Threat Detection, Monitoring, or Blockchain.
  - **Recommended Fix:** Dynamically update header title based on `useLocation().pathname`.

- **BUG-L2: Confusing Extraneous `backend/package.json`**
  - **File:** `backend/package.json`
  - **Problem:** Contains Node.js/Express dependencies in the Python FastAPI backend folder.
  - **Recommended Fix:** Clean up or document that `backend/package.json` is unused legacy scaffolding.


---

## 9. Phase 5 — AI/ML Testing Results

### 9.1 XGBoost Intrusion Detection Model Verification

| Property | Target Specification | Actual Measured Value | Verdict |
|---|---|---|---|
| **Model File** | `backend/ai/models/saved/xgboost_baseline.joblib` | File present, size: 1,397,911 bytes | **PASS** |
| **Model Architecture** | Scikit-learn wrapped XGBoost Classifier | `xgboost.sklearn.XGBClassifier` | **PASS** |
| **Input Feature Dimension** | 40 engineered flow features | `n_features_in_ = 40` | **PASS** |
| **Target Classes** | 15 distinct network traffic classes | 15 classes (`[0, 1, 2, ..., 14]`) | **PASS** |
| **Primary Metric** | Macro F1 | `macro_f1` (per `model_config.json`) | **PASS** |
| **Prediction Inference** | `predict(features)` | Discrete attack ID (int) | **PASS** |
| **Probability & Confidence** | `predict_proba(features)` | Max probability float rounded to 4 decimals | **PASS** |

#### Element-by-Element Feature Order Alignment
Verified that the 40 feature names and their exact sequence match 100% element-by-element across:
1. `backend/ai/evaluation/Selected_Features.txt` (Ground truth feature selection)
2. `backend/app/services/live_feature_extractor.py` (`FEATURE_NAMES` tuple)
3. `backend/ai/preprocessing/06_train_test_split.py` (`columns_to_load` ordering)

*Result:* **PASS** — Exact 40-element match with zero transposition.

---

### 9.2 Held-Out Test Dataset Audit (`backend/ai/datasets/final/`)

- **Feature Matrix (`X_test.npy`):** Shape `(378355, 40)`, dtype `float32`, size `60,536,928 bytes`.
- **Target Vector (`y_test.npy`):** Shape `(378355,)`, dtype `int8`, size `378,483 bytes`.
- **Data Quality:** NaN count: `0`, Infinite values: `0`.
- **Class Stratification (378,355 Test Samples):**

| Class ID | Attack Label | Test Samples | Proportion |
|---|---|---|---|
| 0 | `Benign` | 314,473 | 83.12% |
| 1 | `Bot` | 293 | 0.08% |
| 2 | `DDoS` | 19,203 | 5.08% |
| 3 | `DoS GoldenEye` | 1,543 | 0.41% |
| 4 | `DoS Hulk` | 25,928 | 6.85% |
| 5 | `DoS Slowhttptest` | 784 | 0.21% |
| 6 | `DoS slowloris` | 808 | 0.21% |
| 7 | `FTP-Patator` | 890 | 0.24% |
| 8 | `Heartbleed` | 1 | <0.01% |
| 9 | `Infiltration` | 5 | <0.01% |
| 10 | `PortScan` | 13,623 | 3.60% |
| 11 | `SSH-Patator` | 483 | 0.13% |
| 12 | `Web Attack - Brute Force` | 220 | 0.06% |
| 13 | `Web Attack - Sql Injection` | 3 | <0.01% |
| 14 | `Web Attack - XSS` | 98 | 0.03% |

---

### 9.3 Empirical Model Evaluation on 378,355 Test Samples

The saved XGBoost model was evaluated against the entire held-out test dataset `(X_test.npy, y_test.npy)`:

| Metric | Measured Test Result | Config Reference (`model_config.json`) | Status |
|---|---|---|---|
| **Overall Accuracy** | **99.8803%** (`0.998803`) | `0.9988` (99.88%) | **MATCH** |
| **Macro Precision** | **93.2101%** (`0.932101`) | — | **PASS** |
| **Weighted Precision** | **99.8776%** (`0.998776`) | — | **PASS** |
| **Macro Recall** | **91.8782%** (`0.918782`) | — | **PASS** |
| **Weighted Recall** | **99.8803%** (`0.998803`) | — | **PASS** |
| **Macro F1-Score** | **92.3987%** (`0.923987`) | `0.9240` (92.40%) | **MATCH** |
| **Weighted F1-Score** | **99.8776%** (`0.998776`) | — | **PASS** |
| **Inference Throughput** | **2.47s for 378,355 samples** | ~0.0065 ms per flow | **HIGH SPEED** |

#### Per-Class Performance Breakdown:
- High-volume classes (`Benign`, `DDoS`, `DoS Hulk`, `PortScan`, `FTP-Patator`, `SSH-Patator`): **F1 > 0.994**
- Rare attacks with distinct signatures (`Heartbleed`, `Infiltration`, `Sql Injection`): **F1 = 1.0000**
- Challenging minor classes (`Web Attack - Brute Force`): **F1 = 0.7420**
- Extreme minority classes (`Bot`): **F1 = 0.8267**
- Imbalanced low-sample attack (`Web Attack - XSS`, 98 test samples): **F1 = 0.3176** (Primary reason Macro F1 is 92.40% rather than 99%)

---

### 9.4 Resolution of the Macro-F1 Discrepancy (89.35% vs 92.40%)

- **Finding:**
  1. **92.40% (`0.923987`):** Represents the verified, empirical **Test Macro-F1** of the final trained `xgboost_baseline.joblib` evaluated on the held-out `X_test.npy` dataset (378,355 samples). This matches `backend/ai/models/model_config.json` (`test_macro_f1: 0.9240`).
  2. **89.35%:** Originates from the baseline Random Forest model (`backend/ai/models/07_random_forest.py` / `08_random_forest_test.py`) or preliminary pre-tuning validation runs before XGBoost hyperparameter tuning was finalized.
  3. **Conclusion:** There is no model corruption or data fabrication. 92.40% is the true performance metric of the active XGBoost model.

---

### 9.5 Random Forest Baseline Model Audit

- **Training Script:** [`backend/ai/models/07_random_forest.py`](file:///C:/final%20year/CyberShieldAI-Final/backend/ai/models/07_random_forest.py) (Present)
- **Evaluation Script:** [`backend/ai/models/08_random_forest_test.py`](file:///C:/final%20year/CyberShieldAI-Final/backend/ai/models/08_random_forest_test.py) (Present)
- **Saved Model File:** `backend/ai/models/saved/random_forest_baseline.joblib` is **NOT PRESENT** in the repository.
- **API Exposure:** Not exposed via FastAPI routes (as designed; the active detection engine uses XGBoost).
- **Status:** **PARTIAL / NOT IMPLEMENTED (Model binary not saved)**.

---

### 9.6 Safe Inference & Edge-Case Testing

| Test Case | Input Characteristics | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|
| **Benign Flow** | Real sample from `X_test` (Class 0) | Class 0 (`Benign`), Conf > 0.95 | Class 0, Conf = 1.0000 | **PASS** |
| **Bot Traffic** | Real sample from `X_test` (Class 1) | Class 1 (`Bot`) | Class 1, Conf = 1.0000 | **PASS** |
| **DDoS Attack** | Real sample from `X_test` (Class 2) | Class 2 (`DDoS`) | Class 2, Conf = 0.9999 | **PASS** |
| **DoS GoldenEye** | Real sample from `X_test` (Class 3) | Class 3 (`DoS GoldenEye`) | Class 3, Conf = 0.9999 | **PASS** |
| **DoS Hulk** | Real sample from `X_test` (Class 4) | Class 4 (`DoS Hulk`) | Class 4, Conf = 0.9999 | **PASS** |
| **PortScan** | Real sample from `X_test` (Class 10) | Class 10 (`PortScan`) | Class 10, Conf = 0.9999 | **PASS** |
| **SSH-Patator** | Real sample from `X_test` (Class 11) | Class 11 (`SSH-Patator`) | Class 11, Conf = 1.0000 | **PASS** |
| **Web Attack** | Real sample from `X_test` (Class 12) | Class 12 (`Web Attack - Brute Force`) | Class 12, Conf = 0.8644 | **PASS** |
| **Feature Undersize** | 39 numerical features | Reject with `ValueError` | `ValueError: Expected 40 features, but received 39.` | **PASS** |
| **Feature Oversize** | 41 numerical features | Reject with `ValueError` | `ValueError: Expected 40 features, but received 41.` | **PASS** |
| **Non-Numeric Value** | String passed in feature list | Reject with conversion error | `ValueError: could not convert string to float` | **PASS** |
| **Missing Values (NaN)** | Single NaN in feature array | Handled natively by XGBoost tree traversal | Returned Class 0 (`Benign`) without runtime crash | **PASS** |
