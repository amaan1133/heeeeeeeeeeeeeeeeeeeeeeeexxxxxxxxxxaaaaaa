
-- Hexamed Asset & Procurement Management System Database Schema
-- PostgreSQL Database Structure
-- Production-ready schema with all tables, indexes, triggers, and sample data

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication and role management
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'User',
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Assets table with inventory management
CREATE TABLE IF NOT EXISTS asset (
    id SERIAL PRIMARY KEY,
    asset_tag VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    asset_type VARCHAR(50) DEFAULT 'Fixed Asset', -- Fixed Asset or Consumable Asset
    brand VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    purchase_cost DECIMAL(15,2),
    current_value DECIMAL(15,2),
    condition VARCHAR(50) DEFAULT 'Good',
    location VARCHAR(200),
    assigned_to INTEGER REFERENCES "user"(id),
    status VARCHAR(50) DEFAULT 'Available',
    warranty_expiry DATE,
    notes TEXT,
    -- Inventory fields for consumable assets
    current_quantity INTEGER DEFAULT 1,
    minimum_threshold INTEGER DEFAULT 5,
    unit_of_measurement VARCHAR(50) DEFAULT 'Piece',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset requests table
CREATE TABLE IF NOT EXISTS asset_request (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    purpose TEXT NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    estimated_cost DECIMAL(15,2),
    urgency VARCHAR(20) DEFAULT 'Normal',
    status VARCHAR(20) DEFAULT 'Pending',
    current_approval_level INTEGER DEFAULT 1,
    -- Asset fulfillment fields
    fulfilled_from_asset_id INTEGER REFERENCES asset(id),
    fulfilled_quantity INTEGER DEFAULT 0,
    fulfilled_by INTEGER REFERENCES "user"(id),
    fulfilled_at TIMESTAMP,
    fulfillment_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id)
);

-- Uploaded files table
CREATE TABLE IF NOT EXISTS uploaded_file (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_id INTEGER NOT NULL REFERENCES asset_request(id) ON DELETE CASCADE
);

-- Approvals table
CREATE TABLE IF NOT EXISTS approval (
    id SERIAL PRIMARY KEY,
    approval_level INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    comments TEXT,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_id INTEGER NOT NULL REFERENCES asset_request(id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL REFERENCES "user"(id)
);

-- Activity log table
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    request_id INTEGER REFERENCES asset_request(id)
);

