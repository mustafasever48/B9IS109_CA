from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask_cors import CORS
import json
from datetime import datetime
from flask import jsonify


