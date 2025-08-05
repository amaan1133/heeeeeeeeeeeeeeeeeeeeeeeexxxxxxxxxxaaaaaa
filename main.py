
import os
import sys
import logging

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', application_path)
    data_path = application_path
else:
    base_path = application_path
    data_path = application_path
os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(data_path, "hexamed.db")}'
os.environ['UPLOAD_FOLDER'] = os.path.join(data_path, 'uploads')
uploads_dir = os.environ['UPLOAD_FOLDER']
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    with open(os.path.join(uploads_dir, '.gitkeep'), 'w') as f:
        f.write('')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from app import app
    
    if __name__ == '__main__':
        print("Starting Hexamed Asset Management System...")
        print(f"Database: {os.environ['DATABASE_URL']}")
        print(f"Uploads: {os.environ['UPLOAD_FOLDER']}")
        print("Access the application at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except Exception as e:
    print(f"Error starting application: {e}")
    logging.error(f"Application startup error: {e}", exc_info=True)
    input("Press Enter to exit...")
    sys.exit(1)
