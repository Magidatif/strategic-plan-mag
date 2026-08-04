"""
Configuration file for Governorate Strategic Plan Dashboard (English Version)
"""

SHEET_SOURCES = {
    "1g8Hj76hwEpDyw4fveVG-zSV909NvoiIrbszGxL8JmNY": "Luxor",
    "1ozzKaEBsa66yLowO2PA60vRFXDCDochhGu4sLjyW0iM": "Ismailia",
    "1jzNhXxuSL6wkVOgO3HCVsf9eAMVR4kBVerDI-hFc4Rw": "Suez",
    "1fAF5fE98QtRsJe_FNqa1IL7SQhdMH_7ZMjQ6sdE0xe4": "Aswan",
    "12O43L7eTbYcUuXv6UAfCcFgiRTDSN51QeD33_zs0FSI": "Port Said",
    "1ra91ajdyoiHr1-sFb2GG8f6veWWcLdxmE_tjYJK73Ag": "South Sinai"
}

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
