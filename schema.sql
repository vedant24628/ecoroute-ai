-- =========================================================
-- EcoRoute AI - Smart Society Waste Management System Schema
-- Database: ecoroute_db
-- Engine: InnoDB
-- =========================================================

CREATE DATABASE IF NOT EXISTS `ecoroute_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ecoroute_db`;

-- 1. System Settings Table
CREATE TABLE IF NOT EXISTS `system_settings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `setting_key` VARCHAR(100) UNIQUE NOT NULL,
  `setting_value` TEXT,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Waste Categories Table
CREATE TABLE IF NOT EXISTS `waste_categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) UNIQUE NOT NULL,
  `description` TEXT,
  `color_code` VARCHAR(20) DEFAULT '#43A047',
  `recyclable_rate` DECIMAL(5,2) DEFAULT 0.00, -- percentage recyclable
  `co2_factor` DECIMAL(5,2) DEFAULT 1.50, -- kg CO2 saved per kg recycled
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Admin Table
CREATE TABLE IF NOT EXISTS `admins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20),
  `role` VARCHAR(50) DEFAULT 'SUPER_ADMIN',
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Societies Table
CREATE TABLE IF NOT EXISTS `societies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `society_name` VARCHAR(150) NOT NULL,
  `registration_number` VARCHAR(100) UNIQUE NOT NULL,
  `secretary_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) UNIQUE NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `address` TEXT NOT NULL,
  `landmark` VARCHAR(150),
  `city` VARCHAR(100) NOT NULL,
  `state` VARCHAR(100) NOT NULL,
  `pin_code` VARCHAR(10) NOT NULL,
  `latitude` DECIMAL(10,8) NOT NULL,
  `longitude` DECIMAL(11,8) NOT NULL,
  `num_buildings` INT DEFAULT 1,
  `num_wings` INT DEFAULT 1,
  `num_flats` INT DEFAULT 10,
  `total_residents` INT DEFAULT 40,
  `estimated_daily_waste` DECIMAL(8,2) DEFAULT 50.00, -- in kg
  `preferred_pickup_time` VARCHAR(50) DEFAULT '08:00 AM - 10:00 AM',
  `photo` VARCHAR(255) DEFAULT 'default_society.jpg',
  `status` ENUM('PENDING', 'APPROVED', 'SUSPENDED') DEFAULT 'APPROVED',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Drivers Table
CREATE TABLE IF NOT EXISTS `drivers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL,
  `license_number` VARCHAR(50) UNIQUE NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL,
  `email` VARCHAR(120) UNIQUE,
  `status` ENUM('AVAILABLE', 'ON_DUTY', 'OFF_DUTY') DEFAULT 'AVAILABLE',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. Workers Table
CREATE TABLE IF NOT EXISTS `workers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL,
  `employee_id` VARCHAR(50) UNIQUE NOT NULL,
  `address` TEXT,
  `status` ENUM('AVAILABLE', 'ASSIGNED', 'ON_LEAVE', 'OFFLINE') DEFAULT 'AVAILABLE',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 7. Vehicles Table
CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `vehicle_number` VARCHAR(50) UNIQUE NOT NULL,
  `vehicle_type` VARCHAR(50) NOT NULL, -- e.g., Electric Truck, Hydraulic Tipper, Mini Van
  `capacity_kg` DECIMAL(8,2) NOT NULL,
  `driver_id` INT,
  `worker_id` INT,
  `gps_device_id` VARCHAR(100) UNIQUE,
  `current_lat` DECIMAL(10,8) DEFAULT 18.5204,
  `current_lng` DECIMAL(11,8) DEFAULT 73.8567,
  `status` ENUM('Available', 'Assigned', 'On Route', 'Collecting', 'Maintenance', 'Offline') DEFAULT 'Available',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`driver_id`) REFERENCES `drivers`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`worker_id`) REFERENCES `workers`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. Pickup Requests Table
CREATE TABLE IF NOT EXISTS `pickup_requests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `society_id` INT NOT NULL,
  `request_code` VARCHAR(50) UNIQUE NOT NULL,
  `scheduled_date` DATE NOT NULL,
  `preferred_slot` VARCHAR(50) NOT NULL,
  `estimated_weight` DECIMAL(8,2) DEFAULT 0.00,
  `notes` TEXT,
  `status` ENUM('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING',
  `urgency_level` ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`society_id`) REFERENCES `societies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Assignments Table
CREATE TABLE IF NOT EXISTS `assignments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `pickup_request_id` INT UNIQUE NOT NULL,
  `vehicle_id` INT NOT NULL,
  `worker_id` INT NOT NULL,
  `driver_id` INT,
  `assigned_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `optimized_sequence` INT DEFAULT 1,
  `estimated_eta_minutes` INT DEFAULT 15,
  `status` ENUM('DISPATCHED', 'EN_ROUTE', 'ARRIVED', 'COMPLETED') DEFAULT 'DISPATCHED',
  FOREIGN KEY (`pickup_request_id`) REFERENCES `pickup_requests`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`worker_id`) REFERENCES `workers`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`driver_id`) REFERENCES `drivers`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 10. Collections Table
CREATE TABLE IF NOT EXISTS `collections` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `assignment_id` INT UNIQUE NOT NULL,
  `society_id` INT NOT NULL,
  `worker_id` INT NOT NULL,
  `vehicle_id` INT NOT NULL,
  `total_weight_kg` DECIMAL(8,2) NOT NULL DEFAULT 0.00,
  `wet_waste_kg` DECIMAL(8,2) DEFAULT 0.00,
  `dry_waste_kg` DECIMAL(8,2) DEFAULT 0.00,
  `recyclable_kg` DECIMAL(8,2) DEFAULT 0.00,
  `hazardous_kg` DECIMAL(8,2) DEFAULT 0.00,
  `image_proof` VARCHAR(255),
  `remarks` TEXT,
  `collected_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`assignment_id`) REFERENCES `assignments`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`society_id`) REFERENCES `societies`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`worker_id`) REFERENCES `workers`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Waste Processing & Recycling Table
