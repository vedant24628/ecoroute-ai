/**
 * EcoRoute AI - Live Vehicle Tracking Engine (Leaflet.js & OpenStreetMap)
 */

class LiveTracker {
    constructor(mapContainerId, options = {}) {
        this.mapId = mapContainerId;
        this.options = options;
        this.map = null;
        this.vehicleMarkers = {};
        this.societyMarkers = {};
        this.societyFootprints = {};
        this.routePolyline = null;
        this.pollingInterval = null;
    }

    init(centerLat = 18.5204, centerLng = 73.8567, zoomLevel = 13) {
        if (!document.getElementById(this.mapId)) return;

        // Initialize Leaflet Map
        this.map = L.map(this.mapId).setView([centerLat, centerLng], zoomLevel);

        // Add OpenStreetMap tile layer (Clean CartoDB voyager style)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        }).addTo(this.map);

        // Custom Truck Icon
        this.truckIcon = L.divIcon({
            className: 'custom-vehicle-marker',
            html: `<div style="background:#1B5E20; color:#fff; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 10px rgba(0,0,0,0.3); border:2px solid #fff;">
                    <i class="fas fa-truck" style="font-size:16px;"></i>
                   </div>`,
            iconSize: [36, 36],
            iconAnchor: [18, 18]
        });

        // Custom Society Building Icon
        this.societyIcon = L.divIcon({
            className: 'custom-society-marker',
            html: `<div style="background:#00BCD4; color:#fff; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 10px rgba(0,0,0,0.25); border:2px solid #fff;">
                    <i class="fas fa-building" style="font-size:14px;"></i>
                   </div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        // Start Live Telemetry Polling (baseline refresh)
        this.fetchVehiclePositions();
        this.pollingInterval = setInterval(() => this.fetchVehiclePositions(), 3000);

        // Also listen for real-time SocketIO push updates so marker moves
        // aren't limited to the 3s polling cadence.
        this.initSocket();
    }

    initSocket() {
        if (typeof io === 'undefined') return;
        try {
            this.socket = io();
            this.socket.on('vehicle_position', (v) => {
                this.updateVehicleMarker(v);
            });
        } catch (err) {
            console.error('SocketIO connection failed, falling back to polling only:', err);
        }
    }

    updateVehicleMarker(v) {
        if (!this.map || !v || v.lat == null || v.lng == null) return;
        const latLng = [v.lat, v.lng];
        const popupHtml = `
            <b>Vehicle: ${v.vehicle_number}</b><br>
            Status: <span class="badge bg-success">${v.status}</span>
        `;
        if (this.vehicleMarkers[v.id]) {
            this.vehicleMarkers[v.id].setLatLng(latLng);
            this.vehicleMarkers[v.id].getPopup()?.setContent(popupHtml);
        } else {
            const marker = L.marker(latLng, { icon: this.truckIcon })
                .addTo(this.map)
                .bindPopup(popupHtml);
            this.vehicleMarkers[v.id] = marker;
        }
    }

    addSociety(id, name, lat, lng, address = '') {
        if (!this.map) return;
        const marker = L.marker([lat, lng], { icon: this.societyIcon })
            .addTo(this.map)
            .bindPopup(`<b>${name}</b><br><small>${address}</small>`);
        this.societyMarkers[id] = marker;

        // Best-effort: also draw the real building footprint outline under
        // the marker, instead of just showing an approximate dot.
        this.drawBuildingFootprint(id, lat, lng, name);
    }

    /**
     * Looks up the actual building polygon at a given rooftop coordinate via
     * OSM Nominatim reverse geocoding (polygon_geojson=1) and draws it as an
     * outlined shape on the map. Falls back to leaving just the marker in
     * place if OSM has no building outline for that point, or the lookup
     * fails - this is always a visual enhancement, never a requirement.
     *
     * Requests are throttled to respect Nominatim's public-instance usage
     * policy of max 1 request/second (https://operations.osmfoundation.org/policies/nominatim/).
     * For a production deployment with many concurrent users, consider
     * self-hosting Nominatim or caching footprints server-side instead of
     * calling the public endpoint from every client.
     */
    drawBuildingFootprint(id, lat, lng, name) {
        LiveTracker._nominatimQueue = (LiveTracker._nominatimQueue || Promise.resolve())
            .then(() => new Promise(resolve => setTimeout(resolve, 1100)))
            .then(() => this._fetchAndDrawFootprint(id, lat, lng, name))
            .catch(err => console.error('Building footprint queue error:', err));
    }

    async _fetchAndDrawFootprint(id, lat, lng, name) {
        try {
            const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}&zoom=18&polygon_geojson=1`;
            const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
            if (!resp.ok || !this.map) return;

            const data = await resp.json();
            const geojson = data && data.geojson;
            if (!geojson || (geojson.type !== 'Polygon' && geojson.type !== 'MultiPolygon')) {
                return; // No real building outline available for this point - keep the marker only.
            }

            const footprint = L.geoJSON(geojson, {
                style: {
                    color: '#00BCD4',
                    weight: 2,
                    fillColor: '#00BCD4',
                    fillOpacity: 0.22
                }
            }).addTo(this.map);
            footprint.bindPopup(`<b>${name}</b><br><small>${data.display_name || 'Building footprint'}</small>`);

            if (this.societyFootprints[id]) {
                this.map.removeLayer(this.societyFootprints[id]);
            }
            this.societyFootprints[id] = footprint;
        } catch (err) {
            console.error('Building footprint unavailable, showing marker only:', err);
        }
    }

    async drawRoute(waypoints) {
        if (!this.map || !waypoints || waypoints.length < 2) return;

        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
            this.routePolyline = null;
        }

        const roadCoords = await this.fetchRoadRoute(waypoints);
        const latLngs = roadCoords || waypoints.map(wp => [wp.lat, wp.lng]);

        this.routePolyline = L.polyline(latLngs, {
            color: '#43A047',
            weight: 5,
            opacity: 0.85,
            dashArray: roadCoords ? null : '8, 8', // dashed = fallback straight line, solid = real road route
            lineJoin: 'round'
        }).addTo(this.map);

        this.map.fitBounds(this.routePolyline.getBounds(), { padding: [40, 40] });
    }

