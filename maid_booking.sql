-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: maid_booking
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `admin_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `admin_password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `admin_email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `admin_username` (`admin_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'admin','123','admin');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `service_id` int NOT NULL,
  `member_id` int NOT NULL,
  `maid_id` int NOT NULL,
  `booking_datetime` datetime NOT NULL,
  `booking_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `booking_arrive_datetime` datetime DEFAULT NULL,
  `booking_address` text COLLATE utf8mb4_general_ci NOT NULL,
  `booking_leave_datetime` datetime NOT NULL,
  PRIMARY KEY (`booking_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,1,1,2,'2023-05-04 14:05:05','pending','2023-05-28 14:00:00','abc','2023-05-28 15:00:00'),(11,5,1,3,'2023-05-31 14:40:00','pending','2023-06-03 12:00:00','efg','2023-06-03 14:00:00');
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favourite_list`
--

DROP TABLE IF EXISTS `favourite_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favourite_list` (
  `member_id` int DEFAULT NULL,
  `maid_id` int DEFAULT NULL,
  `fav_id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`fav_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favourite_list`
--

LOCK TABLES `favourite_list` WRITE;
/*!40000 ALTER TABLE `favourite_list` DISABLE KEYS */;
INSERT INTO `favourite_list` VALUES (1,2,1),(1,3,2);
/*!40000 ALTER TABLE `favourite_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maid`
--

DROP TABLE IF EXISTS `maid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maid` (
  `maid_id` int NOT NULL AUTO_INCREMENT,
  `maid_age` int NOT NULL,
  `maid_gender` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `maid_experience` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `availability_start` time DEFAULT NULL,
  `availability_end` time DEFAULT NULL,
  `maid_skill` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `member_id` int NOT NULL,
  `maid_background_check_status` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`maid_id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `maid_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maid`
--

LOCK TABLES `maid` WRITE;
/*!40000 ALTER TABLE `maid` DISABLE KEYS */;
INSERT INTO `maid` VALUES (9,25,'Female','3 years','09:00:00','17:00:00','Cleaning, Cooking',1,'Approved'),(10,28,'Male','5 years','08:30:00','16:30:00','Childcare, Laundry',2,'Approved'),(11,30,'Female','7 years','10:00:00','18:00:00','Elderly Care, Errands',3,'Rejected'),(12,22,'Female','2 years','09:30:00','17:30:00','Pet Care, Gardening',4,'Pending'),(13,27,'Male','4 years','08:00:00','16:00:00','Housekeeping, Organizing',5,'Approved'),(14,26,'Male','4 years','09:00:00','18:00:00','Cleaning, Cooking',21,'Approved');
/*!40000 ALTER TABLE `maid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `member_id` int NOT NULL AUTO_INCREMENT,
  `member_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `member_email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `member_contact` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `member_address` text COLLATE utf8mb4_general_ci NOT NULL,
  `member_image` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `member_password` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`member_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
INSERT INTO `member` VALUES (1,'John Doe','john.doe@example.com','1234567890','123 Main St','uploads/members/1.jpg','password1'),(2,'Jane Smith','jane.smith@example.com','9876543210','456 Elm St','uploads/members/2.jpg','password2'),(3,'Michael Johnson','michael.johnson@example.com','5551234567','789 Oak St','uploads/members/3.jpg','password3'),(4,'Emily Davis','emily.davis@example.com','9876543210','321 Maple Ave','uploads/members/4.jpg','password4'),(5,'David Wilson','david.wilson@example.com','1234567890','456 Pine Rd','uploads/members/5.jpg','password5'),(6,'Olivia Thompson','olivia.thompson@example.com','5551234567','789 Cedar Ln','uploads/members/6.jpg','password6'),(7,'James Anderson','james.anderson@example.com','9876543210','123 Oak St','uploads/members/7.jpg','password7'),(8,'Emma Garcia','emma.garcia@example.com','1234567890','456 Elm St','uploads/members/8.jpg','password8'),(9,'John Doe','john.doe@example.com','1234567890','123 Main St','uploads/members/9.jpg','password9'),(10,'Sophia Robinson','sophia.robinson@example.com','9876543210','321 Cedar Ln','uploads/members/10.jpg','password10'),(11,'Daniel Rodriguez','daniel.rodriguez@example.com','1234567890','123 Maple Ave','uploads/members/11.jpg','password11'),(12,'Isabella Thompson','isabella.thompson@example.com','5551234567','456 Oak St','uploads/members/12.jpg','password12'),(13,'Alexander Lee','alexander.lee@example.com','9876543210','789 Elm St','uploads/members/13.jpg','password13'),(14,'Mia Walker','mia.walker@example.com','1234567890','321 Pine Rd','uploads/members/14.jpg','password14'),(15,'Ethan Hall','ethan.hall@example.com','5551234567','123 Cedar Ln','uploads/members/15.jpg','password15'),(16,'Ava Young','ava.young@example.com','9876543210','456 Maple Ave','uploads/members/16.jpg','password16'),(17,'Matthew Hernandez','matthew.hernandez@example.com','1234567890','789 Oak St','uploads/members/17.jpg','password17'),(18,'Charlotte King','charlotte.king@example.com','5551234567','321 Elm St','uploads/members/18.jpg','password18'),(19,'Joseph Allen','joseph.allen@example.com','9876543210','123 Pine Rd','uploads/members/19.jpg','password19'),(20,'Harper Wright','harper.wright@example.com','1234567890','456 Cedar Ln','uploads/members/20.jpg','password20'),(21,'maid','maid','1234567890','124 Main St','uploads/members/21.jpg','12'),(22,'member','member','1234567890','123 Main St','uploads/members/22.jpg','1');
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `payment_type` varchar(255) DEFAULT NULL,
  `payment_price` decimal(10,0) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `booking_id` int DEFAULT NULL,
  PRIMARY KEY (`payment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rating`
--

DROP TABLE IF EXISTS `rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rating` (
  `rating_id` int NOT NULL AUTO_INCREMENT,
  `maid_id` int NOT NULL,
  `member_id` int NOT NULL,
  `rating_score` int NOT NULL,
  `comment` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`rating_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rating`
--

LOCK TABLES `rating` WRITE;
/*!40000 ALTER TABLE `rating` DISABLE KEYS */;
INSERT INTO `rating` VALUES (1,5,1,4,'Great job, very satisfied with the service.'),(2,3,1,3,'Could have been better, but overall okay.'),(3,2,1,5,'Excellent service, highly recommended.'),(4,4,1,2,'Disappointing experience, will not use again.'),(6,2,1,4,'The maid did a great job cleaning the kitchen and bathroom. Very thorough and efficient.'),(7,2,3,3,'The maid was okay. They did the job, but missed a few spots. Could have been better.'),(8,2,4,5,'Excellent service! The maid was friendly, professional, and went above and beyond to make sure our home was spotless.');
/*!40000 ALTER TABLE `rating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `service_type` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `service_title` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `service_description` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `service_image` varchar(35) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES (1,'Cleaning','House Cleaning','A thorough cleaning of your home from top to bottom.','uploads/service/house-clean1.jpg'),(4,'Cleaning','Basic Office Cleaning','Includes basic cleaning of floors, surfaces, and bathrooms.','uploads/service/office-clean.jpg'),(5,'Baby Care','Basic Baby Care Package','Includes feeding, bathing, and diaper changing','uploads/service/baby-care2.jpg'),(6,'Gardening','Gardening Service','Our gardening service includes lawn mowing, hedge trimming, weeding, and more.','uploads/service/gardening2.jpg');
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-04 20:30:47
