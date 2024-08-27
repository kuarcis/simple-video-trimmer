import gettext
import os

def setup_locales(lang):
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    translate = gettext.translation('messages', localedir, languages=[lang], fallback=True)
    translate.install()
    return translate.gettext

# Define the global _ function
translate = setup_locales('tw')  # Default to Traditional Chinese

def change_language(lang):
    global translate
    translate = setup_locales(lang)