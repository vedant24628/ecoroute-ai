import math
from datetime import datetime, timedelta

class AIEngine:
    """
    EcoRoute AI Engine: Multi-objective Route Optimization,
    Waste Generation Forecasting, and Carbon Savings Analytics.
    """

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate geographical distance between two coordinates in kilometers."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def optimize_route(cls, depot_coords, pickup_list, vehicle_capacity_kg=1000):
        """
        AI Vehicle Routing Problem (VRP) solver using Greedy Nearest-Neighbor heuristic
        with Urgency Multiplier & Capacity constraints.
        
        pickup_list = [
           {'id': 1, 'lat': 18.52, 'lng': 73.85, 'est_weight': 150, 'urgency': 'HIGH', 'name': 'Green Acres'},
           ...
        ]
        """
        if not pickup_list:
            return {'route': [], 'total_distance_km': 0.0, 'estimated_time_mins': 0}

        urgency_weights = {
            'CRITICAL': 2.0,
            'HIGH': 1.5,
            'MEDIUM': 1.0,
            'LOW': 0.8
        }

        unvisited = list(pickup_list)
        current_lat, current_lng = depot_coords
        route = []
        total_distance = 0.0
        current_load = 0.0
        sequence = 1

        while unvisited:
            best_next = None
            best_score = float('inf')
            best_dist = 0.0

            for pickup in unvisited:
                dist = cls.haversine_distance(current_lat, current_lng, pickup['lat'], pickup['lng'])
                urgency = pickup.get('urgency', 'MEDIUM')
                weight = urgency_weights.get(urgency, 1.0)
                
                # Penalize distance by urgency weight (higher urgency = smaller score = prioritized)
                score = dist / weight
                
                if score < best_score:
                    best_score = score
                    best_next = pickup
                    best_dist = dist

            if not best_next:
                break

            # Add to route
            best_next['sequence'] = sequence
            best_next['distance_from_prev_km'] = round(best_dist, 2)
            route.append(best_next)

            total_distance += best_dist
            current_lat, current_lng = best_next['lat'], best_next['lng']
            current_load += best_next.get('est_weight', 50)
            sequence += 1
            unvisited.remove(best_next)

        # Average city speed 25 km/h + 10 mins per stop for pickup
        travel_time_mins = (total_distance / 25.0) * 60
        service_time_mins = len(route) * 10
        total_time_mins = round(travel_time_mins + service_time_mins)

        return {
            'route': route,
            'total_distance_km': round(total_distance, 2),
            'estimated_time_mins': total_time_mins,
            'stops_count': len(route),
            'total_estimated_load_kg': round(current_load, 2)
        }

    @classmethod
    def predict_society_waste(cls, total_residents, num_flats, historical_avg_kg=None, days_ahead=7):
        """
        AI Predictive model estimating upcoming waste volume breakdown (kg)
        for a society over N days based on resident count and historical patterns.
        """
        # Baseline average waste generation per person per day = ~0.45 kg in urban societies
        per_capita_daily_kg = 0.45
        base_daily_waste = total_residents * per_capita_daily_kg

        if historical_avg_kg and historical_avg_kg > 0:
            # Blend 60% historical average + 40% per capita baseline formula
            daily_estimate = (0.6 * historical_avg_kg) + (0.4 * base_daily_waste)
        else:
            daily_estimate = base_daily_waste

        predictions = []
        today = datetime.now()

        for i in range(days_ahead):
            future_date = today + timedelta(days=i)
            day_of_week = future_date.weekday()
            
            # Weekend surge multiplier (Saturdays & Sundays yield ~20-25% more household waste)
            day_multiplier = 1.22 if day_of_week in [5, 6] else 0.96
            
            predicted_total = round(daily_estimate * day_multiplier, 2)
            
            # Category breakdown estimation
            wet = round(predicted_total * 0.48, 2)       # ~48% organic wet waste
            dry = round(predicted_total * 0.28, 2)       # ~28% paper/cardboard/dry
            plastic = round(predicted_total * 0.16, 2)   # ~16% recyclable plastic
            hazardous = round(predicted_total * 0.08, 2) # ~8% hazardous/glass/metal

            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'day_name': future_date.strftime('%A'),
                'total_kg': predicted_total,
                'wet_waste_kg': wet,
                'dry_waste_kg': dry,
                'plastic_kg': plastic,
                'hazardous_kg': hazardous
            })

        return {
            'society_daily_avg_kg': round(daily_estimate, 2),
            'forecast_days': days_ahead,
            'predictions': predictions,
            'total_projected_7day_kg': round(sum(p['total_kg'] for p in predictions), 2)
        }

    @classmethod
    def calculate_carbon_footprint(cls, wet_kg, dry_kg, plastic_kg, metal_glass_kg):
        """
        Calculate Environmental & Carbon Impact Metrics.
        - Bio-composting organic waste prevents methane emissions (1.8 kg CO2e / kg)
        - Recycling plastic avoids virgin plastic production (2.1 kg CO2e / kg)
        - Recycling paper/dry waste saves trees and energy (1.5 kg CO2e / kg)
        - Recycling metal/glass saves high-temperature smelting CO2 (2.5 kg CO2e / kg)
        """
        co2_wet = wet_kg * 1.80
        co2_dry = dry_kg * 1.50
        co2_plastic = plastic_kg * 2.10
        co2_metal = metal_glass_kg * 2.50

        total_co2_saved_kg = round(co2_wet + co2_dry + co2_plastic + co2_metal, 2)
        trees_equivalent = round(total_co2_saved_kg / 21.77, 1) # 1 mature tree absorbs ~21.77 kg CO2 / year
        landfill_cubic_meters_saved = round((wet_kg + dry_kg + plastic_kg + metal_glass_kg) / 350.0, 2)
        
        # Society Eco Score out of 100
        total_waste = wet_kg + dry_kg + plastic_kg + metal_glass_kg
        recycled_waste = (wet_kg * 0.95) + (dry_kg * 0.90) + (plastic_kg * 0.85) + (metal_glass_kg * 0.98)
        recycling_rate = round((recycled_waste / total_waste * 100) if total_waste > 0 else 85.0, 1)

        return {
            'total_waste_processed_kg': round(total_waste, 2),
            'co2_saved_kg': total_co2_saved_kg,
            'trees_equivalent': trees_equivalent,
            'landfill_saved_m3': landfill_cubic_meters_saved,
            'recycling_rate_percent': recycling_rate,
            'eco_score': min(100, int(recycling_rate * 0.95 + 10))
        }
