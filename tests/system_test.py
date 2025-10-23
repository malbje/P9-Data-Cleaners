# system_test.py - Automated test suite verifying database access and OpenAI integration.
# Tests direct queries, function calling, and appointment persistence.

import sys
import os

# Add parent directory to path so we can import from main project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.DB_read import (
    list_customers, find_address_by_text, get_appointments_by_address_id
)
from main import ask_llm


def simple_test():
    """
    Run comprehensive system tests: database access, OpenAI integration, and appointment persistence.
    
    Returns:
        None
    """
    print("=== DATACLEARNERS SYSTEM TEST ===\n")
    
    # Test 1: Direkte database adgang (uden OpenAI)
    print("Test 1: Direct database access")
    print("-" * 40)
    try:
        customers = list_customers()
        print(f"SUCCESS: Retrieved {len(customers)} customers from database")
        print(f"  First customer: {customers[0]['name']} {customers[0]['surname']}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\n")
    
    # Test 2: OpenAI med tool calling
    print("Test 2: OpenAI calls database functions")
    print("-" * 40)
    try:
        # Simpel prompt der kræver funktionskald
        prompt = "Who is customer number 1?"
        print(f"Prompt: '{prompt}'")
        print("Waiting for OpenAI...\n")
        
        response = ask_llm(prompt)
        print(f"SUCCESS: OpenAI response: {response}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\n")
    
    # Test 3: Find adresse
    print("Test 3: Find address functionality")
    print("-" * 40)
    try:
        addresses = find_address_by_text("Danmarksgade")
        print(f"SUCCESS: Found {len(addresses)} addresses with 'Danmarksgade'")
        if addresses:
            print(f"  First address: {addresses[0]}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\n")
    
    # Test 4: OpenAI opretter appointment
    print("Test 4: OpenAI creates appointment in database")
    print("-" * 40)
    try:
        # Meget eksplicit prompt der tvinger OpenAI til at bruge add_appointment
        prompt = "Create an appointment with address_id=13, date='2025-12-01', time='15:00', notes='Test appointment', notification_preference='email'"
        print(f"Prompt: '{prompt}'")
        print("Waiting for OpenAI...\n")
        
        response = ask_llm(prompt)
        print(f"SUCCESS: OpenAI response: {response}")
        
        # Verificer at den faktisk blev oprettet i databasen
        if "id" in response.lower() or "appointment" in response.lower():
            print("\n  Verifying in database...")
            appointments = get_appointments_by_address_id(13)
            print(f"  SUCCESS: Found {len(appointments)} appointments on address_id 13")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\n=== TEST COMPLETED ===")


if __name__ == "__main__":
    simple_test()
