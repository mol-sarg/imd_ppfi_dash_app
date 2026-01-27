# app.py
from dash import Dash, html
import dash
from layouts.main_layout import layout

app = Dash(__name__, suppress_callback_exceptions=True)

# register callbacks
import callbacks.navigation_callbacks
import callbacks.map_callbacks
import callbacks.stats_callbacks
import callbacks.mismatch_callbacks
import callbacks.compare_domain_callbacks

# set layout on import
app.layout = layout
server = app.server
