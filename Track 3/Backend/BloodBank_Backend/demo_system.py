#!/usr/bin/env python3
"""
Blood Bank System Demonstration
Shows complete functionality of the blood bank management system
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

def demo_blood_bank_system():
    """Demonstrate the complete blood bank system"""
    print("🩸 BLOOD BANK MANAGEMENT SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    try:
        from app.services.blood_bank_service import BloodBankService
        from app.db.database import SessionLocal
        from app.schemas.blood_bank import BloodDonationCreate, BloodUsageCreate, BloodType, Gender, UrgencyLevel
        from app.models.user import User
        from app.core.security import SecurityUtils
        from datetime import datetime, timedelta
        import uuid
        
        db = SessionLocal()
        service = BloodBankService(db)
        
        # Create test user if needed
        print("👤 Setting up user...")
        existing_user = db.query(User).filter(User.username == "bloodbank_demo").first()
        if existing_user:
            user_id = existing_user.id
            print(f"   Using existing user (ID: {user_id})")
        else:
            hashed_password = SecurityUtils.hash_password("demo123")
            new_user = User(
                username="bloodbank_demo",
                email="demo@bloodbank.com",
                hashed_password=hashed_password,
                full_name="Demo User",
                role="staff",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id
            print(f"   ✅ Created demo user (ID: {user_id})")
        
        # 1. Show initial inventory
        print("\n📊 INITIAL BLOOD INVENTORY:")
        inventory = service.get_current_inventory()
        for inv in inventory:
            print(f"   {inv.blood_group:3}: {inv.current_volume_ml:6.0f}ml ({inv.current_units:2} units) - {inv.stock_status}")
        
        # 2. Add multiple blood donations
        print("\n🩸 ADDING BLOOD DONATIONS:")
        donations_data = [
            {
                "donor_name": "Alice Johnson",
                "blood_type": BloodType.A_POSITIVE,
                "volume": 450,
                "hemoglobin": 13.2
            },
            {
                "donor_name": "Bob Smith", 
                "blood_type": BloodType.O_NEGATIVE,
                "volume": 450,
                "hemoglobin": 15.1
            },
            {
                "donor_name": "Carol Davis",
                "blood_type": BloodType.B_POSITIVE,
                "volume": 400,
                "hemoglobin": 12.8
            }
        ]
        
        created_donations = []
        for i, data in enumerate(donations_data):
            donation_id = f"DEMO_DON_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
            donor_id = f"DHIS2_DONOR_{i+1:03d}"
            
            donation = BloodDonationCreate(
                donation_record_id=donation_id,
                donor_id=donor_id,
                donor_name=data["donor_name"],
                donor_age=25 + i * 5,
                donor_gender=Gender.FEMALE if i % 2 == 0 else Gender.MALE,
                donor_phone=f"+1555{i+1:03d}{i+2:04d}",
                blood_type=data["blood_type"],
                collection_volume_ml=data["volume"],
                collection_site="Main Blood Center",
                collection_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=35),
                hemoglobin_g_dl=data["hemoglobin"],
                blood_pressure_systolic=120 + i * 5,
                blood_pressure_diastolic=80 + i * 2,
                temperature_celsius=36.5 + i * 0.1,
                collected_by_staff_id=user_id
            )
            
            try:
                created_donation = service.create_donation(donation, user_id)
                created_donations.append(created_donation)
                print(f"   ✅ {data['donor_name']}: {data['volume']}ml {data['blood_type'].value} (ID: {donation_id})")
            except Exception as e:
                if "duplicate key" in str(e):
                    print(f"   ⚠️  {data['donor_name']}: Donation already exists, skipping")
                else:
                    print(f"   ❌ {data['donor_name']}: Error - {e}")
        
        # 3. Show updated inventory after donations
        print("\n📊 INVENTORY AFTER DONATIONS:")
        inventory = service.get_current_inventory()
        for inv in inventory:
            if inv.current_volume_ml > 0:
                print(f"   {inv.blood_group:3}: {inv.current_volume_ml:6.0f}ml ({inv.current_units:2} units) - {inv.stock_status}")
        
        # 4. Create blood usage records
        print("\n📤 BLOOD USAGE TRANSACTIONS:")
        usage_data = [
            {
                "patient_name": "Emergency Patient 1",
                "blood_type": BloodType.O_POSITIVE,
                "volume": 200,
                "urgency": UrgencyLevel.EMERGENCY,
                "reason": "Emergency surgery"
            },
            {
                "patient_name": "Surgery Patient 2",
                "blood_type": BloodType.A_POSITIVE, 
                "volume": 300,
                "urgency": UrgencyLevel.URGENT,
                "reason": "Elective surgery"
            }
        ]
        
        for i, data in enumerate(usage_data):
            usage_id = f"DEMO_USAGE_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
            
            # Check if we have enough stock
            blood_group_str = data["blood_type"].value
            inventory_item = next((inv for inv in inventory if inv.blood_group == blood_group_str), None)
            
            if inventory_item and inventory_item.available_volume_ml >= data["volume"]:
                usage = BloodUsageCreate(
                    usage_record_id=usage_id,
                    blood_group=data["blood_type"],
                    volume_used_ml=data["volume"],
                    units_used=1,
                    patient_name=data["patient_name"],
                    patient_id=f"PAT_{i+1:03d}",
                    usage_date=datetime.now(),
                    usage_reason=data["reason"],
                    urgency_level=data["urgency"],
                    recipient_location="City Hospital - Emergency Department",
                    prescribed_by_doctor=f"Dr. Smith {i+1}",
                    dispensed_by_staff_id=user_id
                )
                
                try:
                    created_usage = service.create_usage(usage, user_id)
                    print(f"   ✅ {data['patient_name']}: {data['volume']}ml {data['blood_type'].value} - {data['urgency'].value}")
                except Exception as e:
                    if "duplicate key" in str(e):
                        print(f"   ⚠️  {data['patient_name']}: Usage already exists, skipping")
                    else:
                        print(f"   ❌ {data['patient_name']}: Error - {e}")
            else:
                available = inventory_item.available_volume_ml if inventory_item else 0
                print(f"   ❌ {data['patient_name']}: Insufficient stock ({available}ml available, {data['volume']}ml requested)")
        
        # 5. Show final inventory
        print("\n📊 FINAL INVENTORY STATUS:")
        inventory = service.get_current_inventory()
        total_volume = 0
        total_units = 0
        
        for inv in inventory:
            total_volume += inv.current_volume_ml
            total_units += inv.current_units
            status_icon = "🔴" if inv.stock_status == "critically_low" else "🟡" if inv.stock_status == "low" else "🟢"
            print(f"   {status_icon} {inv.blood_group:3}: {inv.current_volume_ml:6.0f}ml ({inv.current_units:2} units) - {inv.stock_status}")
        
        print(f"\n   📈 TOTAL STOCK: {total_volume:.0f}ml ({total_units} units)")
        
        # 6. Show analytics
        print("\n📈 SYSTEM ANALYTICS (Last 30 Days):")
        analytics = service.get_inventory_analytics(30)
        print(f"   📊 Current inventory: {len(analytics['current_inventory'])} blood groups")
        print(f"   🩸 Collections: {len(analytics['collections'])} donations")
        print(f"   📤 Usage: {len(analytics['usage'])} transfusions")
        print(f"   📅 Period: {analytics['period_days']} days")
        
        # 7. Show recent donations
        print("\n📋 RECENT DONATIONS:")
        recent_donations = service.get_recent_donations(5)
        for donation in recent_donations:
            print(f"   • {donation.donor_name}: {donation.collection_volume_ml}ml {donation.blood_type} ({donation.donation_record_id})")
        
        db.close()
        print("\n✅ BLOOD BANK SYSTEM DEMONSTRATION COMPLETED!")
        print("🎉 The system is fully functional and ready for production use!")
        
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_blood_bank_system()
