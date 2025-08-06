#!/usr/bin/env python3
"""
Debug script to test patient listing
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.models.models import Patient as PatientModel

async def debug_patients():
    try:
        # Initialize database connection
        from app.db.database import connect_to_mongo
        await connect_to_mongo()
        
        # Get patients
        patients = await PatientModel.find().limit(1).to_list()
        
        if patients:
            patient = patients[0]
            print(f"Patient ID type: {type(patient.id)}")
            print(f"Patient ID value: {patient.id}")
            print(f"Patient attributes: {dir(patient)}")
            print(f"Patient.patient_id: {getattr(patient, 'patient_id', 'NOT_FOUND')}")
            
            # Test model_dump
            try:
                dumped = patient.model_dump()
                print(f"Model dump keys: {dumped.keys()}")
                print(f"Model dump _id: {dumped.get('_id', 'NOT_FOUND')}")
            except Exception as e:
                print(f"Model dump error: {e}")
        else:
            print("No patients found")
            
    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_patients())
