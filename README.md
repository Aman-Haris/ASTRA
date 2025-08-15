# **ASTRA 🌠**

***Asteroid Threat Scoring & Trajectory Analysis***

*An AI-powered system for predicting asteroid trajectories, assessing collision threats, and enabling real-time planetary defense insights.*

---

## **🚀 Mission Statement**

ASTRA is designed to:

1. **Predict asteroid trajectories** using Graph Neural Networks (GNNs).
2. **Quantify collision risk** through Bayesian threat scoring.
3. **Visualize asteroid threats** in real-time for scientists, agencies, and researchers.

---

## **📡 Data Flow Overview**

```plaintext
[NASA APIs] → [ASTRA Pipeline] → [PostgreSQL DB] → [GNN Training & Prediction]
↑
[External Sources] ← [Scheduled Updates]
```

---

## **🛰 Data Sources**

| Source         | Description            | Data Type                |
| -------------- | ---------------------- | ------------------------ |
| **NASA NeoWS** | Near-Earth Object data | Orbital parameters       |
| **JPL SBDB**   | Small-Body Database    | Object characteristics   |
| **MPC**        | Minor Planet Center    | Catalog & discovery data |
| **DONKI CAD**  | Close Approach Data    | Historical encounters    |

---

## **⚙️ Setup Guide**

### **1️⃣ Prerequisites**

```bash
# Install PostgreSQL (Linux example)
sudo apt-get install postgresql postgresql-contrib

# Install Python dependencies
pip install -r requirements.txt
```

---

### **2️⃣ Database Setup**

**Windows (pgAdmin):**

1. Open **pgAdmin 4**.
2. Create a database:

   * Name: `astra`
   * Owner: `postgres`
3. (Optional) Create a dedicated user:

   * Username: `astra_user`
   * Password: `secure_password`
4. Set credentials in **`config/config.yaml`**.

**CLI:**

```bash
# Initialize DB
python scripts/init_db.py
```

---

### **3️⃣ Running the Pipeline**

```bash
# First-time data fetch (sample NEOs)
python src/pipeline/fetch.py --init

# Preprocess raw data
python src/pipeline/preprocess.py --input data/raw/ --output data/processed/

# Manual update
python scripts/scheduled_update.py
```

---

### **4️⃣ Scheduled Updates**

```bash
# Add to crontab (example: daily at 3 AM)
0 3 * * * /path/to/python /path/to/ASTRA/scripts/scheduled_update.py >> update.log 2>&1
```

---

## **📂 Repository Structure**

```plaintext
ASTRA/
├── src/
│   ├── pipeline/           # ETL + data pipeline scripts
│   │   ├── fetch.py        # Enhanced data fetching
│   │   ├── preprocess.py   # Data preprocessing
│   │   ├── database.py     # PostgreSQL interface
│   │   └── update.py       # Scheduled updates
│   │
│   ├── models/             # GNN & ML models
│   └── visualization/      # Dashboard code
│
├── config/                 # Config files & SQL queries
├── scripts/                # DB init and automation scripts
└── requirements.txt
```

---

## **📊 Example Queries**

Find reusable queries in **`config/queries.sql`**:

* Get hazardous asteroids
* Find upcoming close approaches
* Retrieve datasets for model training

---

## **🛠 Development**

```bash
# Run tests
pytest tests/

# Format code
black src/
```

🔑 **Note:** NASA API key required — [Get it here](https://api.nasa.gov).

---

## **🤝 Contributing**

Contributions are welcome!

* Improve GNN models
* Add new asteroid data sources
* Enhance dashboard visualizations

---

## **📜 License**

MIT License — feel free to use, modify, and share.