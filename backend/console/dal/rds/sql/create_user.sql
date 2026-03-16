DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`
(
    `id`           bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'User ID (Primary Key)',
    `username`     varchar(64)         NOT NULL COMMENT 'Unique username for login',
    `password`     varchar(128)        NOT NULL COMMENT 'Hashed password',
    `email`        varchar(128)        NOT NULL COMMENT 'Email address',
    `avatar_url`   varchar(512)        DEFAULT '' COMMENT 'User avatar URL',
    `created_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    `is_deleted`   tinyint(1)          NOT NULL DEFAULT 0 COMMENT 'Soft delete flag (0: Active, 1: Deleted)',
    `last_gps`     json                DEFAULT NULL COMMENT 'User last GPS location',
    `profile`      json                DEFAULT NULL COMMENT 'User profile in JSON format',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Core user information table';