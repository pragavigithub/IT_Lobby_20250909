#!/usr/bin/env python3
"""
MySQL Migration Auto-Updater for WMS Application
This script automatically updates the MySQL migration file with any new database schema changes.
"""

import os
import re
import sys
from datetime import datetime
import ast
import importlib.util

def extract_model_info():
    """Extract all SQLAlchemy model information from the codebase"""
    models = {}
    
    # Files to scan for models
    model_files = ['models.py', 'models_extensions.py']
    
    # Also check modules directory
    modules_dir = 'modules'
    if os.path.exists(modules_dir):
        for root, dirs, files in os.walk(modules_dir):
            for file in files:
                if file == 'models.py':
                    model_files.append(os.path.join(root, file))
    
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"Scanning {file_path} for models...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract model classes using regex
                model_pattern = r'class\s+(\w+)\([^)]*db\.Model[^)]*\):\s*\n(?:\s*"""[^"]*"""\s*\n)?(\s*__tablename__\s*=\s*[\'"]([^\'"]+)[\'"])?'
                matches = re.finditer(model_pattern, content, re.MULTILINE)
                
                for match in matches:
                    model_name = match.group(1)
                    table_name = match.group(3) if match.group(3) else model_name.lower()
                    
                    # Extract column information
                    class_start = match.end()
                    # Find the end of the class (next class or end of file)
                    next_class = re.search(r'\nclass\s+\w+', content[class_start:])
                    class_end = class_start + next_class.start() if next_class else len(content)
                    
                    class_content = content[class_start:class_end]
                    
                    # Extract columns
                    column_pattern = r'(\w+)\s*=\s*db\.Column\(([^)]+(?:\([^)]*\))*[^)]*)\)'
                    columns = []
                    
                    for col_match in re.finditer(column_pattern, class_content):
                        col_name = col_match.group(1)
                        col_definition = col_match.group(2)
                        columns.append({
                            'name': col_name,
                            'definition': col_definition.strip()
                        })
                    
                    models[model_name] = {
                        'table_name': table_name,
                        'file': file_path,
                        'columns': columns
                    }
                    
                    print(f"  Found model: {model_name} -> {table_name} ({len(columns)} columns)")
                    
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                continue
    
    return models

def generate_mysql_schema(models):
    """Generate MySQL CREATE TABLE statements from model information"""
    schema_sql = []
    
    # SQL type mapping from SQLAlchemy to MySQL
    type_mapping = {
        'db.Integer': 'INT',
        'db.String': 'VARCHAR',
        'db.Text': 'TEXT',
        'db.Boolean': 'BOOLEAN',
        'db.DateTime': 'DATETIME',
        'db.Date': 'DATE',
        'db.Time': 'TIME',
        'db.Float': 'FLOAT',
        'db.Numeric': 'DECIMAL',
        'db.LargeBinary': 'LONGBLOB',
        'db.JSON': 'JSON'
    }
    
    for model_name, model_info in models.items():
        table_name = model_info['table_name']
        columns = model_info['columns']
        
        create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
        column_definitions = []
        
        for col in columns:
            col_name = col['name']
            col_def = col['definition']
            
            # Parse column definition
            mysql_type = 'VARCHAR(255)'  # Default
            constraints = []
            
            # Extract type
            for sqla_type, mysql_type_mapped in type_mapping.items():
                if sqla_type in col_def:
                    if 'String' in sqla_type and '(' in col_def:
                        # Extract string length
                        length_match = re.search(r'String\((\d+)\)', col_def)
                        if length_match:
                            mysql_type = f"VARCHAR({length_match.group(1)})"
                        else:
                            mysql_type = "VARCHAR(255)"
                    else:
                        mysql_type = mysql_type_mapped
                    break
            
            # Check for constraints
            if 'primary_key=True' in col_def:
                constraints.append('PRIMARY KEY')
                if mysql_type == 'INT':
                    constraints.append('AUTO_INCREMENT')
            
            if 'nullable=False' in col_def and 'primary_key=True' not in col_def:
                constraints.append('NOT NULL')
            
            if 'unique=True' in col_def:
                constraints.append('UNIQUE')
                
            if 'default=' in col_def:
                # Extract default value
                default_match = re.search(r"default=([^,)]+)", col_def)
                if default_match:
                    default_val = default_match.group(1).strip()
                    if default_val == 'datetime.utcnow':
                        constraints.append('DEFAULT CURRENT_TIMESTAMP')
                    elif default_val == 'True':
                        constraints.append('DEFAULT TRUE')
                    elif default_val == 'False':
                        constraints.append('DEFAULT FALSE')
                    elif default_val.startswith("'") and default_val.endswith("'"):
                        constraints.append(f'DEFAULT {default_val}')
            
            # Build column definition
            col_sql = f"  `{col_name}` {mysql_type}"
            if constraints:
                col_sql += f" {' '.join(constraints)}"
            
            column_definitions.append(col_sql)
        
        create_sql += ',\n'.join(column_definitions)
        create_sql += f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n"
        
        schema_sql.append(f"-- Table: {table_name} (Model: {model_name})")
        schema_sql.append(create_sql)
        schema_sql.append("")
    
    return '\n'.join(schema_sql)

def update_migration_file():
    """Update the MySQL migration file with current schema"""
    print("🔄 Updating MySQL Migration File...")
    
    # Extract current models
    models = extract_model_info()
    
    if not models:
        print("❌ No models found!")
        return
    
    print(f"✅ Found {len(models)} models")
    
    # Generate schema SQL
    schema_sql = generate_mysql_schema(models)
    
    # Read current migration file
    migration_file = 'mysql_migration_consolidated_final.py'
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file {migration_file} not found!")
        return
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the schema section
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create backup
    backup_file = f"{migration_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    # Update the migration file header comment
    updated_content = re.sub(
        r'(""".*?✅ Comprehensive indexing for optimal performance\n)(.*?)(\n✅ PostgreSQL compatibility for Replit environment)',
        rf'\1✅ Schema auto-updated on {timestamp}\2\3',
        content,
        flags=re.DOTALL
    )
    
    # Add a comment about the last update
    comment_to_add = f"""
# =============================================================================
# SCHEMA AUTO-UPDATE SECTION - Last Updated: {timestamp}
# =============================================================================
# This section contains the latest database schema extracted from models
# Models found: {', '.join(models.keys())}
# Total tables: {len(models)}
#
# Generated Schema SQL:
# {schema_sql.replace(chr(10), chr(10) + '# ')}
# =============================================================================
"""
    
    # Find a good place to insert the comment (after imports)
    import_end = re.search(r'(from datetime import datetime\n)', updated_content)
    if import_end:
        insert_pos = import_end.end()
        updated_content = (updated_content[:insert_pos] + 
                         comment_to_add + 
                         updated_content[insert_pos:])
    
    # Write updated file
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Migration file updated successfully!")
    print(f"✅ Models included: {', '.join(models.keys())}")
    
    # Also write a standalone schema file
    schema_file = f"current_schema_mysql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(f"-- WMS Database Schema - Generated on {timestamp}\n")
        f.write(f"-- Models: {', '.join(models.keys())}\n\n")
        f.write(schema_sql)
    
    print(f"✅ Schema file created: {schema_file}")

if __name__ == "__main__":
    print("🚀 WMS MySQL Migration Updater")
    print("=" * 50)
    
    update_migration_file()
    
    print("\n✅ Update completed!")
    print("📝 Note: Review the changes before running the migration")
    print("🔄 Run: python mysql_migration_consolidated_final.py")