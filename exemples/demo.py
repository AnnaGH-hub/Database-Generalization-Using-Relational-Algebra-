def main():
    """
    Demonstration of database generalization with relational algebra.
    """
    # Connection string - UPDATE WITH YOUR CREDENTIALS
    conn_string = "dbname=company_db user=postgres password=yourpassword host=localhost"
    
    print("=" * 80)
    print("DATABASE GENERALIZATION DEMONSTRATION")
    print("=" * 80)
    
    try:
        with DatabaseManager(conn_string) as db:
            # ================================================================
            # CREATE NEW CUSTOMER
            # ================================================================
            print("\n1. Creating New Customer...")
            person = Person(
                person_id=None,
                name="Alice Thompson",
                address="100 Tech Street, Seattle, WA",
                phone="555-0200",
                email="alice.thompson@email.com",
                person_type="Customer"
            )
            customer = Customer(
                customer_id=None,
                person_id=0,  # Will be set by create_customer
                loyalty_points=500,
                customer_tier="Silver"
            )
            
            person_id, customer_id = db.create_customer(person, customer)
            print(f"   ✓ Created: PersonID={person_id}, CustomerID={customer_id}")
            
            # ================================================================
            # RETRIEVE COMPLETE CUSTOMER
            # ================================================================
            print("\n2. Retrieving Complete Customer Information...")
            customer_info = db.get_customer_complete(customer_id)
            print(f"   Name: {customer_info['name']}")
            print(f"   Email: {customer_info['email']}")
            print(f"   Loyalty Points: {customer_info['loyaltypoints']}")
            print(f"   Tier: {customer_info['customertier']}")
            
            # ================================================================
            # RELATIONAL ALGEBRA: UNION
            # ================================================================
            print("\n3. UNION Operation - All Contacts")
            print("   Relational Algebra: π[Name,Email](Customers) ∪ π[Name,Email](Employees)")
            contacts = db.demonstrate_union()
            print(f"   Found {len(contacts)} unique contacts:")
            for contact in contacts[:5]:
                print(f"   - {contact['name']}: {contact['email']} ({contact['type']})")
            
            # ================================================================
            # RELATIONAL ALGEBRA: INTERSECTION
            # ================================================================
            print("\n4. INTERSECTION Operation - Both Customer AND Employee")
            print("   Relational Algebra: π[PersonID](Customers) ∩ π[PersonID](Employees)")
            both = db.demonstrate_intersection()
            print(f"   Found {len(both)} persons with both roles:")
            for person in both:
                print(f"   - {person['name']}: {person['loyaltypoints']} pts, {person['department']} dept")
            
            # ================================================================
            # RELATIONAL ALGEBRA: DIFFERENCE
            # ================================================================
            print("\n5. SET DIFFERENCE Operation")
            print("   Relational Algebra: π[PersonID](Customers) - π[PersonID](Employees)")
            customers_only, employees_only = db.demonstrate_difference()
            print(f"   Customers only: {len(customers_only)}")
            print(f"   Employees only: {len(employees_only)}")
            
            # ================================================================
            # RELATIONAL ALGEBRA: PROJECTION
            # ================================================================
            print("\n6. PROJECTION Operation - Unique Departments")
            print("   Relational Algebra: π[Department](Employee)")
            departments = db.demonstrate_projection()
            print(f"   Departments: {', '.join(departments)}")
            
            # ================================================================
            # RELATIONAL ALGEBRA: SELECTION
            # ================================================================
            print("\n7. SELECTION Operation - High-Value Customers")
            print("   Relational Algebra: σ[LoyaltyPoints >= 1000](Customers)")
            high_value = db.demonstrate_selection(min_loyalty=1000)
            print(f"   Found {len(high_value)} high-value customers:")
            for cust in high_value:
                print(f"   - {cust['name']}: {cust['loyaltypoints']} points ({cust['customertier']})")
            
            # ================================================================
            # AGGREGATE OPERATIONS
            # ================================================================
            print("\n8. AGGREGATE Operation - Department Statistics")
            print("   Relational Algebra: γ[Department; AVG(Salary), COUNT(*)](Employee)")
            stats = db.get_department_statistics()
            for stat in stats:
                print(f"   {stat['department']}:")
                print(f"      Employees: {stat['employeecount']}")
                print(f"      Avg Salary: ${stat['avgsalary']:,.2f}")
            
            print("\n" + "=" * 80)
            print("DEMONSTRATION COMPLETE")
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
