"""
Configuration file for Governorate Strategic Plan Dashboard (English Version)
"""

SHEET_ID = "1g6vWMzylEvSmv9ixgy5haabs5d-axokNKoc9Y9fLcYs"
GID = "169902006"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}#gid={GID}"
CSV_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# Cache expiration in seconds for live Google Sheets sync
CACHE_TTL_SECONDS = 30

# Branding & Color Palette (Healthcare Executive Theme)
COLORS = {
    'primary': '#0F172A',         # Slate / Dark Navy
    'primary_light': '#1E293B',   # Card Navy Background
    'accent': '#0EA5E9',          # Sky Blue
    'accent_teal': '#14B8A6',     # Teal
    'completed': '#10B981',       # Emerald Green
    'in_progress': '#3B82F6',     # Royal Blue
    'delayed': '#EF4444',         # Crimson Red
    'text': '#F8FAFC',            # Light Text
    'text_muted': '#94A3B8',      # Muted Gray
    'high_priority': '#DC2626',   # Dark Red
    'medium_priority': '#F59E0B'  # Amber Gold
}

STATUS_MAP_EN = {
    'Completed': 'Completed 🟢',
    'in progress': 'In Progress 🔵',
    'delayed': 'Delayed 🔴'
}

PRIORITY_MAP_EN = {
    'High': 'High ⚠️',
    'Medium': 'Medium ⚡',
    'Low': 'Low ℹ️'
}
