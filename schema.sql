SCHEMA_SQL = """
-- ============================================================================
-- Database Generalization Schema
-- ============================================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS Employee CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;
DROP TABLE IF EXISTS Person CASCADE;

-- ============================================================================
-- PERSON TABLE (Supertype)
-- ============================================================================

CREATE TABLE Person (
    PersonID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    Phone VARCHAR(20),
    Email VARCHAR(100) UNIQUE NOT NULL,
    PersonType VARCHAR(20) NOT NULL CHECK (PersonType IN ('Customer', 'Employee', 'Both')),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_email_format CHECK (Email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$')
);

-- ============================================================================
-- CUSTOMER TABLE (Subtype)
-- ============================================================================

CREATE TABLE Customer (
    CustomerID SERIAL PRIMARY KEY,
    PersonID INT NOT NULL UNIQUE,
    LoyaltyPoints INT DEFAULT 0 CHECK (LoyaltyPoints >= 0),
    RegistrationDate DATE DEFAULT CURRENT_DATE,
    CustomerTier VARCHAR(20) DEFAULT 'Bronze' CHECK (CustomerTier IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
    CONSTRAINT fk_customer_person FOREIGN KEY (PersonID)
        REFERENCES Person(PersonID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================================
-- EMPLOYEE TABLE (Subtype)
-- ============================================================================

CREATE TABLE Employee (
    EmployeeID SERIAL PRIMARY KEY,
    PersonID INT NOT NULL UNIQUE,
    Salary DECIMAL(10, 2) CHECK (Salary > 0),
    Department VARCHAR(50) NOT NULL,
    HireDate DATE DEFAULT CURRENT_DATE,
    Position VARCHAR(100),
    ManagerID INT,
    CONSTRAINT fk_employee_person FOREIGN KEY (PersonID)
        REFERENCES Person(PersonID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_employee_manager FOREIGN KEY (ManagerID)
        REFERENCES Employee(EmployeeID)
        ON DELETE SET NULL,
    CONSTRAINT chk_hire_date CHECK (HireDate <= CURRENT_DATE)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Person table indexes
CREATE INDEX idx_person_email ON Person(Email);
CREATE INDEX idx_person_type ON Person(PersonType);
CREATE INDEX idx_person_name ON Person(Name);
CREATE INDEX idx_person_name_type ON Person(Name, PersonType);

-- Customer table indexes
CREATE INDEX idx_customer_loyalty ON Customer(LoyaltyPoints DESC);
CREATE INDEX idx_customer_person_id ON Customer(PersonID);

-- Employee table indexes
CREATE INDEX idx_employee_department ON Employee(Department);
CREATE INDEX idx_employee_salary ON Employee(Salary);
CREATE INDEX idx_employee_person_id ON Employee(PersonID);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.LastModified = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_person_update
BEFORE UPDATE ON Person
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Complete customer view
CREATE VIEW v_customer_complete AS
SELECT 
    c.CustomerID, p.PersonID, p.Name, p.Address, p.Phone, p.Email,
    c.LoyaltyPoints, c.CustomerTier, c.RegistrationDate,
    p.CreatedDate, p.LastModified
FROM Person p
INNER JOIN Customer c ON p.PersonID = c.PersonID;

-- Complete employee view
CREATE VIEW v_employee_complete AS
SELECT 
    e.EmployeeID, p.PersonID, p.Name, p.Address, p.Phone, p.Email,
    e.Salary, e.Department, e.Position, e.HireDate,
    m.Name AS ManagerName
FROM Person p
INNER JOIN Employee e ON p.PersonID = e.PersonID
LEFT JOIN Employee me ON e.ManagerID = me.EmployeeID
LEFT JOIN Person m ON me.PersonID = m.PersonID;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample persons
INSERT INTO Person (Name, Address, Phone, Email, PersonType) VALUES
('John Smith', '123 Main St, New York, NY', '555-0101', 'john.smith@email.com', 'Customer'),
('Emily Johnson', '456 Oak Ave, Los Angeles, CA', '555-0102', 'emily.johnson@email.com', 'Employee'),
('Michael Brown', '789 Pine Rd, Chicago, IL', '555-0103', 'michael.brown@email.com', 'Both'),
('Sarah Davis', '321 Elm St, Houston, TX', '555-0104', 'sarah.davis@email.com', 'Customer'),
('David Wilson', '654 Maple Dr, Phoenix, AZ', '555-0105', 'david.wilson@email.com', 'Employee'),
('Jennifer Martinez', '987 Cedar Ln, Philadelphia, PA', '555-0106', 'jennifer.martinez@email.com', 'Customer'),
('Robert Anderson', '147 Birch Ct, San Antonio, TX', '555-0107', 'robert.anderson@email.com', 'Employee'),
('Lisa Taylor', '258 Spruce Way, San Diego, CA', '555-0108', 'lisa.taylor@email.com', 'Both'),
('James Thomas', '369 Willow Pl, Dallas, TX', '555-0109', 'james.thomas@email.com', 'Customer'),
('Mary Garcia', '741 Ash Blvd, San Jose, CA', '555-0110', 'mary.garcia@email.com', 'Employee');

-- Insert customers
INSERT INTO Customer (PersonID, LoyaltyPoints, CustomerTier) VALUES
(1, 1500, 'Gold'),
(3, 2500, 'Platinum'),
(4, 800, 'Silver'),
(6, 450, 'Bronze'),
(8, 3200, 'Platinum'),
(9, 1200, 'Gold');

-- Insert employees
INSERT INTO Employee (PersonID, Salary, Department, Position) VALUES
(2, 75000.00, 'Engineering', 'Software Developer'),
(3, 95000.00, 'Sales', 'Sales Manager'),
(5, 68000.00, 'Engineering', 'QA Engineer'),
(7, 82000.00, 'Marketing', 'Marketing Specialist'),
(8, 110000.00, 'Engineering', 'Senior Developer'),
(10, 72000.00, 'HR', 'HR Coordinator');
"""
