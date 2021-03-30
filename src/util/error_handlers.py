from flask import jsonify, make_response, render_template, session, redirect, Markup

headers = {'Content-Type': 'text/html'}

def page_not_found(e):
  print(e)
  notFound = {
     "description": "not found"
  }
  return make_response(render_template('404.html', notFound=notFound), 404, headers)
