-- Use the mysql application dba user for this script
use db_damg7245team7;

CREATE TABLE IF NOT EXISTS `ApplicationLog` (
  `Application_LogId` int NOT NULL AUTO_INCREMENT,
  `Application_LogCorrelationID` varchar(255) DEFAULT NULL,
  `Application_Component` varchar(255) DEFAULT NULL,
  `Application_LogStatus` varchar(255) DEFAULT NULL,
  `Application_LogDetails` varchar(2000) DEFAULT NULL,
  `created_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Application_LogId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `usercredentials` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `user_salt` varbinary(16) NOT NULL,
  `user_hashpassword` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `created_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_datetime` datetime DEFAULT NULL,
  `lastlogin_datetime` datetime DEFAULT NULL,
  `active` bit(1) NOT NULL DEFAULT b'1',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `chathistory` (
  `chat_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_question` longtext NOT NULL,
  `system_answer` longtext NOT NULL,
  `created_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`chat_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `chathistory_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `usercredentials` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `vectordatabasestats` (
  `form_name` varchar(100) NOT NULL,
  `recent_activity` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`form_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

