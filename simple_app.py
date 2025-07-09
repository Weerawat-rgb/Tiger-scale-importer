from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
import os
from config import Config
from database import DatabaseManager
from excel_generator import ExcelGenerator
from datetime import datetime

# ระบุ template folder ชัดเจน
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Config)

# Debug template folder
print(f"Template folder: {template_dir}")
print(f"Template folder exists: {os.path.exists(template_dir)}")
if os.path.exists(template_dir):
    print(f"Template files: {os.listdir(template_dir)}")

# Initialize components
db_manager = DatabaseManager()
excel_generator = ExcelGenerator(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    """หน้าแรก - ตรวจสอบการล็อกอิน"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """หน้าล็อกอิน"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ตรวจสอบ credentials
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['username'] = username
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    # Try template file first, fallback to simple HTML
    try:
        return render_template('login.html')
    except:
        # Simple login page as fallback
        login_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>เข้าสู่ระบบ</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container">
                <div class="row justify-content-center mt-5">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h3 class="text-center mb-4">เข้าสู่ระบบ</h3>
                                <form method="POST">
                                    <div class="mb-3">
                                        <label class="form-label">ชื่อผู้ใช้</label>
                                        <input type="text" class="form-control" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">รหัสผ่าน</label>
                                        <input type="password" class="form-control" name="password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">เข้าสู่ระบบ</button>
                                </form>
                                <div class="text-center mt-3">
                                    <small class="text-muted">ทดสอบ: admin / 1234</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        from flask import render_template_string
        return render_template_string(login_html)

@app.route('/logout')
def logout():
    """ล็อกเอาท์"""
    session.clear()
    flash('ออกจากระบบแล้ว', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """หน้าแดชบอร์ด - แสดงรายละเอียดสินค้า"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # ดึงข้อมูลสินค้า
    products_df = db_manager.get_products_summary()
    
    if products_df is not None:
        products = products_df.to_dict('records')
        total_products = len(products)
        
        # จัดกลุ่มตาม category
        grouped_products = {}
        for product in products:
            category = product.get('category_name') or 'ไม่ระบุหมวดหมู่'
            if category not in grouped_products:
                grouped_products[category] = []
            grouped_products[category].append(product)
        
        # เรียงลำดับ category
        grouped_products = dict(sorted(grouped_products.items()))
        
    else:
        products = []
        total_products = 0
        grouped_products = {}
        flash('ไม่สามารถดึงข้อมูลสินค้าได้', 'error')
    
    return render_template('dashboard.html', 
                         products=products,
                         grouped_products=grouped_products,
                         total_products=total_products,
                         username=session.get('username', ''))

@app.route('/generate_excel')
def generate_excel():
    """สร้างไฟล์ Excel"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        filepath, message = excel_generator.generate_excel_file(session.get('username', 'admin'))
        
        if filepath:
            flash(message, 'success')
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        else:
            flash(message, 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/test_connection')
def test_connection():
    """ทดสอบการเชื่อมต่อฐานข้อมูล"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': 'ไม่ได้เข้าสู่ระบบ'})
    
    try:
        success = db_manager.test_connection()
        if success:
            return jsonify({'success': True, 'message': 'เชื่อมต่อฐานข้อมูลสำเร็จ'})
        else:
            return jsonify({'success': False, 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/refresh_data')
def refresh_data():
    """รีเฟรชข้อมูลสินค้า"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': 'ไม่ได้เข้าสู่ระบบ'})
    
    try:
        products_df = db_manager.get_products_summary()
        if products_df is not None:
            products = products_df.to_dict('records')
            
            # จัดกลุ่มตาม category
            grouped_products = {}
            for product in products:
                category = product.get('category_name') or 'ไม่ระบุหมวดหมู่'
                if category not in grouped_products:
                    grouped_products[category] = []
                grouped_products[category].append(product)
            
            # เรียงลำดับ category
            grouped_products = dict(sorted(grouped_products.items()))
            
            return jsonify({
                'success': True, 
                'products': products,
                'grouped_products': grouped_products,
                'total_products': len(products)
            })
        else:
            return jsonify({'success': False, 'message': 'ไม่สามารถดึงข้อมูลสินค้าได้'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # สร้างโฟลเดอร์ downloads ถ้ายังไม่มี
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True, host='0.0.0.0', port=5000)