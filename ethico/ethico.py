import reflex as rx

from ethico.pages.login import login_page
from ethico.pages.about import about
from ethico.pages.index import index
    
   
app = rx.App()
app.add_page(index, route="/", title="THUFIR")
app.add_page(about, route="/about", title="About THUFIR")
app.add_page(login_page, route="/login", title="Login")