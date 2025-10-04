# utils/translations.py
TRANSLATIONS = {
    "es": {
        "app_title": "Multiverse Gamer Emulador",
        "login": "Iniciar Sesión",
        "register": "Crear Cuenta",
        "email": "Email",
        "password": "Contraseña",
        "play": "Jugar",
        "favorites": "Favoritos",
        "settings": "Configuración",
        "theme": "Tema",
        "big_picture": "Modo Big Picture",
        "stats": "Estadísticas",
        "games_played": "Juegos más jugados",
        "total_hours": "Horas totales"
    },
    "en": {
        "app_title": "Multiverse Gamer Emulator",
        "login": "Login",
        "register": "Sign Up",
        "email": "Email",
        "password": "Password",
        "play": "Play",
        "favorites": "Favorites",
        "settings": "Settings",
        "theme": "Theme",
        "big_picture": "Big Picture Mode",
        "stats": "Statistics",
        "games_played": "Most Played Games",
        "total_hours": "Total Hours"
    }
}

def tr(key: str, lang: str = "es") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)