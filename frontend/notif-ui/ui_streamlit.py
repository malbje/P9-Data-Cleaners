# ------------------------------
# This page creates the buttons in the frontend via the 'Streamlit' framework.
#
# To run type the following command in the terminal: streamlit run frontend\notif-ui\ui_streamlit.py
# ------------------------------

import streamlit as st
from datetime import date, datetime
import pandas as pd

# Demo mode flag - when True, uses in-memory storage instead of real database
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
    dstr = (cleaning_date_str or "").strip()

    # Validate required fields
    if not name: 
        raise ValidationError("Navn er påkrævet.")
    if "@" not in email: 
        raise ValidationError("Ikke en rigtig email adresse.")
    if not adress: 
        raise ValidationError("Adresse er påkrævet.")
    
    # Validate date format and parse it
    try:
        d = datetime.strptime(dstr, "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("Dato SKAL være i formatet YYYY-MM-DD.")
    
    # Business rule: cleaning date cannot be in the past
    if d < date.today():
        raise ValidationError("Rengøringsdato må ikke ligge i fortiden.")
    
    # Business rule: email must be unique across all customers
    if find_index_by_email(email) != -1:
        raise ValidationError("Der findes allerede en kunde med denne email.")
    
    # All validations passed - add new customer to our in-memory database
    st.session_state.rows.append({
        "name": name, 
        "email": email, 
        "adress": adress, 
        "cleaning_date": dstr
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
    dstr = (new_date_str or "").strip()
    
    # Validate and parse the new date
    try:
        d = datetime.strptime(dstr, "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("Ny dato skal være i formatet YYYY-MM-DD.")
    
    # Business rule: new date cannot be in the past
    if d < date.today():
        raise ValidationError("Ny dato må ikke ligge i fortiden.")
    
    # Find the customer record
    idx = find_index_by_email(email)
    if idx == -1:
        raise ValidationError("Ingen kunde fundet med den email.")
    
    # Update the cleaning date for the found customer
    st.session_state.rows[idx]["cleaning_date"] = dstr
    return {"status": "ok"}

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
    idx = find_index_by_email(email)
    if idx == -1:
        raise ValidationError("Ingen kunde fundet med den email.")
    
    # Remove the customer from our in-memory database
    st.session_state.rows.pop(idx)
    return {"status": "ok"}

# ========== Streamlit UI (User Interface) ==========

# Configure the Streamlit page with title, icon, and layout
st.set_page_config(page_title="Rengøringsplan - Admin", page_icon="🧹", layout="centered")
st.title("🧹 Rengøringsplan - Admin")
st.caption("Frontend (knapper) til at oprette, opdatere og slette kunder.")

# Display current customers in an expandable table (for demo purposes)
with st.expander("📋 Aktuelle kunder (demo)", expanded=True):
    # Convert our list of dictionaries to a pandas DataFrame for display
    df = pd.DataFrame(st.session_state.rows)
    
    if df.empty:
        # Show informational message when no customers exist
        st.info("Ingen kunder endnu.")
    else:
        # Rename columns to Danish for better user experience
        df_show = df.rename(columns={
            "name": "Navn", 
            "email": "Email", 
            "adress": "Adresse", 
            "cleaning_date": "Rengøringsdato" 
        })
        # Display the data in a nice table format
        st.dataframe(df_show, use_container_width=True, hide_index=True)

# Visual separator between sections
st.divider()

# ---------- Customer Creation Form ----------
st.subheader("➕ Opret kunde")

# Use Streamlit form to group related inputs and handle submission together
with st.form("form_create", clear_on_submit=True):
    # Create two columns for better layout
    c1, c2 = st.columns(2)
    
    # Input fields for customer data
    name = c1.text_input("Navn")  # Customer name
    email = c2.text_input("Email")  # Customer email
    adress = st.text_input("Adresse")  # Customer address
    
    # Date picker for cleaning date (defaults to today)
    d = st.date_input("Rengøringsdato", value=date.today())
    
    # Form submission button
    create_clicked = st.form_submit_button("Opret kunde")
    
    # Handle form submission when button is clicked
    if create_clicked:
        try:
            # Call our business logic function with form data
            # Convert date to ISO format (YYYY-MM-DD) for consistency
            res = create_customer_logic(name, email, adress, d.isoformat())
            
            # Show success message to user
            st.success("Kunde oprettet.")
            
            # Refresh the page to show updated customer list
            st.rerun()
            
        except ValidationError as e:
            # Show validation errors to the user in red
            st.error(str(e))
        except Exception as e:
            # Catch any unexpected errors and display them
            st.error(f"Uventet fejl: {e}")

st.divider()

# ---------- Date Update Form ----------
st.subheader("✏️ Opdater rengøringsdato")

# Form for updating existing customer's cleaning date
with st.form("form_update"):
    # Create two columns for better layout
    u1, u2 = st.columns(2)
    
    # Input fields for update operation
    email_u = u1.text_input("Kunden email")  # Email to identify customer
    d_new = u2.date_input("Ny dato", value=date.today())  # New cleaning date
    
    # Form submission button
    update_clicked = st.form_submit_button("Opdatér dato")
    
    # Handle form submission
    if update_clicked:
        try:
            # Call business logic to update the date
            update_date_logic(email_u, d_new.isoformat())
            
            # Show success message
            st.success("Dato opdateret")
            
            # Refresh page to show changes
            st.rerun()
            
        except ValidationError as e:
            # Show validation errors
            st.error(str(e))
        except Exception as e:
            # Show unexpected errors
            st.error(f"Uventet fejl: {e}")

st.divider()

# ---------- Customer Deletion Form ----------
st.subheader("🗑️ Slet kunde")

# Form for deleting customers
with st.form("form_delete"):
    # Input field for customer email to delete
    email_d = st.text_input("Kundens email")
    
    # Form submission button (primary type makes it more prominent)
    delete_clicked = st.form_submit_button("Slet kunde", type="primary")
    
    # Handle deletion with confirmation
    if delete_clicked:
        # Require user confirmation to prevent accidental deletions
        confirm = st.checkbox("Ja, jeg er sikker")
        
        if confirm:
            try:
                # Call business logic to delete customer
                delete_customer_logic(email_d)
                
                # Show success message
                st.success("Kunde slettet")
                
                # Refresh page to show updated list
                st.rerun()
                
            except ValidationError as e:
                # Show validation errors
                st.error(str(e))
            except Exception as e:
                # Show unexpected errors
                st.error(f"Uventet fejl: {e}")
        else:
            # Remind user to confirm deletion
            st.info("Sæt flueben for at bekræfte sletning")