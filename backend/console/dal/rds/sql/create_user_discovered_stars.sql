DROP TABLE IF EXISTS `user_discovered_stars`;

CREATE TABLE `user_discovered_stars`
(
    `id`           bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Discovery ID (Primary Key)',
    `user_id`      bigint(20) unsigned NOT NULL COMMENT 'User ID',
    `hip_id`       bigint(20) unsigned NOT NULL COMMENT 'Star HIP ID',
    `created_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_hip` (`user_id`, `hip_id`) COMMENT 'Prevents duplicate star discoveries for the same user'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='STARS discovered by users information table';

CREATE INDEX idx_user_ctime ON user_discovered_stars (user_id, created_at);