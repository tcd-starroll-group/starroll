DROP TABLE IF EXISTS `observation_site`;

CREATE TABLE `observation_site`
(
    `id`                     bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Observation site ID',
    `name`                   varchar(128)        NOT NULL COMMENT 'Observation site name',
    `latitude`               double              NOT NULL COMMENT 'Site latitude',
    `longitude`              double              NOT NULL COMMENT 'Site longitude',
    `light_pollution_score`  double              NOT NULL DEFAULT 50 COMMENT 'Lower score means darker sky',
    `description`            varchar(512)        DEFAULT '' COMMENT 'Site description',
    `is_active`              tinyint(1)          NOT NULL DEFAULT 1 COMMENT 'Active flag',
    `created_at`             timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at`             timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',

    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Observation sites used by recommendation emails';

INSERT INTO `observation_site` (`name`, `latitude`, `longitude`, `light_pollution_score`, `description`, `is_active`)
VALUES
    ('West Lake Viewing Point', 30.2431, 120.1500, 45, 'Urban site with easy access and open sky areas', 1),
    ('Fuyang Mountain Deck', 30.0488, 119.9607, 22, 'Suburban mountain area with lower light pollution', 1),
    ('Qiandao Lake Shore', 29.6088, 119.0472, 18, 'Lakeside site with dark sky and broad horizon', 1);
