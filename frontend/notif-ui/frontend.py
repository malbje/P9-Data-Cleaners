# ------------------------------
# This page creates the buttons in the frontend via the 'Streamlit' framework, with backend-like logic.
# It is currently using in-memory storage (a list) to simulate a database for demo purposes.
#
#Note: st is the abriviation for streamlit and refered to in the import. 
#
#
# To run, type the following command in the terminal: streamlit run frontend\notif-ui\frontend.py
# ------------------------------

import streamlit as st
from datetime import date, datetime
import pandas as pd

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

import database.DB_write as DB_write
import database.DB_read as DB_read

# Demo mode flag
DEMO_MODE = True

# Custom exception class for validation errors in our business logic
class ValidationError(Exception):
    """Custom exception for handling validation errors in customer data"""
    pass

# Initialize session state for storing customer data in memory (demo mode only)
if "rows" not in st.session_state:
    st.session_state.rows = []  # This acts as our fake database in local memory

def find_index_by_email(email):
    """
    Find the index of a customer record by email address
    
    Args:
        email (str): The email address to search for
        
    Returns:
        int: Index of the customer in the list, or -1 if not found
    """
    for i, r in enumerate(st.session_state.rows):
        # Case-insensitive comparison with stripped whitespace
        if r["email"].lower().strip() == email.lower().strip():
            return i
    return -1  # Return -1 if customer not found

def create_customer_logic(name: str, email: str, adress: str, cleaning_date_str: str):
    """
    Create a new customer with comprehensive validation
    
    Args:
        name (str): Customer's full name
        email (str): Customer's email address (must be unique)
        adress (str): Customer's physical address
        cleaning_date_str (str): Cleaning date in YYYY-MM-DD format
        
    Returns:
        dict: Status dictionary with "ok" if successful
        
    Raises:
        ValidationError: If any validation rules fail
    """
    # Clean and normalize input data by stripping whitespace
    name = (name or "").strip()
    email = (email or "").strip()
    adress = (adress or "").strip()
    cleaning_date_string = (cleaning_date_str or "").strip()

    # Validate required fields
    if not name: 
        raise ValidationError("Name is required.")
    if "@" not in email: 
        raise ValidationError("Not a valid email address.")
    if not adress: 
        raise ValidationError("Address is required.")
    
    # Validate date format and parse it
    try:
        cleaning_date_str = datetime.strptime(cleaning_date_string, "%Y-%m-%d").date() # type: ignore
    except Exception:
        raise ValidationError("Date MUST be in the format YYYY-MM-DD.")
    
    # Business rule: cleaning date cannot be in the past
    if cleaning_date_str < date.today(): # type: ignore
        raise ValidationError("Cleaning date cannot be in the past.")
    
    # Business rule: email must be unique across all customers
    if find_index_by_email(email) != -1:
        raise ValidationError("A customer with this email already exists.")
    
    # All validations passed - add new customer to our in-memory database
    st.session_state.rows.append({
        "name": name, 
        "email": email, 
        "adress": adress, 
        "cleaning_date": cleaning_date_string
    })
    
    return {"status": "ok"}

