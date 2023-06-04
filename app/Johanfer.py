from dash import dash
from dash import dcc
from dash import html

# Crear una instancia de la aplicación Dash
app = dash.Dash(__name__)

# Definir el diseño de la aplicación
app.layout = html.Div(
    children=[
        html.H1('¡Hola, mundo!'),
        html.P('Bienvenido a Dash')
    ]
)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
