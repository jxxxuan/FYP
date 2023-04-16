-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2023-04-16 05:57:51
-- 服务器版本： 10.4.28-MariaDB
-- PHP 版本： 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `maid_booking`
--

-- --------------------------------------------------------

--
-- 表的结构 `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(11) NOT NULL,
  `admin_username` varchar(50) NOT NULL,
  `admin_password` varchar(255) NOT NULL,
  `admin_email` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `admin`
--

INSERT INTO `admin` (`admin_id`, `admin_username`, `admin_password`, `admin_email`) VALUES
(1, 'jx', '123', 'ngjunxuan1120@gmail.com');

-- --------------------------------------------------------

--
-- 表的结构 `booking`
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

-- --------------------------------------------------------

--
-- 表的结构 `maid`
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
  `maid_email` varchar(255) DEFAULT NULL,
  `maid_password` varchar(20) NOT NULL,
  `image_file_path` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `maid`
--

INSERT INTO `maid` (`maid_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `availability_end`, `skill`, `maid_email`, `maid_password`, `image_file_path`) VALUES
(1, 'NG JUN XUAN', 1, 'male', '0123456789', 'no 11', '1', '0000-00-00', '0000-00-00', 's', 'ngjunxuan1120@gmail.com', '12', 'uploads/8.jpg');

-- --------------------------------------------------------

--
-- 表的结构 `maid_application`
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
-- 转存表中的数据 `maid_application`
--

INSERT INTO `maid_application` (`application_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `availability_end`, `skill`, `email`, `background_check_status`, `image_file_path`) VALUES
(8, 'NG JUN XUAN', 1, 'male', '0123456789', 'no 11', '1', '06:00:00', '14:00:00', 's', 'ngjunxuan1120@gmail.com', 'Approved', 'uploads/8.jpg');

-- --------------------------------------------------------

--
-- 表的结构 `member`
--

CREATE TABLE `member` (
  `member_id` int(11) NOT NULL,
  `member_username` varchar(255) NOT NULL,
  `member_email` varchar(255) NOT NULL,
  `member_contact` varchar(20) NOT NULL,
  `member_address` text NOT NULL,
  `member_image_file_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 表的结构 `service`
--

CREATE TABLE `service` (
  `service_id` int(10) NOT NULL,
  `service_type` varchar(30) NOT NULL,
  `service_title` varchar(30) NOT NULL,
  `service_description` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转储表的索引
--

--
-- 表的索引 `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `admin_username` (`admin_username`);

--
-- 表的索引 `booking`
--
ALTER TABLE `booking`
  ADD PRIMARY KEY (`booking_id`);

--
-- 表的索引 `maid`
--
ALTER TABLE `maid`
  ADD PRIMARY KEY (`maid_id`);

--
-- 表的索引 `maid_application`
--
ALTER TABLE `maid_application`
  ADD PRIMARY KEY (`application_id`);

--
-- 表的索引 `member`
--
ALTER TABLE `member`
  ADD PRIMARY KEY (`member_id`);

--
-- 表的索引 `service`
--
ALTER TABLE `service`
  ADD PRIMARY KEY (`service_id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `admin`
--
ALTER TABLE `admin`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `booking`
--
ALTER TABLE `booking`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `maid`
--
ALTER TABLE `maid`
  MODIFY `maid_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `maid_application`
--
ALTER TABLE `maid_application`
  MODIFY `application_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- 使用表AUTO_INCREMENT `member`
--
ALTER TABLE `member`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `service`
--
ALTER TABLE `service`
  MODIFY `service_id` int(10) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
