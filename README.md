# SOS Audio Detection — שומר הבית

פרויקט זיהוי קולות מצוקה (בכי תינוק) בזמן אמת באמצעות בינה מלאכותית.

## מבנה הפרויקט
```
SOS-Audio-Detection/
├── backend/            # שרת FastAPI
│   └── main.py
├── frontend/           # ממשק React
│   └── src/
├── src/                # קוד עיבוד ואינפרנס
│   ├── audio_utils.py
│   ├── realtime_detector.py
│   └── training/
│       ├── prepare_data.py
│       ├── preprocess.py
│       └── train.py
├── models/             # מודל מאומן וסטטיסטיקות נרמול
│   ├── sos_model.keras
│   └── norm_stats.json
├── notebooks/          # מחברות Jupyter לניסויים
│   └── train_colab.ipynb
├── outputs/            # תוצאות אימון (גרפים וכו')
│   └── confusion_matrix.png
├── data/
│   ├── raw/            # קבצי WAV מקוריים לפי קטגוריה
│   └── processed/      # ספקטרוגרמות מעובדות (.npy)
├── .env.example        # תבנית משתני סביבה
├── requirements.txt
└── README.md
```

## התקנה

```bash
pip install -r requirements.txt
```

העתק את `.env.example` ל-`.env` ומלא את הערכים:
```bash
cp .env.example .env
```

## הרצה

**Backend:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

**זיהוי בזמן אמת (ללא UI):**
```bash
python src/realtime_detector.py
```

## אימון מחדש

```bash
python src/training/prepare_data.py   # הכנת נתונים
python src/training/preprocess.py     # עיבוד מקדים
python src/training/train.py          # אימון המודל
```
