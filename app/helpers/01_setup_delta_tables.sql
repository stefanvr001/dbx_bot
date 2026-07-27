CREATE SCHEMA IF NOT EXISTS classic_demo.insurance_customer_service;

CREATE TABLE IF NOT EXISTS classic_demo.insurance_customer_service.policies (
  policy_number STRING NOT NULL,
  customer_id STRING,
  product_type STRING,
  status STRING,
  start_date DATE,
  premium_amount DOUBLE,
  currency STRING,
  excess_amount DOUBLE,
  cover_details STRING
) USING DELTA;


CREATE TABLE IF NOT EXISTS classic_demo.insurance_customer_service.debit_orders (
  policy_number STRING NOT NULL,
  account_holder STRING,
  bank_name STRING,
  account_number_masked STRING,
  branch_code STRING,
  debit_day INT,
  debit_amount DOUBLE,
  last_successful_debit_date DATE,
  last_debit_status STRING,
  next_debit_date DATE,
  payment_frequency STRING
) USING DELTA;


CREATE TABLE IF NOT EXISTS classic_demo.insurance_customer_service.vehicle_noted_interest (
  policy_number STRING NOT NULL,
  make STRING,
  model STRING,
  year INT,
  registration_number STRING,
  vin STRING,
  financial_institution STRING,
  noted_interest_status STRING
) USING DELTA;


CREATE TABLE IF NOT EXISTS classic_demo.insurance_customer_service.customer_identifiers (
  policy_number STRING NOT NULL,
  identifier STRING NOT NULL,
  identifier_type STRING NOT NULL
) USING DELTA;

-- =====================================================
-- POLICIES
-- =====================================================

INSERT INTO classic_demo.insurance_customer_service.policies VALUES
('POL100001','CUST1001','Motor Comprehensive','Active','2024-01-15',1250.00,'ZAR',5000.00,'Comprehensive cover including theft, hail and third-party liability'),
('POL100002','CUST1002','Homeowners','Active','2023-11-01',980.50,'ZAR',2500.00,'Building cover up to ZAR 2,500,000'),
('POL100003','CUST1003','Household Contents','Active','2022-07-10',450.25,'ZAR',1500.00,'Household contents insured up to ZAR 750,000'),
('POL100004','CUST1001','Vehicle Third Party','Cancelled','2021-05-18',320.00,'ZAR',0.00,'Third-party only cover'),
('POL100005','CUST1004','Motor Comprehensive','Lapsed','2023-02-14',1460.75,'ZAR',3500.00,'Comprehensive vehicle insurance'),
('POL100006','CUST1005','Life Cover','Active','2020-10-01',780.00,'ZAR',0.00,'Life cover of ZAR 1,500,000'),
('POL100007','CUST1006','Funeral Plan','Active','2024-03-20',185.00,'ZAR',0.00,'Family funeral plan'),
('POL100008','CUST1007','Motor Comprehensive','Active','2024-06-12',1650.00,'ZAR',4000.00,'Luxury vehicle comprehensive insurance'),
('POL100009','CUST1008','Homeowners','Pending','2025-01-01',1150.00,'ZAR',3000.00,'Awaiting inspection'),
('POL100010','CUST1009','Travel Insurance','Expired','2023-09-05',120.00,'ZAR',500.00,'International travel cover');

-- =====================================================
-- DEBIT ORDERS
-- =====================================================

INSERT INTO classic_demo.insurance_customer_service.debit_orders VALUES
('POL100001','John Smith','Standard Bank','****5678','051001',25,1250.00,'2025-07-25','Successful','2025-08-25','Monthly'),
('POL100002','Mary Johnson','FNB','****1234','250655',1,980.50,'2025-07-01','Successful','2025-08-01','Monthly'),
('POL100003','Peter Williams','Nedbank','****9876','198765',15,450.25,'2025-07-15','Successful','2025-08-15','Monthly'),
('POL100004','John Smith','Standard Bank','****5678','051001',25,320.00,'2024-10-25','Cancelled',NULL,'Monthly'),
('POL100005','Sarah Brown','Capitec','****4421','470010',5,1460.75,'2025-03-05','Failed','2025-08-05','Monthly'),
('POL100006','David Wilson','ABSA','****7744','632005',28,780.00,'2025-07-28','Successful','2025-08-28','Monthly'),
('POL100007','Lisa Adams','TymeBank','****2299','678910',10,185.00,'2025-07-10','Successful','2025-08-10','Monthly'),
('POL100008','Michael Green','Investec','****8899','580105',20,1650.00,'2025-07-20','Successful','2025-08-20','Monthly'),
('POL100009','Emma White','FNB','****6633','250655',3,1150.00,NULL,'Pending','2025-08-03','Monthly'),
('POL100010','Daniel Black','Standard Bank','****1188','051001',18,120.00,'2024-09-18','Completed',NULL,'Once-off');

-- =====================================================
-- VEHICLE NOTED INTEREST
-- =====================================================

INSERT INTO classic_demo.insurance_customer_service.vehicle_noted_interest VALUES
('POL100001','Toyota','Hilux',2023,'KDR123GP','JT123456789012345','WesBank','Active'),
('POL100004','Volkswagen','Polo',2019,'HGF456GP','VW987654321098765','MFC','Released'),
('POL100005','Ford','Ranger',2022,'LMP987GP','FR123450987654321','Toyota Financial Services','Active'),
('POL100008','BMW','X5',2024,'BMW555GP','WBAX5123456789012','BMW Financial Services','Active');


-- =====================================================
-- IDENTIFIERS
-- =====================================================

INSERT INTO classic_demo.insurance_customer_service.customer_identifiers VALUES

-- POL100001
('POL100001','john.smith@email.com','EMAIL'),
('POL100001','0821234567','PHONE'),
('POL100001','8001015009087','ID'),

-- POL100002
('POL100002','mary.johnson@email.com','EMAIL'),
('POL100002','0832345678','PHONE'),
('POL100002','8205056009088','ID'),

-- POL100003
('POL100003','peter.williams@email.com','EMAIL'),
('POL100003','0843456789','PHONE'),
('POL100003','7902125009089','ID'),

-- POL100004 (same customer as POL100001)
('POL100004','john.smith@email.com','EMAIL'),
('POL100004','0821234567','PHONE'),
('POL100004','8001015009087','ID'),

-- POL100005
('POL100005','sarah.brown@email.com','EMAIL'),
('POL100005','0814567890','PHONE'),
('POL100005','8509205009090','ID'),

-- POL100006
('POL100006','david.wilson@email.com','EMAIL'),
('POL100006','0795678901','PHONE'),
('POL100006','7703155009091','ID'),

-- POL100007
('POL100007','lisa.adams@email.com','EMAIL'),
('POL100007','0766789012','PHONE'),
('POL100007','9008115009092','ID'),

-- POL100008
('POL100008','michael.green@email.com','EMAIL'),
('POL100008','0727890123','PHONE'),
('POL100008','8806245009093','ID'),

-- POL100009
('POL100009','emma.white@email.com','EMAIL'),
('POL100009','0718901234','PHONE'),
('POL100009','9501035009094','ID'),

-- POL100010
('POL100010','daniel.black@email.com','EMAIL'),
('POL100010','0789012345','PHONE'),
('POL100010','8104305009095','ID');