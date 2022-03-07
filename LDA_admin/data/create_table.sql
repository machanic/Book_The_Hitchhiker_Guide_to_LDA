/*
SQLyog Ultimate v11.24 (32 bit)
MySQL - 5.1.26-rc : Database - topic_model
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`topic_model_machen` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;

USE `topic_model_machen`;

/*Table structure for table `django_migrations` */

DROP TABLE IF EXISTS `django_migrations`;

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8_bin NOT NULL,
  `name` varchar(255) COLLATE utf8_bin NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topic_doc` */

DROP TABLE IF EXISTS `topic_doc`;

CREATE TABLE `topic_doc` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(250) COLLATE utf8_bin NOT NULL,
  `score` float NOT NULL,
  `title` varchar(250) COLLATE utf8_bin DEFAULT NULL,
  `stock` varchar(250) COLLATE utf8_bin DEFAULT NULL,
  `content` longtext COLLATE utf8_bin,
  PRIMARY KEY (`id`),
  UNIQUE KEY `DOC_URL` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=14781 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topic_id` */

DROP TABLE IF EXISTS `topic_id`;

CREATE TABLE `topic_id` (
  `id` int(11) unsigned NOT NULL,
  `topic_label_id` int(10) unsigned DEFAULT NULL,
  `update_time` datetime NOT NULL,
  `abstract` text COLLATE utf8_bin,
  PRIMARY KEY (`id`),
  KEY `TOPIC_LABEL_ID` (`topic_label_id`),
  CONSTRAINT `TOPIC_LABEL_ID` FOREIGN KEY (`topic_label_id`) REFERENCES `topic_label` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topic_label` */

DROP TABLE IF EXISTS `topic_label`;

CREATE TABLE `topic_label` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `label_name` varchar(10) COLLATE utf8_bin NOT NULL,
  `min_len` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `LABEL_NAME` (`label_name`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topic_label_word` */

DROP TABLE IF EXISTS `topic_label_word`;

CREATE TABLE `topic_label_word` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `word` char(10) COLLATE utf8_bin NOT NULL,
  `word_type` tinyint(1) NOT NULL COMMENT '0:typical word,1:extracted word',
  `label_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LABEL_ID` (`label_id`),
  CONSTRAINT `LABEL_ID` FOREIGN KEY (`label_id`) REFERENCES `topic_label` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1030 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topic_word` */

DROP TABLE IF EXISTS `topic_word`;

CREATE TABLE `topic_word` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `word` varchar(10) COLLATE utf8_bin NOT NULL,
  `topic_id` int(11) unsigned NOT NULL,
  `is_essential` tinyint(1) NOT NULL COMMENT '是否为必须词',
  PRIMARY KEY (`id`),
  KEY `TOPIC_ID_ID` (`topic_id`),
  CONSTRAINT `TOPIC_ID_ID` FOREIGN KEY (`topic_id`) REFERENCES `topic_id` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=116720 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*Table structure for table `topicid_doc` */

DROP TABLE IF EXISTS `topicid_doc`;

CREATE TABLE `topicid_doc` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `topic_id` int(11) unsigned NOT NULL,
  `topic_doc_id` int(10) unsigned NOT NULL,
  `series_number` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `TOPIC_ID` (`topic_id`),
  KEY `TOPIC_DOC_ID` (`topic_doc_id`),
  CONSTRAINT `TOPIC_DOC_ID` FOREIGN KEY (`topic_doc_id`) REFERENCES `topic_doc` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `TOPIC_ID` FOREIGN KEY (`topic_id`) REFERENCES `topic_id` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29808 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
