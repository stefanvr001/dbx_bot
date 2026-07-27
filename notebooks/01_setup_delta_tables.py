# Databricks Notebook: 01_setup_delta_tables
# COMMAND ----------
# MAGIC %md
# MAGIC # Customer Service Agent - Databricks Delta Lake & UC Functions Setup
# MAGIC 
# MAGIC This notebook sets up Delta Lake tables in Unity Catalog for storing policyholder data,
# MAGIC debit order schedules, vehicle financial interest, and registers AI Functions.

# COMMAND ----------
import sys
import os

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS main;
# MAGIC CREATE SCHEMA IF NOT EXISTS main.insurance_customer_service;
# MAGIC USE CATALOG main;
# MAGIC USE SCHEMA insurance_customer_service;

# COMMAND ----------
# MAGIC %sql
# MAGIC -- 1. Policy Master Delta Table
# MAGIC CREATE TABLE IF NOT EXISTS policies (
# MAGIC   policy_number STRING NOT NULL,
# MAGIC   customer_id STRING,
# MAGIC   product_type STRING,
# MAGIC   status STRING,
# MAGIC   start_date DATE,
# MAGIC   premium_amount DOUBLE,
# MAGIC   currency STRING,
# MAGIC   excess_amount DOUBLE,
# MAGIC   cover_details STRING
# MAGIC ) USING DELTA;

# COMMAND ----------
# MAGIC %sql
# MAGIC -- 2. Debit Order Schedule Delta Table
# MAGIC CREATE TABLE IF NOT EXISTS debit_orders (
# MAGIC   policy_number STRING NOT NULL,
# MAGIC   account_holder STRING,
# MAGIC   bank_name STRING,
# MAGIC   account_number_masked STRING,
# MAGIC   branch_code STRING,
# MAGIC   debit_day INT,
# MAGIC   debit_amount DOUBLE,
# MAGIC   last_successful_debit_date DATE,
# MAGIC   last_debit_status STRING,
# MAGIC   next_debit_date DATE,
# MAGIC   payment_frequency STRING
# MAGIC ) USING DELTA;

# COMMAND ----------
# MAGIC %sql
# MAGIC -- 3. Vehicle Financier Interest Delta Table
# MAGIC CREATE TABLE IF NOT EXISTS vehicle_noted_interest (
# MAGIC   policy_number STRING NOT NULL,
# MAGIC   make STRING,
# MAGIC   model STRING,
# MAGIC   year INT,
# MAGIC   registration_number STRING,
# MAGIC   vin STRING,
# MAGIC   financial_institution STRING,
# MAGIC   noted_interest_status STRING
# MAGIC ) USING DELTA;

# COMMAND ----------
print("✅ Unity Catalog Delta Lake tables successfully initialized!")
