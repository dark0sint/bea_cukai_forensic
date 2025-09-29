   from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
   import json
   import os
   import hashlib
   from datetime import datetime
   from cryptography.fernet import Fernet
   import base64

   app = Flask(__name__)
   app.secret_key = 'super_secret_key_bea_cukai'  # Ganti untuk produksi

   # File paths
   DATA_FILE = 'kepabeanan_data.json'
   LOG_FILE = 'forensic_log.txt'
   KEY_FILE = 'secret.key'

   # Generate or load encryption key for logs
   if not os.path.exists(KEY_FILE):
       key = Fernet.generate_key()
       with open(KEY_FILE, 'wb') as f:
           f.write(key)
   with open(KEY_FILE, 'rb') as f:
       key = f.read()
   cipher = Fernet(key)

   # Demo users (hardcoded - gunakan database untuk produksi)
   USERS = {'admin': 'bea_cukai123'}

   # Load/Save data
   def load_data():
       if os.path.exists(DATA_FILE):
           with open(DATA_FILE, 'r') as f:
               return json.load(f)
       return {'activities': []}

   def save_data(data):
       with open(DATA_FILE, 'w') as f:
           json.dump(data, f, indent=4)

   # Forensic log function (encrypted with hash for integrity)
   def log_activity(user, action, details):
       timestamp = datetime.now().isoformat()
       entry = f"{timestamp}|{user}|{action}|{details}"
       hashed_entry = hashlib.sha256(entry.encode()).hexdigest()  # Hash for integrity
       encrypted_entry = cipher.encrypt(entry.encode()).decode()
       with open(LOG_FILE, 'a') as f:
           f.write(f"{encrypted_entry}|{hashed_entry}\n")

   @app.route('/')
   def index():
       if 'user' not in session:
           return redirect(url_for('login'))
       return render_template('index.html', user=session['user'])

   @app.route('/login', methods=['GET', 'POST'])
   def login():
       if request.method == 'POST':
           username = request.form['username']
           password = request.form['password']
           if username in USERS and USERS[username] == password:
               session['user'] = username
               log_activity(username, 'LOGIN', 'Successful login')
               return redirect(url_for('index'))
           else:
               flash('Login gagal!')
               log_activity(username, 'LOGIN_FAILED', f'Invalid credentials for {username}')
       return render_template('login.html')

   @app.route('/logout')
   def logout():
       if 'user' in session:
           log_activity(session['user'], 'LOGOUT', 'User  logged out')
           session.pop('user', None)
       return redirect(url_for('login'))

   @app.route('/track', methods=['GET', 'POST'])
   def track():
       if 'user' not in session:
           return redirect(url_for('login'))
       data = load_data()
       if request.method == 'POST':
           activity = {
               'id': len(data['activities']) + 1,
               'container': request.form['container'],
               'type': request.form['type'],  # impor/ekspor
               'value': request.form['value'],
               'date': datetime.now().isoformat(),
               'status': 'Pending'
           }
           data['activities'].append(activity)
           save_data(data)
           log_activity(session['user'], 'TRACK_ACTIVITY', f"Added: {activity}")
           flash('Aktivitas ditambahkan!')
       return render_template('track.html', activities=data['activities'])

   @app.route('/forensic')
   def forensic():
       if 'user' not in session:
           return redirect(url_for('login'))
       logs = []
       if os.path.exists(LOG_FILE):
           with open(LOG_FILE, 'r') as f:
               for line in f:
                   parts = line.strip().split('|')
                   if len(parts) == 2:
                       encrypted = parts[0]
                       hash_val = parts[1]
                       try:
                           decrypted = cipher.decrypt(encrypted.encode()).decode()
                           # Verify hash
                           entry = decrypted
                           if hashlib.sha256(entry.encode()).hexdigest() == hash_val:
                               logs.append(entry.split('|'))
                       except:
                           continue  # Skip invalid logs
       # Filter logs (simple query via GET params)
       query = request.args.get('query', '')
       filtered_logs = [log for log in logs if query.lower() in ' '.join(log).lower()]
       return render_template('forensic.html', logs=filtered_logs, query=query)

   if __name__ == '__main__':
       app.run(debug=True)
   
