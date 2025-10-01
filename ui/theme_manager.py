# ui/theme_manager.py

THEMES = {
    "Oscuro": {
        "main_bg": "#1e1e1e",
        "card_bg": "#2d2d2d",
        "text": "#ffffff",
        "text_secondary": "#aaaaaa",
        "accent": "#0078d7",
        "favorite": "#FFD700"
    },
    "Claro": {
        "main_bg": "#f0f0f0",
        "card_bg": "#ffffff",
        "text": "#000000",
        "text_secondary": "#555555",
        "accent": "#005a9e",
        "favorite": "#FF8C00"
    },
    "Retro": {
        "main_bg": "#0f0f23",
        "card_bg": "#1a1a2e",
        "text": "#00ffcc",
        "text_secondary": "#00aa88",
        "accent": "#ff2a6d",
        "favorite": "#ffd700"
    },
    "Neón": {
        "main_bg": "#000000",
        "card_bg": "#111111",
        "text": "#00ffff",
        "text_secondary": "#ff00ff",
        "accent": "#00ff00",
        "favorite": "#ffff00"
    }
}

def apply_theme(app, theme_name):
    theme = THEMES.get(theme_name, THEMES["Oscuro"])
    app.setStyleSheet(f"""
        QMainWindow, QWidget {{ 
            background-color: {theme['main_bg']}; 
            color: {theme['text']}; 
        }}
        QListWidget {{
            background-color: {theme['main_bg']};
            color: {theme['text']};
            border: none;
        }}
        QListWidget::item {{
            padding: 10px;
            font-size: 14px;
        }}
        QListWidget::item:selected {{
            background-color: {theme['accent']};
            color: white;
        }}
        QLabel {{ color: {theme['text']}; }}
        QPushButton {{
            background-color: {theme['accent']};
            color: white;
            border: none;
            padding: 8px;
            border-radius: 5px;
        }}
        QToolButton {{
            color: {theme['favorite']};
            background: transparent;
            border: none;
            font-size: 20px;
        }}
    """)
    return theme