def update_date_logic(email: str, new_date_str: str):
    """
    Update the cleaning date for an existing customer
    
    Args:
        email (str): Email of the customer to update
        new_date_str (str): New cleaning date in YYYY-MM-DD format
        
    Returns:
        dict: Status dictionary with "ok" if successful
        
    Raises:
        ValidationError: If customer not found or date invalid
    """
    # Clean input data
    email = (email or "").strip()
    new_date_string = (new_date_str or "").strip()
    
    # Validate and parse the new date
    try:
        cleaning_date = datetime.strptime(new_date_string, "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("New date must be in the format YYYY-MM-DD.")
    
    # Business rule: new date cannot be in the past
    if cleaning_date < date.today():
        raise ValidationError("New date cannot be in the past.")

def delete_customer_logic(email: str):
    """
    Delete a customer record by email address
    
    Args:
        email (str): Email of the customer to delete
        
    Returns:
        dict: Status dictionary with "ok" if successful
        
    Raises:
        ValidationError: If customer not found
    """
    # Clean input data
    email = (email or "").strip()
    
    # Find the customer record
    index = find_index_by_email(email)
    if index == -1:
        raise ValidationError("No customer found with that email.")
    
    # Remove the customer from our in-memory database
    st.session_state.rows.pop(index)
    return {"status": "ok"}

# ========== Streamlit UI (User Interface) ==========

# Configure the Streamlit page with title, icon, and layout
st.set_page_config(page_title="Cleaning Schedule - Admin", page_icon="🧹", layout="centered")
st.title("🧹 Cleaning Schedule - Admin")
st.caption("Frontend (buttons) to create, update, and delete customers.")

# Display current customers in an expandable table (for demo purposes)
with st.expander("📋 Current customers (demo)", expanded=True):
    # Convert our list of dictionaries to a pandas DataFrame for display
    dataFrame = pd.DataFrame(st.session_state.rows)
    if dataFrame.empty:
        # Show informational message when no customers exist
        st.info("No customers yet.")
    else:
        # Rename columns to English for better user experience
        dataFrame_show = dataFrame.rename(columns={
            "name": "Name", 
            "email": "Email", 
            "adress": "Address", 
            "cleaning_date": "Cleaning date" 
        })
        # Display the data in a nice table format
        st.dataframe(dataFrame_show, use_container_width=True, hide_index=True)

# Visual separator between sections
st.divider()

# ---------- Customer Creation Form ----------
st.subheader("Create customer")

# Use Streamlit form to group related inputs and handle submission together
with st.form("form_create", clear_on_submit=True):
    # Create two columns for better layout
    columnLeft, columnRight = st.columns(2)
    
    # Input fields for customer data
    name = columnLeft.text_input("Name")  # Customer name
    email = columnRight.text_input("Email")  # Customer email
    adress = st.text_input("Address")  # Customer address
    
    # Date picker for cleaning date (defaults to today)
    dateChosen = st.date_input("Cleaning date", value=date.today())
    
    # Form submission button
    create_clicked = st.form_submit_button("Create customer")
    
    # Handle form submission when button is clicked
    if create_clicked:
        try:
            # Call our business logic function with form data
            # Convert date to ISO format (YYYY-MM-DD) for consistency
            customerResult = create_customer_logic(name, email, adress, dateChosen.isoformat())

            db_writer = DB_write.DB_write()
            db_writer.create_user(name, adress, email)
            
            # Show success message to user
            st.success("Customer created.")
            
            # Refresh the page to show updated customer list
            st.rerun()
            
        except ValidationError as e:
            # Show validation errors to the user in red
            st.error(str(e))
        except Exception as e:
            # Catch any unexpected errors and display them
            st.error(f"Unexpected error: {e}")

st.divider()

# ---------- Date Update Form ----------
st.subheader("✏️ Update cleaning date")

# Form for updating existing customer's cleaning date
with st.form("form_update"):
    # Create two columns for better layout
    updateColumnLeft, updateColumnRight = st.columns(2)
    
    # Input fields for update operation
    email_update = updateColumnLeft.text_input("Customer email")  # Email to identify customer
    new_cleaning_date = updateColumnRight.date_input("New date", value=date.today())  # New cleaning date
    
    # Form submission button
    update_clicked = st.form_submit_button("Update date")
    
    # Handle form submission
    if update_clicked:
        try:
            # Call business logic to update the date
            update_date_logic(email_update, new_cleaning_date.isoformat())
            
            db_reader = DB_read.DB_read()
            db_writer = DB_write.DB_write()

            id = db_reader.get_appointment_id_by_customer_email(email_update)
            db_writer.update_appointment_date_by_id(id, new_cleaning_date.isoformat())

            # Show success message
            st.success("Date updated")
            
            # Refresh page to show changes
            st.rerun()
            
        except ValidationError as e:
            # Show validation errors
            st.error(str(e))
        except Exception as e:
            # Show unexpected errors
            st.error(f"Non existing email: {e}")

st.divider()

# ---------- Customer Deletion Form ----------
st.subheader("Delete customer")

# Form for deleting customers
with st.form("form_delete"):
    # Input field for customer email to delete
    email_delete = st.text_input("Customer email")
    
    # Form submission button (primary type makes it more prominent)
    delete_clicked = st.form_submit_button("Delete customer", type="primary")
    
    # Handle deletion with confirmation
    if delete_clicked:
        # Require user confirmation to prevent accidental deletions
        confirm = st.checkbox("Yes, I am sure")
        
        if confirm:
            try:
                # Call business logic to delete customer
                delete_customer_logic(email_delete)
                
                # Show success message
                st.success("Customer deleted")
                
                # Refresh page to show updated list
                st.rerun()
                
            except ValidationError as e:
                # Show validation errors
                st.error(str(e))
            except Exception as e:
                # Show unexpected errors
                st.error(f"Unexpected error: {e}")
        else:
            # Remind user to confirm deletion
            st.info("Check the box to confirm deletion")