    /**
     * Ask OSRM's public routing API for the actual road-following path between
     * waypoints (instead of a straight line). Returns an array of [lat, lng]
     * pairs on success, or null on any failure so the caller can fall back to
     * a straight line rather than showing nothing.
     */
    async fetchRoadRoute(waypoints) {
        try {
            const coordStr = waypoints.map(wp => `${wp.lng},${wp.lat}`).join(';');
            const url = `https://router.project-osrm.org/route/v1/driving/${coordStr}?overview=full&geometries=geojson`;
            const resp = await fetch(url);
            if (!resp.ok) return null;

            const data = await resp.json();
            if (data.code !== 'Ok' || !data.routes || !data.routes.length) return null;

            // GeoJSON coordinates are [lng, lat] - Leaflet wants [lat, lng]
            return data.routes[0].geometry.coordinates.map(([lng, lat]) => [lat, lng]);
        } catch (err) {
            console.error('Road routing unavailable, falling back to straight line:', err);
            return null;
        }
    }

    async fetchVehiclePositions() {
        try {
            const resp = await fetch('/api/vehicles/gps');
            const data = await resp.json();

            if (data && data.vehicles) {
                data.vehicles.forEach(v => {
                    const latLng = [v.lat, v.lng];

                    if (this.vehicleMarkers[v.id]) {
                        // Smoothly move marker
                        this.vehicleMarkers[v.id].setLatLng(latLng);
                        this.vehicleMarkers[v.id].getPopup().setContent(`
                            <b>Vehicle: ${v.vehicle_number}</b><br>
                            Type: ${v.vehicle_type}<br>
                            Status: <span class="badge bg-success">${v.status}</span><br>
                            Driver: ${v.driver}
                        `);
                    } else {
                        // Create marker
                        const marker = L.marker(latLng, { icon: this.truckIcon })
                            .addTo(this.map)
                            .bindPopup(`
                                <b>Vehicle: ${v.vehicle_number}</b><br>
                                Type: ${v.vehicle_type}<br>
                                Status: <span class="badge bg-success">${v.status}</span><br>
                                Driver: ${v.driver}
                            `);
                        this.vehicleMarkers[v.id] = marker;
                    }
                });
            }
        } catch (err) {
            console.error('Error fetching live GPS:', err);
        }
    }
}
