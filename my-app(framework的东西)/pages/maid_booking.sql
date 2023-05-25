-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2023-03-28 06:31:23
-- 服务器版本： 10.4.27-MariaDB
-- PHP 版本： 8.0.25

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
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `PASSWORD` varchar(16) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `phone_num` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `admin`
--

INSERT INTO `admin` (`id`, `name`, `PASSWORD`, `email`, `age`, `phone_num`) VALUES
(1, 'Janadmine', NULL, 'jane@example.com', 25, '123456789');

-- --------------------------------------------------------

--
-- 表的结构 `maid`
--

CREATE TABLE `maid` (
  `maid_id` int(10) NOT NULL,
  `application_id` int(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  `age` int(2) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `address` varchar(100) NOT NULL,
  `experience` int(2) NOT NULL,
  `availability_start` varchar(5) NOT NULL,
  `availability_end` varchar(5) NOT NULL,
  `skill` varchar(50) NOT NULL,
  `image_file_path` varchar(35) NOT NULL,
  `email` varchar(30) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `maid`
--

INSERT INTO `maid` (`maid_id`, `application_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `availability_end`, `skill`, `image_file_path`, `email`, `password`) VALUES
(0, 0, '', 0, '', '', '', 0, '', '', '', '', '', '');

-- --------------------------------------------------------

--
-- 表的结构 `maid_application`
--

CREATE TABLE `maid_application` (
  `application_id` int(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  `age` int(3) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `address` varchar(100) NOT NULL,
  `experience` varchar(20) NOT NULL,
  `availability_start` varchar(5) NOT NULL,
  `skill` varchar(50) NOT NULL,
  `availability_end` varchar(5) NOT NULL,
  `background_check_status` varchar(10) NOT NULL,
  `image_file_path` varchar(35) NOT NULL,
  `email` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `maid_application`
--

INSERT INTO `maid_application` (`application_id`, `name`, `age`, `gender`, `contact`, `address`, `experience`, `availability_start`, `skill`, `availability_end`, `background_check_status`, `image_file_path`, `email`) VALUES
(0, '&#31459;&#36713;', 1, 'Male', '0123456789', 'a', '1', '6am', 'a', '2pm', 'Approved', '', '');

-- --------------------------------------------------------

--
-- 表的结构 `user`
--

CREATE TABLE `user` (
  `user_id` int(10) NOT NULL,
  `first_name` varchar(20) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contact` int(15) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `user`
--

INSERT INTO `user` (`user_id`, `first_name`, `email`, `contact`, `last_name`, `password`) VALUES
(0, 'NG', 'ngjunxuan1120@gmail.com', 123456789, 'XUAN', '12345678');

--
-- 转储表的索引
--

--
-- 表的索引 `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `maid`
--
ALTER TABLE `maid`
  ADD PRIMARY KEY (`maid_id`),
  ADD KEY `FK_app_id` (`application_id`);

--
-- 表的索引 `maid_application`
--
ALTER TABLE `maid_application`
  ADD PRIMARY KEY (`application_id`);

--
-- 表的索引 `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 限制导出的表
--

--
-- 限制表 `maid`
--
ALTER TABLE `maid`
  ADD CONSTRAINT `FK_app_id` FOREIGN KEY (`application_id`) REFERENCES `maid_application` (`application_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
