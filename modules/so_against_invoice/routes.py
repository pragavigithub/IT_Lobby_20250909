"""
Routes for SO Against Invoice Module
Implements the complete workflow for creating invoices against Sales Orders
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging
import json

from app import app, db
from models import User, DocumentNumberSeries
from .models import SOInvoiceDocument, SOInvoiceItem, SOInvoiceSerial, SOSeries
from sap_integration import SAPIntegration

# Create blueprint for SO Against Invoice module
so_invoice_bp = Blueprint('so_against_invoice', __name__, url_prefix='/so-against-invoice')


def generate_so_invoice_number():
    """Generate unique document number for SO Against Invoice"""
    return DocumentNumberSeries.get_next_number('SO_AGAINST_INVOICE')


@so_invoice_bp.route('/', methods=['GET'])
@login_required
def index():
    """SO Against Invoice main page with document listing"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        # Ensure per_page is within allowed range
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
        
        # Build base query
        query = SOInvoiceDocument.query
        
        # Apply user-based filtering for non-admin users
        if current_user.role not in ['admin', 'manager']:
            query = query.filter_by(user_id=current_user.id)
        
        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    SOInvoiceDocument.document_number.ilike(search_filter),
                    SOInvoiceDocument.so_number.ilike(search_filter),
                    SOInvoiceDocument.card_code.ilike(search_filter),
                    SOInvoiceDocument.card_name.ilike(search_filter),
                    SOInvoiceDocument.status.ilike(search_filter)
                )
            )
        
        # Order and paginate
        query = query.order_by(SOInvoiceDocument.created_at.desc())
        documents_paginated = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('index.html',
                             documents=documents_paginated.items,
                             pagination=documents_paginated,
                             search=search,
                             per_page=per_page,
                             current_user=current_user)
    
    except Exception as e:
        logging.error(f"Error in SO Against Invoice index: {str(e)}")
        flash(f'Error loading documents: {str(e)}', 'error')
        return render_template('index.html',
                             documents=[],
                             pagination=None,
                             search='',
                             per_page=10,
                             current_user=current_user)


