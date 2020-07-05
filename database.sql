-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 05, 2020 at 01:50 PM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fp`
--

DELIMITER $$
--
-- Functions
--
CREATE DEFINER=`root`@`localhost` FUNCTION `idAutora` (`ime` VARCHAR(30)) RETURNS INT(11) BEGIN
 DECLARE id int;
  Select id_autora into id
  FROM (select * from autor) t
  where ime_autora=ime;
  RETURN id;
END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `imeAutora` (`id` INT) RETURNS VARCHAR(20) CHARSET utf8 COLLATE utf8_unicode_ci BEGIN
  DECLARE ime VARCHAR(20);
  SELECT ime_autora INTO ime
  FROM autor
  WHERE id_autora=id;
  RETURN ime;
END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `maxIdPesme` () RETURNS INT(11) BEGIN
 DECLARE maxId int;
  SELECT MAX(IFNULL(id_muzike,0)) into maxId from (SELECT * from pesma) as t;
  RETURN maxId;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `autor`
--

CREATE TABLE `autor` (
  `id_autora` int(11) NOT NULL,
  `ime_autora` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `autor`
--

INSERT INTO `autor` (`id_autora`, `ime_autora`) VALUES
(1, 'Frank Sinatra'),
(2, 'Queen'),
(3, 'Bon jovi'),
(4, 'Charlie puth'),
(5, 'Wiz khalifa'),
(6, 'Djordje balasevic'),
(7, 'Zdravko colic');

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE `favorites` (
  `datum` date NOT NULL,
  `id_muzike` int(11) NOT NULL,
  `id_osobe` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `favorites`
--

INSERT INTO `favorites` (`datum`, `id_muzike`, `id_osobe`) VALUES
('2020-05-27', 7, 2),
('2020-05-27', 3, 2),
('2020-05-27', 0, 2),
('2020-05-27', 0, 3),
('2020-06-04', 0, 0),
('2020-06-04', 5, 0),
('2020-06-04', 4, 0);

-- --------------------------------------------------------

--
-- Table structure for table `korisnik`
--

CREATE TABLE `korisnik` (
  `id_osobe` int(11) NOT NULL,
  `status` enum('korisnik','admin') NOT NULL DEFAULT 'korisnik',
  `username` text NOT NULL,
  `password` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `korisnik`
--

INSERT INTO `korisnik` (`id_osobe`, `status`, `username`, `password`) VALUES
(0, 'admin', 'darkonrt14818', 'dkei2502'),
(1, 'korisnik', 'viser', 'viser123'),
(2, 'korisnik', 'nikola123', 'nikola321'),
(3, 'korisnik', 'markopantelic', 'marko321');

-- --------------------------------------------------------

--
-- Table structure for table `muzika`
--

CREATE TABLE `muzika` (
  `id_muzike` int(11) NOT NULL,
  `id_autora` int(11) NOT NULL,
  `datum_azuriranja` date DEFAULT NULL,
  `link` text,
  `feat` int(10) UNSIGNED DEFAULT NULL,
  `broj_slusanja` int(10) UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `muzika`
--

INSERT INTO `muzika` (`id_muzike`, `id_autora`, `datum_azuriranja`, `link`, `feat`, `broj_slusanja`) VALUES
(0, 1, '2020-05-26', 'Thats_Life.wav', 0, 1),
(2, 1, '2020-05-26', 'ive_got_you.wav', 0, 8),
(3, 1, '2020-05-26', 'fly_me_to_the_moon.wav', 0, 8),
(4, 2, '2020-05-26', 'bohemian_rhapsody.wav', 0, 8),
(5, 3, '2020-05-26', 'livin\'_on_a_prayer.wav', 0, 11),
(6, 4, '2020-05-27', 'see_you_again.wav', 5, 9),
(7, 6, '2020-05-27', 'pa_dobro_gde_si_ti.wav', NULL, 7),
(8, 7, '2020-05-27', 'malo_pojacaj_radio.wav', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `pesma`
--

CREATE TABLE `pesma` (
  `id_muzike` int(11) NOT NULL,
  `naziv` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pesma`
--

INSERT INTO `pesma` (`id_muzike`, `naziv`) VALUES
(0, 'That\'s Life'),
(2, 'I\'ve Got You Under My Skin'),
(3, 'fly me to the moon'),
(4, 'bohemian rhapsody'),
(5, 'livin\' on a prayer'),
(6, 'see you again'),
(7, 'pa dobro gde si ti'),
(8, 'malo pojacaj radio'),
(9, 'malo pojacaj radio');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `autor`
--
ALTER TABLE `autor`
  ADD PRIMARY KEY (`id_autora`);

--
-- Indexes for table `favorites`
--
ALTER TABLE `favorites`
  ADD KEY `id_muzike` (`id_muzike`),
  ADD KEY `id_osobe` (`id_osobe`);

--
-- Indexes for table `korisnik`
--
ALTER TABLE `korisnik`
  ADD PRIMARY KEY (`id_osobe`);

--
-- Indexes for table `muzika`
--
ALTER TABLE `muzika`
  ADD PRIMARY KEY (`id_muzike`,`id_autora`),
  ADD KEY `i3` (`id_muzike`),
  ADD KEY `i4` (`id_autora`);

--
-- Indexes for table `pesma`
--
ALTER TABLE `pesma`
  ADD PRIMARY KEY (`id_muzike`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`id_muzike`) REFERENCES `muzika` (`id_muzike`),
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`id_osobe`) REFERENCES `korisnik` (`id_osobe`);

--
-- Constraints for table `muzika`
--
ALTER TABLE `muzika`
  ADD CONSTRAINT `i3` FOREIGN KEY (`id_muzike`) REFERENCES `pesma` (`id_muzike`),
  ADD CONSTRAINT `i4` FOREIGN KEY (`id_autora`) REFERENCES `autor` (`id_autora`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
