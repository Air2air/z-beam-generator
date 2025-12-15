#!/usr/bin/env python3
"""
Database Comparison Tool
Compares schemas and data between z-beam.db and data/winston_feedback.db
"""

import sqlite3
import os
from collections import defaultdict

def get_schema_info(db_path):
    """Extract schema information from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        # Get column info
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]
        
        schema[table] = {
            'columns': [(col[1], col[2]) for col in columns],  # (name, type)
            'row_count': row_count
        }
    
    conn.close()
    return schema, tables

def compare_databases(db1_path, db2_path):
    """Compare two databases"""
    print("=" * 80)
    print("DATABASE COMPARISON")
    print("=" * 80)
    print()
    
    # Get file sizes
    size1 = os.path.getsize(db1_path) / 1024
    size2 = os.path.getsize(db2_path) / 1024
    
    print(f"📊 {db1_path}")
    print(f"   Size: {size1:.1f} KB")
    print()
    print(f"📊 {db2_path}")
    print(f"   Size: {size2:.1f} KB")
    print()
    
    # Get schemas
    schema1, tables1 = get_schema_info(db1_path)
    schema2, tables2 = get_schema_info(db2_path)
    
    # Compare tables
    print("TABLE COMPARISON")
    print("-" * 80)
    
    tables1_set = set(tables1)
    tables2_set = set(tables2)
    
    only_in_1 = tables1_set - tables2_set
    only_in_2 = tables2_set - tables1_set
    shared = tables1_set & tables2_set
    
    print(f"Tables only in {db1_path}: {len(only_in_1)}")
    if only_in_1:
        for table in only_in_1:
            print(f"  - {table} ({schema1[table]['row_count']} rows)")
    
    print()
    print(f"Tables only in {db2_path}: {len(only_in_2)}")
    if only_in_2:
        for table in only_in_2:
            print(f"  - {table} ({schema2[table]['row_count']} rows)")
    
    print()
    print(f"Shared tables: {len(shared)}")
    print()
    
    # Compare shared tables
    print("SHARED TABLE DETAILS")
    print("-" * 80)
    
    total_rows_1 = 0
    total_rows_2 = 0
    schema_matches = 0
    
    for table in sorted(shared):
        rows1 = schema1[table]['row_count']
        rows2 = schema2[table]['row_count']
        cols1 = schema1[table]['columns']
        cols2 = schema2[table]['columns']
        
        total_rows_1 += rows1
        total_rows_2 += rows2
        
        schema_match = cols1 == cols2
        if schema_match:
            schema_matches += 1
        
        status = "✅" if schema_match else "⚠️"
        print(f"{status} {table}")
        print(f"   Rows: {rows1} vs {rows2} ({'=' if rows1 == rows2 else '≠'})")
        print(f"   Columns: {len(cols1)} vs {len(cols2)} ({'=' if len(cols1) == len(cols2) else '≠'})")
        
        if not schema_match:
            print(f"   Schema differs!")
            only_in_1 = set(cols1) - set(cols2)
            only_in_2 = set(cols2) - set(cols1)
            if only_in_1:
                print(f"   Only in {db1_path}: {only_in_1}")
            if only_in_2:
                print(f"   Only in {db2_path}: {only_in_2}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Schema matches: {schema_matches}/{len(shared)} tables ({schema_matches/len(shared)*100:.0f}%)")
    print(f"Total rows: {total_rows_1} vs {total_rows_2}")
    print()
    
    # Recommendation
    if schema_matches == len(shared) and only_in_1 == set() and only_in_2 == set():
        print("✅ DATABASES HAVE IDENTICAL SCHEMAS")
        print()
        if total_rows_2 >= total_rows_1:
            print(f"💡 RECOMMENDATION: Keep {db2_path} ({total_rows_2} rows)")
            print(f"   Delete {db1_path} ({total_rows_1} rows)")
            print(f"   Savings: {size1:.1f} KB")
        else:
            print(f"💡 RECOMMENDATION: Keep {db1_path} ({total_rows_1} rows)")
            print(f"   Delete {db2_path} ({total_rows_2} rows)")
            print(f"   Savings: {size2:.1f} KB")
    else:
        print("⚠️  DATABASES HAVE DIVERGED")
        print()
        print("💡 RECOMMENDATION: Investigate which is primary/active")
        print("   - Check git history for recent updates")
        print("   - Review code to see which is actively written to")
        print("   - Consider consolidating data if both are needed")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    db1 = "z-beam.db"
    db2 = "data/winston_feedback.db"
    
    if not os.path.exists(db1):
        print(f"❌ {db1} not found")
        exit(1)
    
    if not os.path.exists(db2):
        print(f"❌ {db2} not found")
        exit(1)
    
    compare_databases(db1, db2)
