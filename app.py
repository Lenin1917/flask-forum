from flask import Flask

app = Flask(__name__)
app.secret_key = 'dasfap;sdofaposdvposdfbpoaesrfpgoqawpefasjdvldksvasd' 

import view
import auth
import db