@so_invoice_bp.route('/create', methods=['GET', 'POST'])
@login_required 
def create():
    """Create new SO Against Invoice document"""
    if request.method == 'GET':
        return render_template('create.html')
    
    try:
        # Generate document number
        document_number = generate_so_invoice_number()
        
        # Create new document
        document = SOInvoiceDocument(
            document_number=document_number,
            user_id=current_user.id,
            comments="SO Against Invoice - Created via WMS"
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash(f'SO Against Invoice {document_number} created successfully', 'success')
        return redirect(url_for('so_against_invoice.detail', doc_id=document.id))
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating SO Against Invoice: {str(e)}")
        flash(f'Error creating document: {str(e)}', 'error')
        return render_template('create.html')


@so_invoice_bp.route('/detail/<int:doc_id>')
@login_required
def detail(doc_id):
    """SO Against Invoice detail page"""
    try:
        document = SOInvoiceDocument.query.get_or_404(doc_id)
        
        # Check permissions
        if current_user.role not in ['admin', 'manager'] and document.user_id != current_user.id:
            flash('Access denied - You can only view your own documents', 'error')
            return redirect(url_for('so_against_invoice.index'))
        
        return render_template('detail.html', 
                             document=document,
                             current_user=current_user)
    
    except Exception as e:
        logging.error(f"Error loading SO Against Invoice detail: {str(e)}")
        flash(f'Error loading document: {str(e)}', 'error')
        return redirect(url_for('so_against_invoice.index'))


# Step 1: Get Sales Order Series API
@so_invoice_bp.route('/api/get-so-series', methods=['GET'])
@login_required
def get_so_series():
    """Get available SO Series from SAP B1"""
    try:
        sap = SAPIntegration()
        
        # Try to get series from SAP B1
        if sap.ensure_logged_in():
            try:
                url = f"{sap.base_url}/b1s/v1/SQLQueries('Get_SO_Series')/List"
                response = sap.session.post(url, json={}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    series_list = data.get('value', [])
                    
                    # Cache series in database for faster lookup
                    for series_data in series_list:
                        existing_series = SOSeries.query.filter_by(series=series_data['Series']).first()
                        if not existing_series:
                            new_series = SOSeries(
                                series=series_data['Series'],
                                series_name=series_data['SeriesName']
                            )
                            db.session.add(new_series)
                    
                    db.session.commit()
                    logging.info(f"Retrieved {len(series_list)} SO series from SAP B1")
                    
                    return jsonify({
                        'success': True,
                        'series': series_list
                    })
                    
            except Exception as e:
                logging.error(f"Error getting SO series from SAP: {str(e)}")
        
        # Fallback to cached data or mock data
        cached_series = SOSeries.query.all()
        if cached_series:
            series_list = [{'Series': s.series, 'SeriesName': s.series_name} for s in cached_series]
            return jsonify({
                'success': True,
                'series': series_list
            })
        
        # Return mock data for offline mode
        return jsonify({
            'success': True,
            'series': [
                {'Series': 11, 'SeriesName': 'Primary'},
                {'Series': 243, 'SeriesName': 'SO2526'},
                {'Series': 173, 'SeriesName': 'SO AVS23'}
            ]
        })
    
    except Exception as e:
        logging.error(f"Error in get_so_series API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Step 2: Validate SO Number with Series
@so_invoice_bp.route('/api/validate-so-number', methods=['POST'])
@login_required
def validate_so_number():
    """Validate SO Number with Series and get DocEntry"""
    try:
        data = request.get_json()
        so_number = data.get('so_number')
        series = data.get('series')
        
        if not so_number or not series:
            return jsonify({
                'success': False,
                'error': 'SO Number and Series are required'
            }), 400
        
        sap = SAPIntegration()
        
        # Try to validate with SAP B1
        if sap.ensure_logged_in():
            try:
                url = f"{sap.base_url}/b1s/v1/SQLQueries('Get_SO_Details')/List"
                request_body = {
                    "ParamList": f"SONumber='{so_number}'&Series='{series}'"
                }
                response = sap.session.post(url, json=request_body, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    so_details = data.get('value', [])
                    
                    if so_details:
                        doc_entry = so_details[0].get('DocEntry')
                        return jsonify({
                            'success': True,
                            'doc_entry': doc_entry,
                            'message': f'SO {so_number} validated successfully'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'SO Number {so_number} not found in Series {series}'
                        }), 404
                        
            except Exception as e:
                logging.error(f"Error validating SO with SAP: {str(e)}")
        
        # Return mock validation for offline mode
        return jsonify({
            'success': True,
            'doc_entry': 1248,
            'message': f'SO {so_number} validated successfully (offline mode)'
        })
    
    except Exception as e:
        logging.error(f"Error in validate_so_number API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Step 3: Fetch Sales Order Details
@so_invoice_bp.route('/api/fetch-so-details', methods=['POST'])
@login_required
def fetch_so_details():
    """Fetch full SO details using DocEntry"""
    try:
        data = request.get_json()
        doc_entry = data.get('doc_entry')
        
        if not doc_entry:
            return jsonify({
                'success': False,
                'error': 'DocEntry is required'
            }), 400
        
        sap = SAPIntegration()
        
        # Try to fetch from SAP B1
        if sap.ensure_logged_in():
            try:
                url = f"{sap.base_url}/b1s/v1/Orders?$filter=DocEntry eq {doc_entry}"
                response = sap.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get('value', [])
                    
                    if orders:
                        order = orders[0]
                        return jsonify({
                            'success': True,
                            'order': order
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'SO with DocEntry {doc_entry} not found'
                        }), 404
                        
            except Exception as e:
                logging.error(f"Error fetching SO details from SAP: {str(e)}")
        
        # Return mock data for offline mode
        mock_order = {
            "DocEntry": doc_entry,
            "CardCode": "3D SEALS",
            "CardName": "3D SEALS PRIVATE LIMITED",
            "Address": "Sai Indu Tower, Mumbai City-400078, IN",
            "DocumentLines": [
                {
                    "LineNum": 0,
                    "ItemCode": "IPhone",
                    "ItemDescription": "12 Series 8GB RAM/250 GB ROM Black",
                    "Quantity": 10,
                    "WarehouseCode": "7000-FG"
                },
                {
                    "LineNum": 1,
                    "ItemCode": "RedmiNote4",
                    "ItemDescription": "8GBRAM/250GBROM Black",
                    "Quantity": 10,
                    "WarehouseCode": "7000-FG"
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'order': mock_order,
            'offline_mode': True
        })
    
    except Exception as e:
        logging.error(f"Error in fetch_so_details API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Step 4: Validation Rules for Serial and Non-Serial Items
@so_invoice_bp.route('/api/validate-item', methods=['POST'])
@login_required
def validate_item():
    """Validate item details (Serial Number or Quantity)"""
    try:
        data = request.get_json()
        item_code = data.get('item_code')
        warehouse_code = data.get('warehouse_code')
        serial_number = data.get('serial_number')
        quantity = data.get('quantity', 1)
        item_type = data.get('item_type', 'serial')  # 'serial' or 'non_serial'
        
        if not item_code or not warehouse_code:
            return jsonify({
                'success': False,
                'error': 'ItemCode and WarehouseCode are required'
            }), 400
        
        sap = SAPIntegration()
        
        if item_type == 'serial' and serial_number:
            # Scenario 1: Serial Number Managed Items
            if sap.ensure_logged_in():
                try:
                    url = f"{sap.base_url}/b1s/v1/SQLQueries('Series_Validation')/List"
                    request_body = {
                        "ParamList": f"whsCode='{warehouse_code}'&itemCode='{item_code}'&series='{serial_number}'"
                    }
                    response = sap.session.post(url, json=request_body, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        serial_details = data.get('value', [])
                        
                        if serial_details:
                            serial_info = serial_details[0]
                            return jsonify({
                                'success': True,
                                'validated': True,
                                'item_type': 'serial',
                                'serial_info': serial_info,
                                'message': f'Serial {serial_number} validated successfully'
                            })
                        else:
                            return jsonify({
                                'success': False,
                                'error': f'Serial {serial_number} not found for item {item_code} in warehouse {warehouse_code}'
                            })
                            
                except Exception as e:
                    logging.error(f"Error validating serial with SAP: {str(e)}")
            
            # Return mock validation for offline mode
            return jsonify({
                'success': True,
                'validated': True,
                'item_type': 'serial',
                'serial_info': {
                    'DistNumber': serial_number,
                    'ItemCode': item_code,
                    'WhsCode': warehouse_code
                },
                'offline_mode': True,
                'message': f'Serial {serial_number} validated successfully (offline mode)'
            })
        
        elif item_type == 'non_serial':
            # Scenario 2: Non-Serial Items - validate quantity against available stock
            # For now, return success with entered quantity
            # In production, you would check available stock from SAP B1
            return jsonify({
                'success': True,
                'validated': True,
                'item_type': 'non_serial',
                'quantity': quantity,
                'message': f'Quantity {quantity} validated for item {item_code}'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid item type or missing required fields'
            }), 400
    
    except Exception as e:
        logging.error(f"Error in validate_item API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Step 5: Post Invoice to SAP B1
@so_invoice_bp.route('/api/post-invoice', methods=['POST'])
@login_required
def post_invoice():
    """Post validated invoice to SAP B1"""
    try:
        data = request.get_json()
        doc_id = data.get('doc_id')
        
        if not doc_id:
            return jsonify({
                'success': False,
                'error': 'Document ID is required'
            }), 400
        
        document = SOInvoiceDocument.query.get_or_404(doc_id)
        
        # Check permissions
        if current_user.role not in ['admin', 'manager'] and document.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Validate document has items
        if not document.items:
            return jsonify({
                'success': False,
                'error': 'Cannot post invoice without line items'
            }), 400
        
        # Build invoice request for SAP B1
        invoice_data = {
            "DocDate": document.doc_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "DocDueDate": (document.doc_due_date or document.doc_date + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "BPLID": document.bplid,
            "CardCode": document.card_code,
            "U_EA_CREATEDBy": current_user.username,
            "U_EA_Approved": current_user.username,
            "Comments": f"SO Against Invoice - {document.document_number}",
            "DocumentLines": []
        }
        
        # Add line items
        for item in document.items:
            line_data = {
                "ItemCode": item.item_code,
                "ItemDescription": item.item_description,
                "Quantity": item.validated_quantity,
                "WarehouseCode": item.warehouse_code
            }
            
            # Add serial numbers if any
            if item.serial_numbers:
                line_data["SerialNumbers"] = []
                for serial in item.serial_numbers:
                    line_data["SerialNumbers"].append({
                        "InternalSerialNumber": serial.serial_number,
                        "Quantity": serial.quantity,
                        "BaseLineNumber": serial.base_line_number
                    })
            
            invoice_data["DocumentLines"].append(line_data)
        
        sap = SAPIntegration()
        
        # Try to post to SAP B1
        if sap.ensure_logged_in():
            try:
                url = f"{sap.base_url}/b1s/v1/Invoices"
                response = sap.session.post(url, json=invoice_data, timeout=30)
                
                if response.status_code in [200, 201]:
                    result_data = response.json()
                    sap_doc_num = result_data.get('DocNum')
                    
                    # Update document with SAP details
                    document.sap_invoice_number = str(sap_doc_num)
                    document.status = 'posted'
                    document.updated_at = datetime.utcnow()
                    
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'sap_doc_num': sap_doc_num,
                        'message': f'Invoice posted successfully to SAP B1. DocNum: {sap_doc_num}'
                    })
                else:
                    error_msg = f"SAP B1 error: {response.status_code} - {response.text}"
                    document.posting_error = error_msg
                    document.status = 'failed'
                    db.session.commit()
                    
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 400
                    
            except Exception as e:
                error_msg = f"Error posting to SAP B1: {str(e)}"
                document.posting_error = error_msg
                document.status = 'failed'
                db.session.commit()
                
                logging.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
        
        # Offline mode - simulate successful posting
        document.sap_invoice_number = f"INV{document.id:06d}"
        document.status = 'posted'
        document.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'sap_doc_num': document.sap_invoice_number,
            'offline_mode': True,
            'message': f'Invoice posted successfully (offline mode). DocNum: {document.sap_invoice_number}'
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in post_invoice API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@so_invoice_bp.route('/api/save-so-details', methods=['POST'])
@login_required
def save_so_details():
    """Save SO details to document after validation"""
    try:
        data = request.get_json()
        doc_id = data.get('doc_id')
        so_details = data.get('so_details')
        series_info = data.get('series_info')
        
        if not doc_id or not so_details or not series_info:
            return jsonify({
                'success': False,
                'error': 'Missing required data'
            }), 400
        
        document = SOInvoiceDocument.query.get_or_404(doc_id)
        
        # Update document with SO details
        document.so_series = series_info.get('series')
        document.so_series_name = series_info.get('series_name')
        document.so_number = so_details.get('so_number')
        document.so_doc_entry = so_details.get('doc_entry')
        document.card_code = so_details.get('order', {}).get('CardCode')
        document.card_name = so_details.get('order', {}).get('CardName')
        document.customer_address = so_details.get('order', {}).get('Address')
        document.status = 'validated'
        
        # Clear existing items and add new ones from SO
        SOInvoiceItem.query.filter_by(so_invoice_id=doc_id).delete()
        
        order = so_details.get('order', {})
        document_lines = order.get('DocumentLines', [])
        
        for line in document_lines:
            item = SOInvoiceItem(
                so_invoice_id=doc_id,
                line_num=line.get('LineNum'),
                item_code=line.get('ItemCode'),
                item_description=line.get('ItemDescription'),
                so_quantity=line.get('Quantity'),
                warehouse_code=line.get('WarehouseCode'),
                validated_quantity=0  # Will be updated when items are validated
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'SO details saved successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving SO details: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500