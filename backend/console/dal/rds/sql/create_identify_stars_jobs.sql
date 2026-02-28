DROP TABLE IF EXISTS `identify_stars_jobs`;

CREATE TABLE `identify_stars_jobs`
(
    `id`           bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Job ID (Primary Key)',
    `user_id`      bigint(20) unsigned NOT NULL COMMENT 'User id',
    `created_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    `updated_at`   timestamp           NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    `image_key`    varchar(512)        NOT NULL COMMENT 'Image storage key',
    `status`       varchar(16)         NOT NULL COMMENT 'Job status',
    `astronomy_net_job_id` bigint(20) unsigned DEFAULT NULL COMMENT 'astronomy.net job id',
    `result`       JSON                DEFAULT NULL COMMENT 'Job result',
    `is_deleted`   tinyint(1)          NOT NULL DEFAULT 0 COMMENT 'Soft delete flag (0: Active, 1: Deleted)',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='Identify stars jobs information table';

CREATE INDEX idx_user_stat_ctime ON identify_stars_jobs (user_id, status, created_at);
