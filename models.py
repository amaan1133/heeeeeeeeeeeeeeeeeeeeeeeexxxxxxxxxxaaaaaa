
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='User') 
    full_name = db.Column(db.String(100), nullable=False)
    floor = db.Column(db.String(50))  
    department = db.Column(db.String(100))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    requests = db.relationship('AssetRequest', foreign_keys='AssetRequest.user_id', backref='requester', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class AssetRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    request_type = db.Column(db.String(50), nullable=False) 
    estimated_cost = db.Column(db.Float)
    urgency = db.Column(db.String(20), default='Normal')  

    status = db.Column(db.String(20), default='Pending') 
    current_approval_level = db.Column(db.Integer, default=1)
    floor = db.Column(db.String(50))  
    
    fulfilled_from_asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    fulfilled_quantity = db.Column(db.Integer, default=0)
    fulfilled_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    fulfilled_at = db.Column(db.DateTime)
    fulfillment_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    uploaded_files = db.relationship('UploadedFile', backref='request', lazy=True, cascade='all, delete-orphan')
    approvals = db.relationship('Approval', backref='request', lazy=True, cascade='all, delete-orphan')
    fulfilled_from_asset = db.relationship('Asset', foreign_keys=[fulfilled_from_asset_id])
    fulfilled_by_user = db.relationship('User', foreign_keys=[fulfilled_by])

    def __repr__(self):
        return f'<AssetRequest {self.item_name}>'

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    request_id = db.Column(db.Integer, db.ForeignKey('asset_request.id'), nullable=False)

    def __repr__(self):
        return f'<UploadedFile {self.original_filename}>'

class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    approval_level = db.Column(db.Integer, nullable=False)  
    action = db.Column(db.String(20), nullable=False)  
    comments = db.Column(db.Text)
    approved_at = db.Column(db.DateTime, default=datetime.utcnow)

    request_id = db.Column(db.Integer, db.ForeignKey('asset_request.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    approver = db.relationship('User', backref='approvals')

    def __repr__(self):
        return f'<Approval {self.action} by {self.approver.username}>'

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('asset_request.id'), nullable=True)

    user = db.relationship('User', backref='activities')
    request = db.relationship('AssetRequest', backref='activities')

    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user.username}>'

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)  
    asset_type = db.Column(db.String(50), default='Fixed Asset')  # Fixed Asset or Consumable Asset
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)
    current_value = db.Column(db.Float)
    condition = db.Column(db.String(50), default='Good')  
    location = db.Column(db.String(200))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default='Available')  
    warranty_expiry = db.Column(db.Date)
    notes = db.Column(db.Text)

    # Inventory fields for consumable assets
    current_quantity = db.Column(db.Integer, default=1)
    minimum_threshold = db.Column(db.Integer, default=5)
    unit_of_measurement = db.Column(db.String(50), default='Piece')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_user = db.relationship('User', backref='assigned_assets')

    @property
    def is_below_threshold(self):
        """Check if consumable asset is below minimum threshold"""
        return (self.asset_type == 'Consumable Asset' and 
                self.current_quantity <= self.minimum_threshold)

    def __repr__(self):
        return f'<Asset {self.asset_tag} - {self.name}>'

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(100), unique=True, nullable=False)
    vendor_name = db.Column(db.String(200), nullable=False)
    bill_amount = db.Column(db.Float, nullable=False)
    bill_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    bill_file_path = db.Column(db.String(500))  # Path to uploaded bill file
    bill_filename = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Pending')  # Pending, Verified, Rejected
    verification_comments = db.Column(db.Text)

    # Link to request
    request_id = db.Column(db.Integer, db.ForeignKey('asset_request.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    request = db.relationship('AssetRequest', backref='bills')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_bills')
    verifier = db.relationship('User', foreign_keys=[verified_by], backref='verified_bills')

    def __repr__(self):
        return f'<Bill {self.bill_number} - {self.vendor_name}>'

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    vendor_code = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))  # IT Equipment, Furniture, etc.
    payment_terms = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vendor {self.vendor_name}>'

class ItemAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    delivery_status = db.Column(db.String(50), default='Pending')  # Pending, In Transit, Delivered
    notes = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = db.relationship('Vendor', backref='item_assignments')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assignments_made')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assignments_received')

    def __repr__(self):
        return f'<ItemAssignment {self.item_name} to {self.assignee.full_name}>'

class InventoryUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    previous_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    update_type = db.Column(db.String(50), nullable=False)  # Addition, Consumption, Adjustment
    reason = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref='inventory_updates')
    updater = db.relationship('User', backref='inventory_updates')

    def __repr__(self):
        return f'<InventoryUpdate {self.asset.name} - {self.update_type}>'

class AssetMaintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # Preventive, Corrective, Predictive
    scheduled_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date)
    cost = db.Column(db.Float)
    service_provider = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    next_maintenance_date = db.Column(db.Date)
    maintenance_notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = db.relationship('Asset', backref='maintenance_records')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_maintenances')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_maintenances')

    def __repr__(self):
        return f'<AssetMaintenance {self.asset.asset_tag} - {self.maintenance_type}>'

class AssetDepreciation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    depreciation_method = db.Column(db.String(50), default='Straight Line') 
    useful_life_years = db.Column(db.Integer, nullable=False)
    salvage_value = db.Column(db.Float, default=0)
    annual_depreciation = db.Column(db.Float, nullable=False)
    accumulated_depreciation = db.Column(db.Float, default=0)
    book_value = db.Column(db.Float, nullable=False)
    depreciation_start_date = db.Column(db.Date, nullable=False)
    last_calculated_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = db.relationship('Asset', backref='depreciation_record', uselist=False)

    def calculate_current_depreciation(self):
        """Calculate current depreciation based on time elapsed"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if not self.depreciation_start_date:
            return 0
        
        today = date.today()
        months_elapsed = relativedelta(today, self.depreciation_start_date).years * 12 + relativedelta(today, self.depreciation_start_date).months
        
        total_depreciation = (months_elapsed / 12) * self.annual_depreciation
        return min(total_depreciation, self.asset.purchase_cost - self.salvage_value)

    def update_book_value(self):
        """Update book value based on current depreciation"""
        self.accumulated_depreciation = self.calculate_current_depreciation()
        self.book_value = self.asset.purchase_cost - self.accumulated_depreciation
        self.last_calculated_date = datetime.utcnow().date()

    def __repr__(self):
        return f'<AssetDepreciation {self.asset.asset_tag} - Book Value: ${self.book_value}>'

class WarrantyAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  
    alert_date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    acknowledged_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref='warranty_alerts')
    acknowledger = db.relationship('User', backref='acknowledged_alerts')

    def __repr__(self):
        return f'<WarrantyAlert {self.asset.asset_tag} - {self.alert_type}>'

class ProcurementQuotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('asset_request.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    quotation_number = db.Column(db.String(100), unique=True, nullable=False)
    quoted_price = db.Column(db.Float, nullable=False)
    quoted_quantity = db.Column(db.Integer, nullable=False)
    delivery_timeline = db.Column(db.String(100))  
    validity_period = db.Column(db.Integer, default=30)  
    payment_terms = db.Column(db.String(200))
    warranty_period = db.Column(db.String(100))
    specifications = db.Column(db.Text)
    additional_costs = db.Column(db.Float, default=0)  
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  
    evaluation_score = db.Column(db.Float)  
    evaluation_notes = db.Column(db.Text)
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    evaluated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    quotation_file_path = db.Column(db.String(500))
    quotation_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    request = db.relationship('AssetRequest', backref='quotations')
    vendor = db.relationship('Vendor', backref='quotations')
    submitter = db.relationship('User', foreign_keys=[submitted_by], backref='submitted_quotations')
    evaluator = db.relationship('User', foreign_keys=[evaluated_by], backref='evaluated_quotations')

    @property
    def cost_per_unit(self):
        return self.total_cost / self.quoted_quantity if self.quoted_quantity > 0 else 0

    def __repr__(self):
        return f'<ProcurementQuotation {self.quotation_number} - {self.vendor.vendor_name}>'