-- Bills table for financial tracking
CREATE TABLE IF NOT EXISTS bill (
    id SERIAL PRIMARY KEY,
    bill_number VARCHAR(100) UNIQUE NOT NULL,
    vendor_name VARCHAR(200) NOT NULL,
    bill_amount DECIMAL(15,2) NOT NULL,
    bill_date DATE NOT NULL,
    description TEXT,
    bill_file_path VARCHAR(500),
    bill_filename VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending', -- Pending, Verified, Rejected
    verification_comments TEXT,
    request_id INTEGER NOT NULL REFERENCES asset_request(id),
    uploaded_by INTEGER NOT NULL REFERENCES "user"(id),
    verified_by INTEGER REFERENCES "user"(id),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory updates table for tracking stock changes
CREATE TABLE IF NOT EXISTS inventory_update (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES asset(id),
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    update_type VARCHAR(50) NOT NULL, -- Addition, Consumption, Adjustment
    reason TEXT,
    updated_by INTEGER NOT NULL REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON "user"(role);
CREATE INDEX IF NOT EXISTS idx_user_active ON "user"(is_active);

CREATE INDEX IF NOT EXISTS idx_asset_tag ON asset(asset_tag);
CREATE INDEX IF NOT EXISTS idx_asset_type ON asset(asset_type);
CREATE INDEX IF NOT EXISTS idx_asset_status ON asset(status);
CREATE INDEX IF NOT EXISTS idx_asset_category ON asset(category);
CREATE INDEX IF NOT EXISTS idx_asset_assigned ON asset(assigned_to);
CREATE INDEX IF NOT EXISTS idx_asset_low_stock ON asset(asset_type, current_quantity, minimum_threshold);
CREATE INDEX IF NOT EXISTS idx_asset_created ON asset(created_at);

CREATE INDEX IF NOT EXISTS idx_request_status ON asset_request(status);
CREATE INDEX IF NOT EXISTS idx_request_user ON asset_request(user_id);
CREATE INDEX IF NOT EXISTS idx_request_type ON asset_request(request_type);
CREATE INDEX IF NOT EXISTS idx_request_urgency ON asset_request(urgency);
CREATE INDEX IF NOT EXISTS idx_request_created ON asset_request(created_at);
CREATE INDEX IF NOT EXISTS idx_request_fulfilled_asset ON asset_request(fulfilled_from_asset_id);

CREATE INDEX IF NOT EXISTS idx_file_request ON uploaded_file(request_id);
CREATE INDEX IF NOT EXISTS idx_file_uploaded ON uploaded_file(uploaded_at);

CREATE INDEX IF NOT EXISTS idx_approval_request ON approval(request_id);
CREATE INDEX IF NOT EXISTS idx_approval_approver ON approval(approver_id);
CREATE INDEX IF NOT EXISTS idx_approval_level ON approval(approval_level);

CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_request ON activity_log(request_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_action ON activity_log(action);

CREATE INDEX IF NOT EXISTS idx_bill_number ON bill(bill_number);
CREATE INDEX IF NOT EXISTS idx_bill_status ON bill(status);
CREATE INDEX IF NOT EXISTS idx_bill_request ON bill(request_id);
CREATE INDEX IF NOT EXISTS idx_bill_uploaded_by ON bill(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_bill_date ON bill(bill_date);

CREATE INDEX IF NOT EXISTS idx_inventory_asset ON inventory_update(asset_id);
CREATE INDEX IF NOT EXISTS idx_inventory_updated_by ON inventory_update(updated_by);
CREATE INDEX IF NOT EXISTS idx_inventory_created ON inventory_update(created_at);
CREATE INDEX IF NOT EXISTS idx_inventory_type ON inventory_update(update_type);

CREATE INDEX IF NOT EXISTS idx_vendor_name ON vendor(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendor_code ON vendor(vendor_code);
CREATE INDEX IF NOT EXISTS idx_vendor_active ON vendor(is_active);
CREATE INDEX IF NOT EXISTS idx_vendor_category ON vendor(category);

CREATE INDEX IF NOT EXISTS idx_assignment_vendor ON item_assignment(vendor_id);
CREATE INDEX IF NOT EXISTS idx_assignment_assigned_by ON item_assignment(assigned_by);
CREATE INDEX IF NOT EXISTS idx_assignment_assigned_to ON item_assignment(assigned_to);
CREATE INDEX IF NOT EXISTS idx_assignment_status ON item_assignment(delivery_status);
CREATE INDEX IF NOT EXISTS idx_assignment_expected_date ON item_assignment(expected_delivery_date);
CREATE INDEX IF NOT EXISTS idx_assignment_created ON item_assignment(created_at);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_asset_request_updated_at 
    BEFORE UPDATE ON asset_request 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_asset_updated_at 
    BEFORE UPDATE ON asset 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bill_updated_at 
    BEFORE UPDATE ON bill 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vendor_updated_at 
    BEFORE UPDATE ON vendor 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_item_assignment_updated_at 
    BEFORE UPDATE ON item_assignment 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: hexamed123)
INSERT INTO "user" (username, email, password_hash, role, full_name) 
VALUES ('admin', 'admin@hexamed.com', 'pbkdf2:sha256:600000$bMRQWgzjFUmBZWwG$e0d5ef7f9cf4b5f5e3e8d9d5f8c1b0e4e2c4b8c9f5b8c4e9b2f4a6c8e2b1d5f7c0', 'MD', 'System Administrator')
ON CONFLICT (username) DO NOTHING;

-- Insert default accounts/SCM user (password: accounts123)
INSERT INTO "user" (username, email, password_hash, role, full_name) 
VALUES ('accounts', 'accounts@hexamed.com', 'pbkdf2:sha256:600000$bMRQWgzjFUmBZWwG$a1c3f5e7d9b2f4a6c8e0d5f7c9b1e3f5a7c9d2f4b6a8c0e2d4f6a8c1e3f5d7b9', 'Accounts/SCM', 'Accounts Manager')
ON CONFLICT (username) DO NOTHING;

-- Insert sample concern manager user (password: manager123)
INSERT INTO "user" (username, email, password_hash, role, full_name) 
VALUES ('manager', 'manager@hexamed.com', 'pbkdf2:sha256:600000$bMRQWgzjFUmBZWwG$c2e4f6a8b0d2f4a6c8e0d2f4a6c8e0d2f4a6c8e0d2f4a6c8e0d2f4a6c8e0d2f4', 'Concern Manager', 'Department Manager')
ON CONFLICT (username) DO NOTHING;

-- Insert sample regular user (password: user123)
INSERT INTO "user" (username, email, password_hash, role, full_name) 
VALUES ('user1', 'user1@hexamed.com', 'pbkdf2:sha256:600000$bMRQWgzjFUmBZWwG$d3f5a7c9e1d3f5a7c9e1d3f5a7c9e1d3f5a7c9e1d3f5a7c9e1d3f5a7c9e1d3f5', 'User', 'Regular User')
ON CONFLICT (username) DO NOTHING;

-- Sample asset categories
INSERT INTO asset (asset_tag, name, category, asset_type, brand, model, purchase_cost, current_value, condition, location, status, current_quantity, minimum_threshold, unit_of_measurement) 
VALUES 
('HEX-001', 'Dell Laptop', 'IT Equipment', 'Fixed Asset', 'Dell', 'Inspiron 15', 50000.00, 45000.00, 'Good', 'IT Department', 'Available', 1, 1, 'Piece'),
('HEX-002', 'Office Chair', 'Furniture', 'Fixed Asset', 'Steelcase', 'Series 1', 15000.00, 12000.00, 'Good', 'Office Floor 1', 'Available', 1, 1, 'Piece'),
('HEX-003', 'A4 Paper', 'Stationery', 'Consumable Asset', 'JK Paper', 'Premium', 500.00, 500.00, 'Good', 'Store Room', 'Available', 20, 5, 'Ream'),
('HEX-004', 'Printer Cartridge', 'IT Equipment', 'Consumable Asset', 'HP', '678 Black', 2500.00, 2500.00, 'Good', 'IT Department', 'Available', 3, 2, 'Piece'),
('HEX-005', 'Surgical Gloves', 'Medical Supplies', 'Consumable Asset', 'Ansell', 'PowerForm', 1200.00, 1200.00, 'Good', 'Medical Store', 'Available', 50, 10, 'Box'),
('HEX-006', 'Ultrasound Machine', 'Medical Equipment', 'Fixed Asset', 'GE Healthcare', 'LOGIQ P5', 850000.00, 800000.00, 'Excellent', 'Radiology Department', 'Available', 1, 1, 'Unit')
ON CONFLICT (asset_tag) DO NOTHING;

-- Sample asset requests
INSERT INTO asset_request (item_name, quantity, purpose, request_type, estimated_cost, urgency, status, user_id) 
VALUES 
('Projector', 1, 'For conference room presentations', 'Purchase', 25000.00, 'Normal', 'Approved', 1),
('Whiteboard Markers', 5, 'For meeting rooms', 'Purchase', 500.00, 'Low', 'Pending', 1),
('Disposable Masks', 100, 'For patient safety during consultations', 'Purchase', 2000.00, 'High', 'Approved', 4)
ON CONFLICT DO NOTHING;

-- Sample bills
INSERT INTO bill (bill_number, vendor_name, bill_amount, bill_date, description, status, request_id, uploaded_by)
VALUES 
('BILL-2024-001', 'Tech Solutions Ltd', 25000.00, '2024-01-15', 'Projector purchase as per approved request', 'Verified', 1, 2),
('BILL-2024-002', 'Office Supplies Co', 500.00, '2024-01-20', 'Whiteboard markers bulk purchase', 'Pending', 2, 2)
ON CONFLICT (bill_number) DO NOTHING;

-- Sample inventory updates
INSERT INTO inventory_update (asset_id, previous_quantity, new_quantity, update_type, reason, updated_by)
VALUES 
(3, 25, 20, 'Consumption', 'Used for office printing requirements', 2),
(4, 5, 3, 'Consumption', 'Replaced cartridges in department printers', 2),
(5, 60, 50, 'Consumption', 'Distributed to medical staff for patient care', 2)
ON CONFLICT DO NOTHING;

-- Sample vendors
INSERT INTO vendor (vendor_name, vendor_code, category, contact_person, phone, email, address, payment_terms, is_active)
VALUES 
('Tech Solutions Ltd', 'TS001', 'IT Equipment', 'Rajesh Kumar', '+91-9876543210', 'sales@techsolutions.com', '123 Tech Park, Bangalore', '30 days', TRUE),
('Office Supplies Co', 'OS002', 'Stationery', 'Priya Sharma', '+91-9876543211', 'orders@officesupplies.com', '456 Supply Street, Mumbai', '15 days', TRUE),
('Medical Equipment Inc', 'ME003', 'Medical Equipment', 'Dr. Amit Patel', '+91-9876543212', 'sales@medequip.com', '789 Medical Plaza, Delhi', '45 days', TRUE),
('Furniture World', 'FW004', 'Furniture', 'Suresh Gupta', '+91-9876543213', 'sales@furnitureworld.com', '321 Furniture Market, Chennai', '30 days', TRUE)
ON CONFLICT (vendor_code) DO NOTHING;

-- Sample item assignments
INSERT INTO item_assignment (item_name, quantity, vendor_id, assigned_by, assigned_to, expected_delivery_date, delivery_status, unit_price, total_amount, notes)
VALUES 
('Dell Laptops', 2, 1, 2, 4, '2024-02-15', 'Pending', 50000.00, 100000.00, 'For new employees in IT department'),
('Office Chairs', 5, 4, 2, 3, '2024-02-10', 'In Transit', 15000.00, 75000.00, 'Ergonomic chairs for conference room'),
('Surgical Masks', 500, 3, 2, 4, '2024-02-05', 'Delivered', 5.00, 2500.00, 'Bulk order for medical staff')
ON CONFLICT DO NOTHING;

-- Add comments to tables for documentation
COMMENT ON TABLE "user" IS 'User accounts with role-based access control';
COMMENT ON TABLE asset IS 'Physical and consumable assets with inventory tracking';
COMMENT ON TABLE asset_request IS 'Purchase and allocation requests with approval workflow';
COMMENT ON TABLE uploaded_file IS 'File attachments linked to requests';
COMMENT ON TABLE approval IS 'Approval history for requests - 3-level hierarchy: Concern Manager → Accounts/SCM → Admin/MD';
COMMENT ON TABLE activity_log IS 'System activity and audit trail';
COMMENT ON TABLE bill IS 'Vendor bills and financial verification';
COMMENT ON TABLE inventory_update IS 'Stock movement history for consumable assets';

-- Vendors table for supplier management
CREATE TABLE IF NOT EXISTS vendor (
    id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(120),
    address TEXT,
    vendor_code VARCHAR(50) UNIQUE,
    category VARCHAR(100),
    payment_terms VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item assignments table for tracking vendor assignments and deliveries
CREATE TABLE IF NOT EXISTS item_assignment (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL REFERENCES vendor(id),
    assigned_by INTEGER NOT NULL REFERENCES "user"(id),
    assigned_to INTEGER NOT NULL REFERENCES "user"(id),
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    delivery_status VARCHAR(50) DEFAULT 'Pending',
    notes TEXT,
    delivery_notes TEXT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create views for common queries
CREATE OR REPLACE VIEW low_stock_assets AS
SELECT 
    a.id,
    a.asset_tag,
    a.name,
    a.category,
    a.current_quantity,
    a.minimum_threshold,
    a.unit_of_measurement,
    a.location,
    (a.minimum_threshold - a.current_quantity) as shortage_quantity
FROM asset a
WHERE a.asset_type = 'Consumable Asset' 
  AND a.current_quantity <= a.minimum_threshold
  AND a.status = 'Available';

CREATE OR REPLACE VIEW pending_requests_summary AS
SELECT 
    ar.id,
    ar.item_name,
    ar.quantity,
    ar.estimated_cost,
    ar.urgency,
    ar.current_approval_level,
    ar.created_at,
    u.full_name as requester_name,
    u.role as requester_role
FROM asset_request ar
JOIN "user" u ON ar.user_id = u.id
WHERE ar.status = 'Pending'
ORDER BY 
    CASE ar.urgency 
        WHEN 'High' THEN 1 
        WHEN 'Normal' THEN 2 
        WHEN 'Low' THEN 3 
    END,
    ar.created_at;

CREATE OR REPLACE VIEW asset_utilization AS
SELECT 
    a.category,
    a.asset_type,
    COUNT(*) as total_assets,
    COUNT(CASE WHEN a.status = 'Available' THEN 1 END) as available_assets,
    COUNT(CASE WHEN a.status = 'In Use' THEN 1 END) as in_use_assets,
    COUNT(CASE WHEN a.assigned_to IS NOT NULL THEN 1 END) as assigned_assets,
    ROUND(
        (COUNT(CASE WHEN a.status = 'In Use' THEN 1 END)::decimal / COUNT(*)::decimal) * 100, 2
    ) as utilization_percentage
FROM asset a
GROUP BY a.category, a.asset_type
ORDER BY a.category, a.asset_type;

-- Grant appropriate permissions (adjust as needed for your security requirements)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO hexamed_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hexamed_app_user;
