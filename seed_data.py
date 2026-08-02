import os
from datetime import datetime, date, timedelta
from app import create_app
from app.models import (db, Admin, Society, Driver, Worker, Vehicle, WasteCategory,
                        PickupRequest, Assignment, Collection, WasteProcessing, SystemSettings)

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()

        print("--> Seeding Waste Categories...")
        categories = [
            ('Organic / Wet Waste', 'Food scraps, kitchen waste, garden waste suitable for bio-composting.', '#2E7D32', 95.0, 1.80),
            ('Dry & Paper Waste', 'Paper, cardboard boxes, dry leaves, packaging materials.', '#43A047', 90.0, 1.50),
            ('Recyclable Plastic', 'PET bottles, HDPE containers, plastic covers, bags.', '#00BCD4', 85.0, 2.10),
            ('Glass & Metal', 'Glass bottles, aluminum cans, scrap metal.', '#0288D1', 98.0, 2.50),
            ('E-Waste', 'Old electronics, cables, batteries, circuit boards.', '#FB8C00', 70.0, 3.20),
            ('Hazardous Waste', 'Chemicals, paints, fluorescent lamps, medical waste.', '#D32F2F', 40.0, 4.00)
        ]

        for name, desc, color, rate, co2 in categories:
            if not WasteCategory.query.filter_by(name=name).first():
                c = WasteCategory(name=name, description=desc, color_code=color, recyclable_rate=rate, co2_factor=co2)
                db.session.add(c)

        print("--> Seeding Super Admin...")
        if not Admin.query.filter_by(email='admin@ecoroute.ai').first():
            admin = Admin(
                full_name='System Admin',
                email='admin@ecoroute.ai',
                phone='+91 99000 11223',
                role='SUPER_ADMIN'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)

        print("--> Seeding Societies...")
        societies_data = [
            {
                'name': 'Green Acres Housing Complex',
                'reg': 'REG-PUN-2024-101',
                'sec': 'Mr. Rajesh Sharma',
                'email': 'secretary@greenacres.com',
                'phone': '+91 98765 00001',
                'addr': 'Sector 4, Kothrud',
                'city': 'Pune', 'state': 'Maharashtra', 'pin': '411038',
                'lat': 18.5300, 'lng': 73.8400,
                'flats': 240, 'residents': 960, 'waste': 280.0
            },
            {
                'name': 'Silver Oak Heights',
                'reg': 'REG-PUN-2024-102',
                'sec': 'Mrs. Sunita Kulkarni',
                'email': 'secretary@silveroak.com',
                'phone': '+91 98765 00002',
                'addr': 'Viman Nagar Main Road',
                'city': 'Pune', 'state': 'Maharashtra', 'pin': '411014',
                'lat': 18.5100, 'lng': 73.8700,
                'flats': 180, 'residents': 720, 'waste': 210.0
            },
            {
                'name': 'Royal Palms Residency',
                'reg': 'REG-PUN-2024-103',
                'sec': 'Dr. Amit Verma',
                'email': 'secretary@royalpalms.com',
                'phone': '+91 98765 00003',
                'addr': 'Baner Road, Near Expressway',
                'city': 'Pune', 'state': 'Maharashtra', 'pin': '411045',
                'lat': 18.5450, 'lng': 73.8800,
                'flats': 310, 'residents': 1240, 'waste': 360.0
            },
            {
                'name': 'Harmony Park Society',
                'reg': 'REG-PUN-2024-104',
                'sec': 'Ms. Neha Gupta',
                'email': 'secretary@harmonypark.com',
                'phone': '+91 98765 00004',
                'addr': 'Hadapsar Magarpatta Road',
                'city': 'Pune', 'state': 'Maharashtra', 'pin': '411028',
                'lat': 18.4900, 'lng': 73.8300,
                'flats': 120, 'residents': 480, 'waste': 140.0
            }
        ]

        created_societies = []
        for sinfo in societies_data:
            s = Society.query.filter_by(email=sinfo['email']).first()
            if not s:
                s = Society(
                    society_name=sinfo['name'],
                    registration_number=sinfo['reg'],
                    secretary_name=sinfo['sec'],
                    email=sinfo['email'],
                    phone=sinfo['phone'],
                    address=sinfo['addr'],
                    city=sinfo['city'], state=sinfo['state'], pin_code=sinfo['pin'],
                    latitude=sinfo['lat'], longitude=sinfo['lng'],
                    num_flats=sinfo['flats'], total_residents=sinfo['residents'],
                    estimated_daily_waste=sinfo['waste'],
                    status='APPROVED'
                )
                s.set_password('Society123!')
                db.session.add(s)
            created_societies.append(s)

        db.session.commit()

        print("--> Seeding Drivers & Workers...")
        drivers_data = [
            ('Suresh Patil', 'DL-MH12-2021-9988', '+91 98220 11111', 'suresh@ecoroute.ai'),
            ('Ramesh Shinde', 'DL-MH12-2022-7744', '+91 98220 22222', 'ramesh@ecoroute.ai'),
            ('Anil Kumar', 'DL-MH12-2023-1122', '+91 98220 33333', 'anil@ecoroute.ai')
        ]
        created_drivers = []
        for dname, dlic, dphone, demail in drivers_data:
            d = Driver.query.filter_by(license_number=dlic).first()
            if not d:
                d = Driver(full_name=dname, license_number=dlic, phone=dphone, email=demail, status='ON_DUTY')
                db.session.add(d)
            created_drivers.append(d)

        workers_data = [
            ('Vikram Singh', 'worker@ecoroute.ai', '+91 97110 11111', 'WRK-101'),
            ('Ganesh Pawar', 'ganesh@ecoroute.ai', '+91 97110 22222', 'WRK-102'),
            ('Rahul Deshmukh', 'rahul@ecoroute.ai', '+91 97110 33333', 'WRK-103')
        ]
        created_workers = []
        for wname, wemail, wphone, empid in workers_data:
            w = Worker.query.filter_by(employee_id=empid).first()
            if not w:
                w = Worker(full_name=wname, email=wemail, phone=wphone, employee_id=empid, status='ASSIGNED')
                w.set_password('Worker123!')
                db.session.add(w)
            created_workers.append(w)

        db.session.commit()

        print("--> Seeding Vehicles...")
        vehicles_data = [
            ('MH-12-EC-409', 'Electric Tipper Truck', 1500.0, 'GPS-TRK-409', 18.5250, 73.8480, 'On Route'),
            ('MH-12-EC-712', 'Hydraulic Waste Compactor', 3000.0, 'GPS-TRK-712', 18.5150, 73.8650, 'Assigned'),
            ('MH-12-EC-905', 'Mini Collection Van', 1000.0, 'GPS-TRK-905', 18.5204, 73.8567, 'Available')
        ]
        created_vehicles = []
        for idx, (vno, vtype, cap, gps, lat, lng, st) in enumerate(vehicles_data):
            v = Vehicle.query.filter_by(vehicle_number=vno).first()
            if not v:
                v = Vehicle(
                    vehicle_number=vno, vehicle_type=vtype, capacity_kg=cap,
                    gps_device_id=gps, current_lat=lat, current_lng=lng, status=st,
                    driver_id=created_drivers[idx].id if idx < len(created_drivers) else None,
                    worker_id=created_workers[idx].id if idx < len(created_workers) else None
                )
                db.session.add(v)
            created_vehicles.append(v)

        db.session.commit()

        print("--> Seeding Pickup Requests & Sample Collections...")
        # Create requests
        req1 = PickupRequest.query.filter_by(request_code='REQ-88910').first()
        if not req1:
            req1 = PickupRequest(
                society_id=created_societies[0].id,
                request_code='REQ-88910',
                scheduled_date=date.today(),
                preferred_slot='07:00 AM - 09:00 AM',
                estimated_weight=260.0,
                status='ASSIGNED',
                urgency_level='HIGH'
            )
            db.session.add(req1)
            db.session.commit()

            asgn1 = Assignment(
                pickup_request_id=req1.id,
                vehicle_id=created_vehicles[0].id,
                worker_id=created_workers[0].id,
                driver_id=created_drivers[0].id,
                estimated_eta_minutes=12,
                status='EN_ROUTE'
            )
            db.session.add(asgn1)

        req2 = PickupRequest.query.filter_by(request_code='REQ-88911').first()
        if not req2:
            req2 = PickupRequest(
                society_id=created_societies[1].id,
                request_code='REQ-88911',
                scheduled_date=date.today() - timedelta(days=1),
                preferred_slot='09:00 AM - 11:00 AM',
                estimated_weight=200.0,
                status='COMPLETED',
                urgency_level='MEDIUM'
            )
            db.session.add(req2)
            db.session.commit()

            asgn2 = Assignment(
                pickup_request_id=req2.id,
                vehicle_id=created_vehicles[1].id,
                worker_id=created_workers[1].id,
                driver_id=created_drivers[1].id,
                status='COMPLETED'
            )
            db.session.add(asgn2)
            db.session.commit()

            col = Collection(
                assignment_id=asgn2.id,
                society_id=created_societies[1].id,
                worker_id=created_workers[1].id,
                vehicle_id=created_vehicles[1].id,
                wet_waste_kg=105.0,
                dry_waste_kg=60.0,
                recyclable_kg=35.0,
                hazardous_kg=10.0,
                total_weight_kg=210.0,
                image_proof='default_proof.jpg',
                remarks='Collection complete. Segregation level 95%.'
            )
            db.session.add(col)
            db.session.commit()

            wp = WasteProcessing(
                collection=col,
                composted_kg=96.6,
                recycled_plastic_kg=29.75,
                recycled_paper_kg=52.8,
                recycled_metal_kg=4.0,
                landfill_kg=21.0,
                co2_saved_kg=388.5
            )
            db.session.add(wp)

        db.session.commit()
        print("--> Database Seeding Completed Successfully!")

if __name__ == '__main__':
    seed_database()
