CREATE DATABASE  IF NOT EXISTS `dbintellectlink`;
USE `dbintellectlink`;

SET foreign_key_checks = 0;

-- Table: click_count_table
DROP TABLE IF EXISTS click_count_table;
CREATE TABLE click_count_table (
  paper_id int NOT NULL,
  click_count int DEFAULT '0',
  PRIMARY KEY (paper_id),
  CONSTRAINT fk_click_count_paper_id FOREIGN KEY (paper_id) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- NEWLY ADDED TABLE AND DATA--
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `adminID` int NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL
);

INSERT INTO `admin` (`adminID`, `username`, `password`) VALUES
('1', 'admin','1234');


-- Table: journal
DROP TABLE IF EXISTS journal;
CREATE TABLE journal (
  personId int NOT NULL,
  paperId int NOT NULL,
  pub_date date NOT NULL,
  KEY personId_idx (personId),
  KEY paperId_idx (paperId),
  CONSTRAINT fk_paperId FOREIGN KEY (paperId) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_personId FOREIGN KEY (personId) REFERENCES person (person_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: paper
DROP TABLE IF EXISTS paper;
CREATE TABLE paper (
  paper_id int NOT NULL AUTO_INCREMENT,
  title longtext NOT NULL,
  pdf_file longblob NOT NULL,
  pdf_url varchar(255) DEFAULT NULL,
  abstract longtext NOT NULL,
  personID int NOT NULL,
  PRIMARY KEY (paper_id),
  KEY personID_idx (personID),
  CONSTRAINT personID FOREIGN KEY (personID) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: paper_person
DROP TABLE IF EXISTS paper_person;
CREATE TABLE paper_person (
  paper_id int NOT NULL,
  person_id int NOT NULL,
  PRIMARY KEY (paper_id, person_id),
  KEY fk_paper_person_person_id (person_id),
  CONSTRAINT fk_paper_person_paper_id FOREIGN KEY (paper_id) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_paper_person_person_id FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: paper_subject
DROP TABLE IF EXISTS paper_subject;
CREATE TABLE paper_subject (
  paper_id int NOT NULL,
  subject_id int NOT NULL,
  PRIMARY KEY (paper_id, subject_id),
  KEY fk_paper_subject_subject_id (subject_id),
  CONSTRAINT fk_paper_subject_paper_id FOREIGN KEY (paper_id) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_paper_subject_subject_id FOREIGN KEY (subject_id) REFERENCES subject (subject_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: person
DROP TABLE IF EXISTS person;
CREATE TABLE person (
  person_id int NOT NULL AUTO_INCREMENT,
  role varchar(255) NOT NULL,
  name varchar(255) NOT NULL,
  email varchar(255) NOT NULL,
  gender varchar(100) NOT NULL,
  phone varchar(255) NOT NULL,
  address varchar(255) DEFAULT NULL,
  age int DEFAULT NULL,
  photo_url varchar(255) NOT NULL,
  PRIMARY KEY (person_id),
  UNIQUE KEY email (email)
) ENGINE=InnoDB AUTO_INCREMENT=23952 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: person_subject
DROP TABLE IF EXISTS person_subject;
CREATE TABLE person_subject (
  person_id int NOT NULL,
  subject_id int NOT NULL,
  PRIMARY KEY (person_id, subject_id),
  KEY fk_person_subject_subject_id (subject_id),
  CONSTRAINT fk_person_subject_person_id FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_person_subject_subject_id FOREIGN KEY (subject_id) REFERENCES subject (subject_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: private
DROP TABLE IF EXISTS private;
CREATE TABLE private (
  personid int NOT NULL,
  paperid int NOT NULL,
  PRIMARY KEY (personid, paperid),
  KEY fk_private_paper_id (paperid),
  CONSTRAINT fk_private_paper_id FOREIGN KEY (paperid) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_private_person_id FOREIGN KEY (personid) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: public
DROP TABLE IF EXISTS public;
CREATE TABLE public (
  personid int NOT NULL,
  paperid int NOT NULL,
  PRIMARY KEY (personid, paperid),
  KEY fk_public_paper_id (paperid),
  CONSTRAINT fk_public_paper_id FOREIGN KEY (paperid) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_public_person_id FOREIGN KEY (personid) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: request
DROP TABLE IF EXISTS request;
CREATE TABLE request (
  request_id int NOT NULL AUTO_INCREMENT,
  sender_person_id int NOT NULL,
  receiver_person_id int NOT NULL,
  paper_id int NOT NULL,
  message text,
  status enum('pending','accepted','rejected') DEFAULT 'pending',
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (request_id),
  KEY sender_person_id (sender_person_id),
  KEY receiver_person_id (receiver_person_id),
  KEY paper_id (paper_id),
  CONSTRAINT request_ibfk_1 FOREIGN KEY (sender_person_id) REFERENCES person (person_id),
  CONSTRAINT request_ibfk_2 FOREIGN KEY (receiver_person_id) REFERENCES person (person_id),
  CONSTRAINT request_ibfk_3 FOREIGN KEY (paper_id) REFERENCES paper (paper_id)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: research
DROP TABLE IF EXISTS research;
CREATE TABLE research (
  personid int NOT NULL,
  paperid int NOT NULL,
  pub_date date NOT NULL,
  KEY paper_ID_idx (paperid),
  KEY person_ID_idx (personid),
  CONSTRAINT paper_ID FOREIGN KEY (paperid) REFERENCES paper (paper_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT person_ID FOREIGN KEY (personid) REFERENCES person (person_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: subject
DROP TABLE IF EXISTS subject;
CREATE TABLE subject (
  subject_id int NOT NULL AUTO_INCREMENT,
  subjectname varchar(255) NOT NULL,
  PRIMARY KEY (subject_id)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: conferences
DROP TABLE IF EXISTS conferences;
CREATE TABLE conferences (
  conference_id int(11) NOT NULL,
  title varchar(255) NOT NULL,
  event_desc varchar(255) NOT NULL,
  location varchar(255) NOT NULL,
  organizer varchar(255) NOT NULL,
  position varchar(255) NOT NULL,
  email varchar(255) NOT NULL,
  deadline date NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET foreign_key_checks = 1;