CREATE TABLE IF NOT EXISTS `waste_processing` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `collection_id` INT UNIQUE NOT NULL,
  `composted_kg` DECIMAL(8,2) DEFAULT 0.00,
  `recycled_plastic_kg` DECIMAL(8,2) DEFAULT 0.00,
  `recycled_paper_kg` DECIMAL(8,2) DEFAULT 0.00,
  `recycled_metal_kg` DECIMAL(8,2) DEFAULT 0.00,
  `landfill_kg` DECIMAL(8,2) DEFAULT 0.00,
  `co2_saved_kg` DECIMAL(8,2) DEFAULT 0.00,
  `processed_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`collection_id`) REFERENCES `collections`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. GPS Locations Table
CREATE TABLE IF NOT EXISTS `gps_locations` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `vehicle_id` INT NOT NULL,
  `latitude` DECIMAL(10,8) NOT NULL,
  `longitude` DECIMAL(11,8) NOT NULL,
  `speed_kmh` DECIMAL(5,2) DEFAULT 0.00,
  `heading` DECIMAL(5,2) DEFAULT 0.00,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 13. Route History Table
CREATE TABLE IF NOT EXISTS `route_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `assignment_id` INT NOT NULL,
  `vehicle_id` INT NOT NULL,
  `start_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `end_time` DATETIME,
  `total_distance_km` DECIMAL(6,2) DEFAULT 0.00,
  `route_geometry_json` LONGTEXT,
  FOREIGN KEY (`assignment_id`) REFERENCES `assignments`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 14. Notifications Table
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_type` ENUM('ADMIN', 'SOCIETY', 'WORKER') NOT NULL,
  `user_id` INT NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `message` TEXT NOT NULL,
  `is_read` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 15. Activity Log Table
CREATE TABLE IF NOT EXISTS `activity_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `actor_type` VARCHAR(50) NOT NULL,
  `actor_id` INT NOT NULL,
  `action` VARCHAR(100) NOT NULL,
  `details` TEXT,
  `ip_address` VARCHAR(45),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Indexes for performance
CREATE INDEX idx_vehicle_status ON vehicles(status);
CREATE INDEX idx_pickup_status ON pickup_requests(status);
CREATE INDEX idx_pickup_date ON pickup_requests(scheduled_date);
CREATE INDEX idx_gps_vehicle ON gps_locations(vehicle_id, timestamp);
CREATE INDEX idx_collections_date ON collections(collected_at);

-- Initial System Settings Seed
INSERT INTO `system_settings` (`setting_key`, `setting_value`) VALUES
('site_name', 'EcoRoute AI'),
('co2_conversion_rate', '1.85'),
('default_currency', 'INR'),
('route_optimization_mode', 'DYNAMIC_TRAFFIC_AWARE')
ON DUPLICATE KEY UPDATE `setting_value` = VALUES(`setting_value`);

-- Initial Waste Categories Seed
INSERT INTO `waste_categories` (`name`, `description`, `color_code`, `recyclable_rate`, `co2_factor`) VALUES
('Organic / Wet Waste', 'Food scraps, kitchen waste, garden waste suitable for bio-composting.', '#2E7D32', 95.00, 1.80),
('Dry & Paper Waste', 'Paper, cardboard boxes, dry leaves, packaging materials.', '#43A047', 90.00, 1.50),
('Recyclable Plastic', 'PET bottles, HDPE containers, plastic covers, bags.', '#00BCD4', 85.00, 2.10),
('Glass & Metal', 'Glass bottles, aluminum cans, scrap metal.', '#0288D1', 98.00, 2.50),
('E-Waste', 'Old electronics, cables, batteries, circuit boards.', '#FB8C00', 70.00, 3.20),
('Hazardous Waste', 'Chemicals, paints, fluorescent lamps, medical waste.', '#D32F2F', 40.00, 4.00);
