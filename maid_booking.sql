-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 03, 2023 at 01:57 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `maid_booking`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(11) NOT NULL,
  `admin_username` varchar(50) NOT NULL,
  `admin_password` varchar(255) NOT NULL,
  `admin_email` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`admin_id`, `admin_username`, `admin_password`, `admin_email`) VALUES
(1, 'jx', '123', 'ngjunxuan1120@gmail.com');

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

CREATE TABLE `booking` (
  `booking_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `maid_id` int(11) NOT NULL,
  `booking_date_time` datetime NOT NULL,
  `booking_status` varchar(20) NOT NULL,
  `booking_arrive_time` datetime DEFAULT NULL,
  `booking_address` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking`
--

INSERT INTO `booking` (`booking_id`, `service_id`, `member_id`, `maid_id`, `booking_date_time`, `booking_status`, `booking_arrive_time`, `booking_address`) VALUES
(1, 0, 1, 2, '2022-03-24 15:30:00', 'pending', '2022-03-28 15:30:00', 'abc');

-- --------------------------------------------------------

--
-- Table structure for table `maid`
--

CREATE TABLE `maid` (
  `maid_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `age` int(11) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `experience` varchar(255) NOT NULL,
  `availability_start` date NOT NULL,
  `availability_end` date NOT NULL,
  `skill` varchar(255) NOT NULL,
  `maid_email` varchar(255) NOT NULL,
  `maid_password` varchar(20) NOT NULL,
  `image_file_path` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `maid`
--

INSERT INTO `maid` (`maid_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `availability_end`, `skill`, `maid_email`, `maid_password`, `image_file_path`) VALUES
(2, 'Maid A', 23, 'Female', '0123456789', '123 Main St, City, State', '3 years', '0000-00-00', '0000-00-00', 'Cooking, Cleaning', 'maidA@example.com', 'password123', 'uploads/maids/55.jpg'),
(3, 'Maid B', 30, 'Female', '0123456789', '456 Main St, City, State', '5 years', '0000-00-00', '0000-00-00', 'Cooking, Cleaning, Laundry', 'maidB@example.com', 'password123', 'uploads/maids/56.jpg'),
(4, 'Maid C', 27, 'Male', '0123456789', '789 Main St, City, State', '2 years', '0000-00-00', '0000-00-00', 'Babysitting, Cooking', 'maidC@example.com', 'password123', 'uploads/maids/57.jpg'),
(5, 'Maid D', 25, 'Female', '0123456789', '246 Main St, City, State', '4 years', '0000-00-00', '0000-00-00', 'Cooking, Cleaning, Gardening', 'maidD@example.com', 'password123', 'uploads/maids/58.jpg'),
(6, 'Maid E', 29, 'Male', '0123456789', '135 Main St, City, State', '1 year', '0000-00-00', '0000-00-00', 'Cleaning, Laundry, Ironing', 'maidE@example.com', 'password123', 'uploads/maids/59.jpg'),
(8, 'NG JUN XUAN', 1, 'male', '0123456789', 'no 11', '1', '0000-00-00', '0000-00-00', 's', 'ngjunxuan1120@gmail.com', '12', 'uploads/8.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `maid_application`
--

CREATE TABLE `maid_application` (
  `application_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `age` int(11) NOT NULL,
  `gender` enum('male','female') NOT NULL,
  `contact` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `experience` text NOT NULL,
  `availability_start` time NOT NULL,
  `availability_end` time NOT NULL,
  `skill` text NOT NULL,
  `email` varchar(255) NOT NULL,
  `background_check_status` varchar(10) NOT NULL,
  `image_file_path` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `maid_application`
--

INSERT INTO `maid_application` (`application_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `availability_end`, `skill`, `email`, `background_check_status`, `image_file_path`) VALUES
(8, 'NG JUN XUAN', 1, 'male', '0123456789', 'no 11', '1', '06:00:00', '14:00:00', 's', 'ngjunxuan1120@gmail.com', 'Approved', 'uploads/8.jpg'),
(9, 'jx', 1, 'male', '0123456789', '159', '1', '06:00:00', '14:00:00', 's', 'ngjunxuan1120@gmail.com', 'pending', 'uploads/9.jpg'),
(10, 'jx', 1, 'male', '0123456789', '123', '1', '06:00:00', '14:00:00', 's', 'ngjunxuan1120@gmail.com', 'pending', 'uploads/10.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `member`
--

CREATE TABLE `member` (
  `member_id` int(11) NOT NULL,
  `member_username` varchar(255) NOT NULL,
  `member_email` varchar(255) NOT NULL,
  `member_contact` varchar(20) NOT NULL,
  `member_address` text NOT NULL,
  `member_image_file_path` varchar(255) DEFAULT NULL,
  `member_password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `member`
--

INSERT INTO `member` (`member_id`, `member_username`, `member_email`, `member_contact`, `member_address`, `member_image_file_path`, `member_password`) VALUES
(1, 'NG JUN XUAN', 'ngjunxuan1120@gmail.com', '0123456789', '', NULL, '1');

-- --------------------------------------------------------

--
-- Table structure for table `rating`
--

CREATE TABLE `rating` (
  `rating_id` int(11) NOT NULL,
  `maid_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `rating_score` int(11) NOT NULL,
  `comment` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rating`
--

INSERT INTO `rating` (`rating_id`, `maid_id`, `member_id`, `rating_score`, `comment`) VALUES
(1, 5, 1, 4, 'Great job, very satisfied with the service.'),
(2, 3, 1, 3, 'Could have been better, but overall okay.'),
(3, 2, 1, 5, 'Excellent service, highly recommended.'),
(4, 4, 1, 2, 'Disappointing experience, will not use again.'),
(6, 2, 1, 4, 'The maid did a great job cleaning the kitchen and bathroom. Very thorough and efficient.'),
(7, 2, 3, 3, 'The maid was okay. They did the job, but missed a few spots. Could have been better.'),
(8, 2, 4, 5, 'Excellent service! The maid was friendly, professional, and went above and beyond to make sure our home was spotless.');

-- --------------------------------------------------------

--
-- Table structure for table `service`
--

CREATE TABLE `service` (
  `service_id` int(10) NOT NULL,
  `service_type` varchar(30) NOT NULL,
  `service_title` varchar(30) NOT NULL,
  `service_description` varchar(100) NOT NULL,
  `image_file_path` varchar(35) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `service`
--

INSERT INTO `service` (`service_id`, `service_type`, `service_title`, `service_description`, `image_file_path`) VALUES
(1, 'Cleaning', 'House Cleaning', 'A thorough cleaning of your home from top to bottom.', ''),
(2, 'Landscaping', 'Lawn Care', 'Mowing, trimming, and other lawn maintenance services.', ''),
(3, 'Home Repair', 'Handyman Services', 'Minor home repairs and installations.', ''),
(4, 'Cleaning', 'Basic Office Cleaning', 'Includes basic cleaning of floors, surfaces, and bathrooms.', ''),
(5, 'Baby Care', 'Basic Baby Care Package', 'Includes feeding, bathing, and diaper changing', ''),
(6, 'Gardening', 'Gardening Service', 'Our gardening service includes lawn mowing, hedge trimming, weeding, and more.', 'uploads/service/gardening.jfif');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `admin_username` (`admin_username`);

--
-- Indexes for table `booking`
--
ALTER TABLE `booking`
  ADD PRIMARY KEY (`booking_id`);

--
-- Indexes for table `maid`
--
ALTER TABLE `maid`
  ADD PRIMARY KEY (`maid_id`);

--
-- Indexes for table `maid_application`
--
ALTER TABLE `maid_application`
  ADD PRIMARY KEY (`application_id`);

--
-- Indexes for table `member`
--
ALTER TABLE `member`
  ADD PRIMARY KEY (`member_id`);

--
-- Indexes for table `rating`
--
ALTER TABLE `rating`
  ADD PRIMARY KEY (`rating_id`);

--
-- Indexes for table `service`
--
ALTER TABLE `service`
  ADD PRIMARY KEY (`service_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `booking`
--
ALTER TABLE `booking`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `maid`
--
ALTER TABLE `maid`
  MODIFY `maid_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `maid_application`
--
ALTER TABLE `maid_application`
  MODIFY `application_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `member`
--
ALTER TABLE `member`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `rating`
--
ALTER TABLE `rating`
  MODIFY `rating_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `service`
--
ALTER TABLE `service`
  MODIFY `service_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
